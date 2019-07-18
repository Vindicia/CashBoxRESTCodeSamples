#!/usr/bin/env python

# Add a subscription to an account using the account id and payment method id 
# and billing plan id and product id

import json 
import pycurl
import sys 
import base64
import StringIO
import random 
import string

# Set the Authentication Credentials 
login = "USERNAME:PASSWORD"
login64 = base64.b64encode(b'' + login)

# Billing Plan Id 
bp_id = "MONTHLY"

# Product Id 
prod_id = "GENERIC"

# Campaign Id (If applicable) 
campaignCode = "10POFF"

# Function used to create a random guid 
def id_generator(size=16, chars=string.ascii_letters + string.digits):
   return ''.join(random.choice(chars) for _ in range(size))  
   
# Send a random integer between 0 and 25 and get a random first name 
def fetchFirstName(fn):

    firstNames = {
        0: "Adam",
        1: "Billy",
        2: "Carl",
        3: "Donovan",
        4: "Edward",
        5: "Frank",
        6: "George",
        7: "Harry",
        8: "Ivan",
        9: "Jerome",
       10: "Kirsten",
       11: "Laura",
       12: "Mary",
       13: "Nancy",
       14: "Oprah",
       15: "Patty",
       16: "Queen",
       17: "Rhonda",
       18: "Stevie",
       19: "Terri",
       20: "Uma",
       21: "Veronica",
       22: "Wendy",
       23: "Xavier",
       24: "Yvette",
       25: "Zoro",
    }
    return firstNames.get(fn, "Liam")
    
# Send a random integer between 0 and 25 and get a random last name 
def fetchLastName(ln):

    lastNames = {
        0: "Apple",
        1: "Broughton",
        2: "Cleveland",
        3: "Drake",
        4: "Evanston",
        5: "Figgirotto",
        6: "Gleason",
        7: "Hamilton",
        8: "Inskip",
        9: "Jenkins",
       10: "Killarney",
       11: "Longhorn",
       12: "Maxwell",
       13: "Norquist",
       14: "Olsteen",
       15: "Patton",
       16: "Quigley",
       17: "Rhoads",
       18: "Stevens",
       19: "Taylor",
       20: "United",
       21: "Various",
       22: "Whatever",
       23: "Xusay",
       24: "Yesterday",
       25: "Zildjian",
    }
    return lastNames.get(ln, "Maxwell")
    
# Send a random integer between 0 and 25 and get a random address line 1 
def fetchAddr1(addr1):

    addr1s = {
        0: "Apple Street",
        1: "Berry Lane",
        2: "Westfield Drive",
        3: "Devonshire Drive",
        4: "Lakeshore Drive",
        5: "Crazy Way",
        6: "High Street",
        7: "Scottsdale",
        8: "Rush Ave",
        9: "Main Street",
       10: "Second Street",
       11: "Lake Shore Drive",
       12: "Centennial Drive",
       13: "Cherry Hills",
       14: "Kenwood Road",
       15: "Strawberry Fields",
       16: "Sultan Way",
       17: "County Road 47",
       18: "William Street",
       19: "Sangamon Ave",
       20: "Southwood Drive",
       21: "Robison Lane",
       22: "Spartcus Lane",
       23: "Fieldhouse Drive",
       24: "Sheridan Roap",
       25: "Duncan Street",
    }
    return addr1s.get(addr1, "Maxwell Street")
    
