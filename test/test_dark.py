""" Unit tests for lambda_function
"""

import unittest
import json
import lambda_function


class Test(unittest.TestCase):

    def setUp(self):
        with open('test/intent_request_test.json', encoding='utf-8') as data_file:
            self.intent_request = json.load(data_file)['intent']
        with open('test/forecast_test.json', encoding='utf-8') as data_file:
            self.full_forecast = json.load(data_file)
        with open('test/forecast_with_alert.json', encoding='utf-8') as data_file:
            self.full_forecast_with_alert = json.load(data_file)

    def test_hello(self):
        response = lambda_function.get_welcome_response()
        self.assertIsInstance(response, dict)

    def test_get_weather_with_rain(self):
        response = lambda_function.get_weather(self.full_forecast)
        self.assertRegex(response,
                         "Breezy and partly cloudy for the hour.")

    def test_get_weather_with_rain_and_alert(self):
        response = lambda_function.get_weather(self.full_forecast_with_alert)
        self.assertRegex(response,
                         "The area is under 2 alerts: Hard Freeze Warning and Wind Chill Advisory.")

    def test_get_weather_in_session(self):
        response = lambda_function.get_weather_in_session(self.intent_request, {})
        self.assertGreater(len(response['response']['outputSpeech']['text']), 2)

    def test_get_help(self):
        response = lambda_function.get_help_in_session()
        self.assertIn("You can ask me for the weather in ",
                      response['response']['outputSpeech']['text'])

    def test_get_temperature(self):
        response = lambda_function.get_temperature(self.full_forecast)
        self.assertEqual(response, "Current temperature is 15 degrees Celsius, "
                                   "with a low of 10 tonight and a high of 26 mid day.")

    def test_get_alert_gives_alerts_when_there_is_1(self):
        response = lambda_function.get_alert({"alerts": [{"title": "Hard Freeze Warning"}]})
        self.assertEqual(response, "The area is under 1 alert: Hard Freeze Warning. ")

    def test_get_alert_gives_alerts_when_there_are_2(self):
        response = lambda_function.get_alert(self.full_forecast_with_alert)
        self.assertEqual(response, "The area is under 2 alerts: Hard Freeze Warning "
                                   "and Wind Chill Advisory. ")

    def test_get_alert_gives_alerts_when_there_are_3(self):
        response = lambda_function.get_alert({"alerts": [{"title": "Hard Freeze Warning"},
                                                         {"title": "Wind Chill Advisory"},
                                                         {"title": "Lazy Guillaume"}]})
        self.assertEqual(response, "The area is under 3 alerts: Hard Freeze Warning, "
                                   "Wind Chill Advisory and Lazy Guillaume. ")

    def test_get_alert_stays_silent_when_there_are_none(self):
        response = lambda_function.get_alert(self.full_forecast)
        self.assertEqual(response, "")

    def test_to_celsius(self):
        self.assertEqual(lambda_function.degrees_f_to_c(50), 10)
        self.assertEqual(lambda_function.degrees_f_to_c(70), 21)
        self.assertEqual(lambda_function.degrees_f_to_c(67.82), 20)

    def test_fuzzy_time(self):
        self.assertEqual(lambda_function.fuzzy_time(3), "early morning")
        self.assertEqual(lambda_function.fuzzy_time(7), "this morning")
        self.assertEqual(lambda_function.fuzzy_time(11), "mid day")
        self.assertEqual(lambda_function.fuzzy_time(15), "this afternoon")
        self.assertEqual(lambda_function.fuzzy_time(19), "this evening")
        self.assertEqual(lambda_function.fuzzy_time(23), "tonight")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
