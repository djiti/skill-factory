"""
Function that AWS Lambda will be looking for
"""
# v1.0.1

import os
import time
import json
import urllib.request
import codecs
import gzip

# --------------- Helpers that build all of the responses ----------------------

with open('gps_positions.json') as gps_positions_file:
    GPS_POSITIONS = json.load(gps_positions_file)
TIMEZONE = 'America/Chicago'
os.environ['TZ'] = TIMEZONE
time.tzset()

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    """ Boiler plate build_speechlet_response from AWS
    """
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    """ Boiler plate build_response from AWS
    """
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

def get_dark_sky_secret():
    """ Gets the Dark Sky API key from wherever it can
    """
    dark_sky_secret_key = ""
    try:
        import boto3
        from base64 import b64decode
        encrypted = os.environ['DARK_SKY_SECRET_KEY']
        dark_sky_secret_key = boto3\
                              .client('kms')\
                              .decrypt(CiphertextBlob=b64decode(encrypted))['Plaintext']\
                              .decode('utf-8')
    except ImportError:
        dark_sky_secret_key = os.getenv('DARK_SKY_SECRET_KEY')
        if dark_sky_secret_key is None:
            with open('secret_dark_sky') as data_file:
                dark_sky_secret_key = data_file.readline().rstrip()
    return dark_sky_secret_key


DARK_SKY_SECRET = get_dark_sky_secret()

def get_full_forecast(gps_position):
    """ Returns the weather forecast as retrieved from the Dark Sky API
    """
    params = urllib.parse.urlencode({'units': 'us', 'exclude': 'flags,hourly'})
    url = 'https://api.darksky.net/forecast/{KEY}/{POSITION}?{params}'.\
          format(KEY=DARK_SKY_SECRET, POSITION=gps_position, params=params)

    req = urllib.request.Request(url)
    req.add_header('Accept-Encoding', 'gzip')
    response = urllib.request.urlopen(req)

    reader = codecs.getreader('utf-8')
    weather = json.load(reader(gzip.GzipFile(fileobj=response)))
    return weather


def get_weather(full_forecast):
    """ Gathers all components of forecast
    """
    forecast = '{minutely} {temperature} {alerts}'
    forecast_string = forecast.format(minutely=full_forecast['minutely']['summary'],
                                      temperature=get_temperature(full_forecast),
                                      alerts=get_alert(full_forecast))
    return forecast_string


def degrees_f_to_c(farenheit):
    """ Quick and dirty conversion from Farenheit to Celsius
    TODO: This is something the Dark Sky API can do for us
    """
    return round((farenheit - 32) * 100 / 180)


def unix_to_time(unix, am_pm=True):
    """
    Converts Unix time to string
    """
    if am_pm:
        return time.strftime("%I %p", time.localtime(unix)).lstrip("0")
    return time.strftime("%H", time.localtime(unix))


def fuzzy_time(hour):
    """ Converts an hour of the day into easy-to-remember plain English
    """
    if hour < 6:
        return "early morning"
    elif hour < 11:
        return "this morning"
    elif hour < 14:
        return "mid day"
    elif hour < 18:
        return "this afternoon"
    elif hour < 21:
        return "this evening"
    return "tonight"


def get_temperature(full_forecast):
    """ Extracts temperature trend from the forecast
    """
    today_forecast = full_forecast['daily']['data'][0]
    forecast = (
        'Current temperature is {current_temp} degrees Celsius, '
        'with a low of {low_temp} {low_temp_time} '
        'and a high of {high_temp} {high_temp_time}. ')\
        .format(current_temp=degrees_f_to_c(full_forecast['currently']['temperature']),
                low_temp=degrees_f_to_c(today_forecast['temperatureMin']),
                low_temp_time=fuzzy_time(int(unix_to_time(today_forecast['temperatureMinTime'],
                                                          False))),
                high_temp=degrees_f_to_c(today_forecast['temperatureHigh']),
                high_temp_time=fuzzy_time(int(unix_to_time(today_forecast['temperatureHighTime'],
                                                           False))))
    return forecast


def get_alert(full_forecast):
    """ Extracts alerts from the forecast
    """
    if not full_forecast.get("alerts"):
        return ""
    alerts = list(map(lambda alert: alert["title"], full_forecast.get("alerts")))
    forecast_start = 'The area is under {num_alert} alert{alert_plural}: '.\
                   format(num_alert=len(alerts),
                          alert_plural="s" if len(alerts) > 1 else "")
    if len(alerts) == 1:
        return forecast_start + alerts[0] + '. '
    if len(alerts) == 2:
        return forecast_start + ' and '.join(alerts[-2:]) + '. '
    forecast_end_1 = ', '.join(alerts[0:-2]) + ', '
    forecast_end_2 = ' and '.join(alerts[-2:])
    return forecast_start + forecast_end_1 + forecast_end_2 + '. '


def get_welcome_response():
    """ Entrypoint to welcome
    """
    card_title = "Welcome"

    reprompt_text = ""
    should_end_session = True

    location = "home"
    full_forecast = get_full_forecast(GPS_POSITIONS[location])
    weather = 'At {}, {}'.format(location, get_weather(full_forecast))

    session_attributes = {"forecast": full_forecast}

    return build_response(session_attributes, build_speechlet_response(
        card_title, weather, reprompt_text, should_end_session))

# --------------- Functions that control the skill's behavior ------------------


def get_weather_in_session(intent, session):
    """ When asked for the weather
    """
    card_title = intent['name']
    session_attributes = session.get('attributes', {})
    reprompt_text = ""
    should_end_session = False
    weather = ""
    full_forecast = {}
    if 'Location' in intent['slots']:
        location = intent['slots']['Location']['value'].lower()
        if location in GPS_POSITIONS.keys():
            full_forecast = session_attributes.get('forecast',
                                                   get_full_forecast(GPS_POSITIONS[location]))
            weather = 'At {}, {}'.format(location, get_weather(full_forecast))
        else:
            weather = 'Oops, somebody forgot to tell me where {} is located. '.format(location)
    else:
        weather = 'I do not know the location you asked about. '
    session_attributes['forecast'] = full_forecast
    return build_response(session_attributes, build_speechlet_response(
        card_title, weather, reprompt_text, should_end_session))

def get_help_in_session():
    """ When asked for help
    """
    card_title = 'getHelp'
    session_attributes = {}
    reprompt_text = ""
    should_end_session = False
    positions = sorted(GPS_POSITIONS.keys())
    all_positions = ', '.join(positions[0:len(positions) - 1])
    all_positions = '{}, and {}'.format(all_positions, positions[-1])
    text = 'You can ask me for the weather in {}. '.format(all_positions)
    return build_response(session_attributes, build_speechlet_response(
        card_title, text, reprompt_text, should_end_session))

# --------------- Events ------------------


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    if intent_name == 'getWeatherIntent':
        return get_weather_in_session(intent, session)
    elif intent_name == 'getHelpIntent':
        return get_help_in_session()
    else:
        raise ValueError('Invalid intent')


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])

# --------------- Main handler ------------------


def lambda_handler(event, _context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    # Now assuming event['request']['type'] == "SessionEndedRequest":
    return on_session_ended(event['request'], event['session'])
