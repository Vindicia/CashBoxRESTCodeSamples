#############################################################################################################
##  VINDICIA SUBSCRIBE OBJECT MIGRATION UTILITY                                                            ##
##   AUTHOR: Liam Maxwell                                                                                  ##
##     DATE: 02/12/2020                                                                                    ##
##  VERSION: 1.0                                                                                           ##
##  PURPOSE: To migrate Subscribe objects from one environment to another.  Currently used for Product     ##
##  Catalog Migration move Season Sets, Rate Plans, Billing Plans, Products and Canpaigns from a source    ##
##  to a destination.  Only tokens are not supported and have to be created manually first.                ##
##                                                                                                         ##
##  Utility settings are located at the bottom of this program                                             ##
#############################################################################################################
import pycurl
import StringIO
import base64
import sys
import json

# This function is used to remove the VIDs off of the RESPONSE JSON 
# We then are able to submit the JSON as a REQUEST to create the objects 
def remove_values(obj, key):
    """Pull all values of specified key from nested JSON."""

    def extract(obj, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, key)
                elif k == key:
                    del obj[k]
        elif isinstance(obj, list):
            for item in obj:
                extract(item, key)
        return obj

    results = extract(obj, key)
    return results

# This function is used to search the RESPONSE JSON for Tokens
def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []
    tokens = []
    token = ""

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                if 'token' in item:
                    token = json.dumps(item['token']['id'])
                    if token not in tokens: 
                        tokens.append(token)

                extract(item, arr, key)

        return tokens

    results = extract(obj, arr, key)
    return results

def validateEndPoint(ep):
	endPoints = {
		"accounts": True, 
		"billing_plans": True, 
		"entitlements": True, 
		"events": True, 
		"invoices": True, 
		"payment_methods": True, 
		"products": True, 
		"rate_plans": True, 
		"refunds": True, 
		"subscriptions": True, 
		"transactions": True, 
		"txsb": True, 
		"campaigns": True, 
		"credits": True, 
        "payments": True, 
        "chargebacks": True, 
        "tokens": True, 
        "season_sets": True,
	}
	return endPoints.get(ep, False)

def migrate_objects(objType, source, destination, sourceURL, destinationURL): 
    print "------------------------------------------------------------------------"

    if (validateEndPoint(objType) != True):
	print "\nInvalid End Point: ", objType
	exit(0)

    # Only migrate active option
    onlyMigrateActiveObjects = True

    if onlyMigrateActiveObjects == True: 
        print "Migrating ACTIVE " + objType
    else: 
        print "Migrating ACTIVE and INACTIVE " + objType

    # Set how many Campaigns to fetch at a time from the command line parameters
    command1 = "/" + objType + "?limit=1" 
    command2 = "/" + objType + "/"
        
    # Initial some of the variables needed to do the fetch and db load 
    fetchComplete = False
    totalNumberOfObjects = 0
        
    while fetchComplete != True:
        target1 = sourceURL + command1 

        # Get the first batch 
        response1 = StringIO.StringIO()
        c1 = pycurl.Curl() 
        c1.setopt(c1.URL, target1)
        c1.setopt(c1.WRITEFUNCTION, response1.write)
        c1.setopt(c1.HTTPHEADER, ['Authorization: Basic ' + source, 'Content-Type: application/json'])

        # Turn on to see more of the action behind the scenes 
        c1.setopt(c1.VERBOSE, False)

        # Execute the REST API 
        c1.perform()

        # Close the Channel 
        c1.close()

        # Parse the response from the REST API call 
        event =  json.loads(response1.getvalue())

        if 'next' in event: 
            command1 = event['next']
            totalNumberOfObjectsFetched = 0
        else: 
            fetchComplete = True
        
        if 'total_count' in event:
            objectCount = event['total_count']
            totalNumberOfObjectsFetched += len(event['data'])
        
            x = 0
            objectCounter = 1
            while objectCounter <= totalNumberOfObjectsFetched:
                objectId = event['data'][x]['id']

                # Need to manage Campaigns differently because status is "state"
                # Need to manage Rate Plans and Season Sets differently because there is not a status 
                if objType == "campaigns": 
                    objectStatus = event['data'][x]['state']
                elif objType == "rate_plans" or objType == "season_sets": 
                    objectStatus = "Active"
                else: 
                    objectStatus = event['data'][x]['status']

                # Check if the option to only cache active is set
                if (onlyMigrateActiveObjects == True and objectStatus == "Active") or (onlyMigrateActiveObjects == False):

                    # Remove the Vids from the JSON 
                    event['data'][x] = remove_values(event['data'][x], "vid")

                    # For Billing Plans remove the used_on_subscriptions attribute for the destination
                    if objType == "billing_plans":
                        del event['data'][x]['used_on_subscriptions']
                    
                    # For products remove the bundles and inherited entitlements 
                    if objType == "products": 
                        if 'bundled_products' in event['data'][x]:
                            print "Removing Product Bundle from " + objectId
                            del event['data'][x]['bundled_products']
                            del event['data'][x]['inherited_entitlements']

                    print "Migrating " + objType + ":" + objectId
                    target2 = destinationURL + command2 
                    payload2 = json.dumps(event['data'][x])

                    # Prepare to make the request
                    response2 = StringIO.StringIO()
                    c2 = pycurl.Curl()
                    c2.setopt(c2.URL, target2)
                    c2.setopt(c2.POST, 1)
                    c2.setopt(c2.POSTFIELDS, payload2)
                    c2.setopt(c2.HTTPHEADER, ['Authorization: Basic ' + destination, 'Content-Type: application/json'])
                    c2.setopt(c2.VERBOSE, 0)
                    c2.setopt(c2.WRITEFUNCTION, response2.write)

                    # Execute the REST API 
                    c2.perform()
                    # Close the Channel 
                    c2.close()
                    
                    # Parse the response from the POST 
                    postResponse =  json.loads(response2.getvalue())


                    # Evaluate any errors 
                    if 'Error' in postResponse['object']: 
                        print "Error Migrating " + objType + ":" + objectId
                        print json.dumps(postResponse)
                    else:
                        print "Successfully Migrated " + objType + ":" + objectId

                # Increment the counters and flush the lists 
                totalNumberOfObjects += 1
                objectCounter += 1
                x += 1
                
        if totalNumberOfObjects == objectCount: 
            fetchComplete = True
            
    # Close the response channel 
    response1.close()

    print "Total Number of " + objType + " Processed: " +str(totalNumberOfObjects)
    return 200