# Send a random integer between 0 and 25 and get a random city / state / postal code 
# Using : as a delimiter 
def fetchCityStateZip(csz):

    cityStateZip = {
        0: "Champaign:IL:61820",
        1: "Grayslake:IL:60030",
        2: "Pleasant Prairie:WI:53158",
        3: "Kenosha:WI:53158",
        4: "New York:NY:10278",
        5: "Bangor:PA:18013",
        6: "Pen Argyl:PA:18072",
        7: "Holland:MI:49424",
        8: "Indianapolis:IN:46208",
        9: "Cleveland:OH:44127",
       10: "Nashville:TN:37209",
       11: "St. Louis:MO:63103",
       12: "Addison:TX:75001",
       13: "Dallas:TX:75243",
       14: "Austin:TX:78703",
       15: "San Francisco:CA:94122",
       16: "Redwood City:CA:94061",
       17: "Palo Alto:CA:94304",
       18: "Berkeley:CA:94704",
       19: "Portland:OR:97209",
       20: "Seattle:WA:98121",
       21: "Bellevue:WA:98006",
       22: "La Push:WA:98350",
       23: "New Orleans:LA:70113",
       24: "Bozeman:MT:59715",
       25: "Casper:WY:82601",
    }
    return cityStateZip.get(csz, "Champaign:IL:61820")

# Generate a *probably* unique id 
guid = id_generator()

# Set the subscription object ids
account_id = "Account_" + guid
payment_id = "CC_" + guid
subscription_id = "Subscription_" + guid
item_id = "Item_" + guid

# Get some random account name and address attributes 
fn = random.randint(0,25)
ln = random.randint(0,25)
ad = random.randint(0,25)
csz = random.randint(0,25)
houseNumber = random.randint(1,25000)
streetName = fetchAddr1(ad)
firstName = fetchFirstName(fn)
lastName = fetchLastName(ln)
accountName = firstName + " " + lastName
addr1 = str(houseNumber) + " " + streetName

cszString = fetchCityStateZip(csz)
cityStateZipArray = cszString.split(":")
city = cityStateZipArray[0]
state = cityStateZipArray[1]
zip = cityStateZipArray[2]

# Set an amount if applicable 
amount = 2001 # Brain Tree - Soft Failure


jsonObj = {

    "id": "Subscription_" + guid,
    
    "account": {
       "id": account_id,
        "name": accountName,   
        "shipping_address": {
               "name": accountName,
               "line1": addr1,
               "city": city,
               "district": state,
               "postal_code": zip,
               "country": "US"
            },
    },
    "billing_plan": {
       "id": bp_id
    },
    "payment_method": {
       "id": payment_id,
       "type": "CreditCard",
          "credit_card": {
               "account": "4113900000000007",
               "expiration_date": "202003"
            },
            "account_holder": accountName,
            "billing_address": {
               "name": accountName,
               "line1": addr1,
               "city": city,
               "district": state,
               "postal_code": zip,
               "country": "US"
            },
            "customer_description": "Credit Card",
            "active": 1
       },
    "currency": "USD",
    "description": subscription_id,
    "items": [
       {
          "id": item_id,
          #"amount": amount, 
          #"currency": "USD",
          "product": {
             "id": prod_id
          },
          #"campaign_code": campaignCode
       },
    ],
    "minimum_commitment": 0,
    "policy": {
       "ignore_cvn_policy": 1,
       "ignore_avs_policy": 1,
       "min_chargeback_probability": 99,
       "immediate_auth_failure_policy": "doNotSaveAutoBill",
       "validate_for_future_payment": 0
    }
 }

# Print out the payload you are going to send
payload = json.dumps(jsonObj)
print "REQUEST JSON" 
print payload

# Set the target 
url = "https://api.prodtest.vindicia.com/"
parameters = "subscriptions?dry_run=0"
target = url + parameters
print "Target-> ", target


# Prepare to make the request
response = StringIO.StringIO()
c = pycurl.Curl()
c.setopt(c.URL, target)
c.setopt(c.POST, 1)
c.setopt(c.POSTFIELDS, payload)
c.setopt(c.HTTPHEADER, ['Authorization: Basic ' + login64, 'Content-Type: application/json'])
c.setopt(c.VERBOSE, 1)

# Execute the REST API 
c.perform()

# Close the Channel 
c.close()

# Print the response from the REST API call 
print "RESPONSE JSON" 
print response.getvalue()

# Close the response channel 
response.close()