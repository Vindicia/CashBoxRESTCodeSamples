import json
import logging
import os
import hmacValidation as auth

# Set up basic logging levels for CloudWatch
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
log = logging.getLogger()
log.setLevel(logging.INFO)

# Grab the PUSH HMAC key from a lambda environment variable
hmac_key = os.environ['hmac_key']

def lambda_handler(event, context):
        
    # Perform HMAC Validation
    log.info('VALIDATING HMAC')
    webHook = event['headers']['X-Webhook-Signature']
    if not auth.Authoriser(webHook, hmac_key).validate(event['body']):
        log.info('HMAC Validation Error')
        log.warning('HMAC CHECK FAILED')
        raise Exception("403 - Not Authorised")
        return 403
    
    # If we get here we know the HMAC was valid
    log.info('HMAC IS VALID')
    
    # Log the JSON for the body and the http headers 
    if isinstance(event['body'], (str, bytes)):
        event['body'] = json.loads(event['body'].strip('"'))
        # Output pretty JSON into the LOG file for easier viewing
        log.info('NOTIFICATION PAYLOAD: %s', json.dumps(event['body']))
        log.info('HTTP HEADERS: %s', json.dumps( event['headers']))
    else: 
        log.warning('ERROR PROCESSING EVENT BODY')

    # Some Basic info from notification header 
    class_name = event['body']['header']['class_name']
    event_name = event['body']['header']['event_name']
    message_id = event['body']['header']['message_id']

    # Some Basic info from entitlement notification  
    entitlement_id = event['body']['content']['merchantEntitlementId'][0]
    account_id = event['body']['content']['merchantAccountId']

    # Log Some basic info
    log.info('ACCOUNT: %s', account_id)
    log.info('CLASS_NAME: %s', class_name)
    log.info('EVENT_NAME: %s', event_name)
    log.info('ENTITLEMENT_ID: %s', entitlement_id)
    log.info('MESSAGE_ID: %s', message_id)