def scan_for_tokens(source, sourceURL): 
    print "----------------------------TOKEN-SCAN-----------------------------------"
        
    # Set how many products to fetch at a time from the command line parameters
    command1 = '/products?limit=1' 
    command2 = '/products/'
        
    # Initial some of the variables needed to do the fetch and db load 
    foundTokens = False
    fetchComplete = False
    totalNumberOfProducts = 0
    numberOfTokens = 0
        
    while fetchComplete != True:
        target1 = sourceURL + command1 

        # Get the first batch of products
        response1 = StringIO.StringIO()
        c1 = pycurl.Curl() 
        c1.setopt(c1.URL, target1)
        c1.setopt(c1.WRITEFUNCTION, response1.write)
        c1.setopt(c1.HTTPHEADER, ['Authorization: Basic ' + source, 'Content-Type: application/json'])

        # Turn on to see more of the action behind the scenes 
        c1.setopt(c1.VERBOSE, False)

        # Execute the REST API 
        c1.perform()

        # Close the Channel 
        c1.close()

        # Parse the response from the REST API call 
        event =  json.loads(response1.getvalue())

        if 'next' in event: 
            command1 = event['next']
            numberOfProductsFetched = 0
        else: 
            fetchComplete = True
        
        if 'total_count' in event:
            productCount = event['total_count']
            numberOfProductsFetched += len(event['data'])
        
            x = 0
            productCounter = 1
            while productCounter <= numberOfProductsFetched:
                merchantProductId = event['data'][x]['id']

                
                tokenResult = extract_values(event['data'][x], "object")
                numberOfTokens = len(tokenResult)
                if numberOfTokens > 0: 
                    foundTokens = True
                    print "Found tokens in " + merchantProductId
                    print tokenResult

                # Increment the counters and flush the lists 
                totalNumberOfProducts += 1
                productCounter += 1
                x += 1
                
        if totalNumberOfProducts == productCount: 
            fetchComplete = True
            
    # Close the response channel 
    response1.close()

    print "Total Number of Products Scanned: " +str(totalNumberOfProducts)
    print "To continue create these tokens in the destination merchant and set the Token Override to True"
    if foundTokens == False: 
        return 200
    else: 
        return 400

#############################################################################################################
##  THIS IS WHERE ALL THE FUN HAPPENS #######################################################################
#############################################################################################################

# Set the source and destination credentials 
sourceLogin = "<username>:<password>"
destinationLogin = "<username>:<password>"

# Encode with base64 for REST 
source = base64.b64encode(b'' + sourceLogin)
destination = base64.b64encode(b'' + destinationLogin)

# Set the CashBox URL targets 
sourceURL = "https://api.prodtest.vindicia.com"
destinationURL = "https://api.prodtest.vindicia.com"

# The Token override should be False for the first run of this utility
# Only change it to true when you know your destination has the tokens
tokenOverride = False

# Set the default result to success it will be set to 400 if we find tokens
result = 200

if tokenOverride == False: 
    result = scan_for_tokens(source, sourceURL)

if result == 200 or tokenOverride == True: 
    result = migrate_objects("rate_plans", source, destination, sourceURL, destinationURL)
    result = migrate_objects("season_sets", source, destination, sourceURL, destinationURL)
    result = migrate_objects("billing_plans", source, destination, sourceURL, destinationURL)
    result = migrate_objects("products", source, destination, sourceURL, destinationURL)
    result = migrate_objects("campaigns", source, destination, sourceURL, destinationURL)