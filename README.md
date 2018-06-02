# What is this

This is a factory for Alexa skills.
Read [this article]() to get some context.


# Pipeline

`.gitlab-ci.yml` defines the delivery pipeline.
In that file, update the YAML-defined [global variables](https://docs.gitlab.com/ee/ci/yaml/README.html#variables):
- `SERVERLESS_SERVICE_NAME` for serverless to keep track of this service
- `QA_INVOCATION` and `PROD_INVOCATION` for the Alexa skill
- `AWS_REGION`, the AWS region where the skill is to be deployed

Configure the following [project-level secret variables](https://docs.gitlab.com/ee/ci/variables/#secret-variables):
- `DARK_SKY_SECRET_KEY`, the [Dark Sky API key](https://darksky.net/dev)
- `GPS_POSITIONS`, GPS position of the locations you want the weather for, in a JSON document such as:
```
{
    "home": "29.8,-95.5",
    "volley-ball court": "29.9,-95.6"
}
```
# CI image

The `Dockerfile` for the debian-ci image is provided in the [debian-ci](debian-ci) directory.
It is rather bloated, as it is used for more projects than just this skills factory.

# Runner

The runner tasked with the deployment has access to the AWS and ASK secrets.
Initialize AWS CLI with
```
aws configure
```
and ASK with
```
ask init --no-browser
```

If more than one person contributes code, restrict the runners for example with
[tags](https://docs.gitlab.com/ee/ci/yaml/#tags)

Their `config.toml` looks like this:

```
[[runners]]
  name = "docker-runner"
  url = "https://<FQDN_OF_OUR_GITLAB_SERVER>"
  executor = "docker"
  environment = ["GODEBUG=netdns=cgo"]
  [runners.docker]
    tls_verify = false
    image = "docker:latest"
    privileged = false
    disable_cache = false
    volumes = ["/var/run/docker.sock:/var/run/docker.sock", "/cache", "/srv/aws/aws:/home/user/.aws", "/srv/aws/ask:/home/user/.ask" ]
    links = ["<NAME_OF_GITLAB_CONTAINER>:<FQDN_OF_OUR_GITLAB_SERVER>"]
    shm_size = 0
  [runners.cache]
```

Our Gitlab server does not have a publicly signed certificate, so we have to ask `go` to trust the certificates that the containerized OS trusts (see the debian-ci Dockerfile).
That's for the
```
environment = ["GODEBUG=netdns=cgo"]
```

# Troubleshooting

```npm run logs-tail-qa``` (resp. ```npm run logs-tail-prod```) tails the log stream coming from the qa (resp. prod) Lambda function.

```node_modules/.bin/sls remove``` removes the stack, in case you had the
bad idea for example to remove Lambda functions manually
(```"Function not found"``` error message).
Trigger the pipeline again to put everything back.

## Testing the Lambda function inside AWS

If everything else fails

## No CloudWatch stream

If 
```
npm run logs-tail-qa
```
or its production counterpart complains of lack of CloudWatch stream, 
make sure that there is no other skill defined with the same invocation.

## Unexplained 

Different symptom, probably same root cause as previous issue.