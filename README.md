# Deployment

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
or its production counterpart complain of lack of CloudWatch stream, 
make sure that there is no other skill defined with the same invocation.

## Unexplained 

Different symptom, probably same root cause as previous issue.