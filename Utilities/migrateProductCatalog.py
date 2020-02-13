#############################################################################################################
##  VINDICIA SUBSCRIBE PRODUCT CATALOG MIGRATION UTILITY                                                   ##
##   AUTHOR: Liam Maxwell                                                                                  ##
##     DATE: 02/12/2020                                                                                    ##
##  VERSION: 1.0                                                                                           ##
##  PURPOSE: To migrate Season Sets, Rate Plans, Billing Plans, Products and Canpaigns from a source       ##
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

# Function to migrate the rate plans 
def migrate_rate_plans(source, destination, sourceURL, destinationURL): 
    print "------------------------------------------------------------------------"
    # Only migrate active option
    onlyMigrateActiveRatePlans = True

    if onlyMigrateActiveRatePlans == True: 
        print "Migrating ACTIVE ratePlans...."
    else: 
        print "Migrating ACTIVE and INACTIVE ratePlans...."
        
    # Set how many ratePlans to fetch at a time from the command line parameters
    command1 = '/rate_plans?limit=1' 
    command2 = '/rate_plans/'
    
    # Initial some of the variables needed to do the fetch and db load 
    fetchComplete = False
    totalNumberOfRatePlans = 0
    
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
            totalNumberOfRatePlansFetched = 0
        else: 
            fetchComplete = True
      
        if 'total_count' in event:
            ratePlanCount = event['total_count']
            totalNumberOfRatePlansFetched += len(event['data'])
      
            x = 0
            ratePlanCounter = 1
            while ratePlanCounter <= totalNumberOfRatePlansFetched:
                ratePlanId = event['data'][x]['id']
                ratePlanstatus = event['data'][x]['status']     

                # Check if the option to only cache active is set
                if (onlyMigrateActiveRatePlans == True and ratePlanstatus == "Active") or (onlyMigrateActiveRatePlans == False):
                    # Remove the Vids from the JSON 
                    event['data'][x] = remove_values(event['data'][x], "vid")
                
                    print "Migrating Rate Plan " + ratePlanId
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
                        print "Error Migrating Rate Plan " + ratePlanId
                        print postResponse
                    else:
                        print "Successfully Migrated Rate Plan " + ratePlanId

                # Increment the counters and flush the lists 
                totalNumberOfRatePlans += 1
                ratePlanCounter += 1
                x += 1
             
        if totalNumberOfRatePlans == ratePlanCount: 
            fetchComplete = True
         
    # Close the response channel 
    response1.close()
    print "Total Number of Rate Plans Processed: " +str(totalNumberOfRatePlans)
    return 200

def migrate_season_sets(source, destination, sourceURL, destinationURL): 
    print "------------------------------------------------------------------------"
    print "Migrating Season Sets...."
        
    # Set how many SeasonSets to fetch at a time from the command line parameters
    command1 = '/season_sets?limit=1' 
    command2 = '/season_sets/'
        
    # Initial some of the variables needed to do the fetch and db load 
    fetchComplete = False
    totalNumberOfSeasonSets = 0
        
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
            totalNumberOfSeasonSetsFetched = 0
        else: 
            fetchComplete = True
        
        if 'total_count' in event:
            seasonSetCount = event['total_count']
            totalNumberOfSeasonSetsFetched += len(event['data'])
        
            x = 0
            seasonSetCounter = 1
            while seasonSetCounter <= totalNumberOfSeasonSetsFetched:
                seasonSetId = event['data'][x]['id']    

                # Remove the Vids from the JSON 
                event['data'][x] = remove_values(event['data'][x], "vid")
                    
                print "Migrating Season Set " + seasonSetId
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
                    print "Error Migrating Season Set " + seasonSetId
                    print postResponse
                else:
                    print "Successfully Migrated Season Set " + seasonSetId

                # Increment the counters and flush the lists 
                totalNumberOfSeasonSets += 1
                seasonSetCounter += 1
                x += 1
                
        if totalNumberOfSeasonSets == seasonSetCount: 
            fetchComplete = True
            
    # Close the response channel 
    response1.close()

    print "Total Number of Season Sets Processed: " +str(totalNumberOfSeasonSets)
    return 200

def migrate_billing_plans(source, destination, sourceURL, destinationURL): 
    print "------------------------------------------------------------------------"
    # Only migrate active Billing Plans option
    onlyMigrateActiveBillingPlans = True

    if onlyMigrateActiveBillingPlans == True: 
        print "Migrating ACTIVE Billing Plans...."
    else: 
        print "Migrating ACTIVE and INACTIVE BillingPlans...."
        
    # Set how many BillingPlans to fetch at a time from the command line parameters
    command1 = '/billing_plans?limit=1' 
    command2 = '/billing_plans/'
    
    # Initial some of the variables needed to do the fetch and db load 
    fetchComplete = False
    totalNumberOfBillingPlans = 0
    
    while fetchComplete != True:
        target1 = sourceURL + command1 

        # Get the first batch of BillingPlans
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
            numberOfBillingPlansFetched = 0
        else: 
            fetchComplete = True
      
        if 'total_count' in event:
            billingPlanCount = event['total_count']
            numberOfBillingPlansFetched += len(event['data'])
      
            x = 0
            billingPlanCounter = 1
            while billingPlanCounter <= numberOfBillingPlansFetched:
                merchantBillingPlanId = event['data'][x]['id']
                event['data'][x]['id'] = merchantBillingPlanId
                merchantBillingPlanstatus = event['data'][x]['status']     

                # Check if the option to only cache active BillingPlans is set
                if (onlyMigrateActiveBillingPlans == True and merchantBillingPlanstatus == "Active") or (onlyMigrateActiveBillingPlans == False):
                    event['data'][x] = remove_values(event['data'][x], "vid")
                    del event['data'][x]['used_on_subscriptions']
                
                    print "Migrating Billing Plan " + merchantBillingPlanId

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
                        print "Error Migrating Billing " + merchantBillingPlanId
                        print postResponse
                    else:
                        print "Successfully Migrated Billing Plan " + merchantBillingPlanId

                # Increment the counters and flush the lists 
                totalNumberOfBillingPlans += 1
                billingPlanCounter += 1
                x += 1
                
        if totalNumberOfBillingPlans == billingPlanCount: 
            fetchComplete = True
            
    # Close the response channel 
    response1.close()
    print "Total Number of Billing Plans Processed: " +str(totalNumberOfBillingPlans)
    return 200

def migrate_products(source, destination, sourceURL, destinationURL): 
    print "------------------------------------------------------------------------"
    # Only migrate active products option
    onlyMigrateActiveProducts = True

    if onlyMigrateActiveProducts == True: 
        print "Migrating ACTIVE Products...."
    else: 
        print "Migrating ACTIVE and INACTIVE Products...."
        
    # Set how many products to fetch at a time from the command line parameters
    command1 = '/products?limit=1' 
    command2 = '/products/'
        
    # Initial some of the variables needed to do the fetch and db load 
    fetchComplete = False
    totalNumberOfProducts = 0
        
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
                merchantProductStatus = event['data'][x]['status']     

                # Check if the option to only cache active products is set
                if (onlyMigrateActiveProducts == True and merchantProductStatus == "Active") or (onlyMigrateActiveProducts == False):
                    event['data'][x] = remove_values(event['data'][x], "vid")

                    print "Migrating Product " + merchantProductId

                    # Remove Product Bundles from the initial load 
                    # We will have to cycle back around to add the bundles as a next step 
                    if 'bundled_products' in event['data'][x]:
                        print "Removing Product Bundle from Product " + merchantProductId
                        del event['data'][x]['bundled_products']
                        del event['data'][x]['inherited_entitlements']

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
                        print "Error Migrating Product " + merchantProductId
                        print postResponse
                    else:
                        print "Successfully Migrated Product " + merchantProductId

                # Increment the counters and flush the lists 
                totalNumberOfProducts += 1
                productCounter += 1
                x += 1
                
        if totalNumberOfProducts == productCount: 
            fetchComplete = True
            
    # Close the response channel 
    response1.close()

    print "Total Number of Products Processed: " +str(totalNumberOfProducts)
    return 200

def migrate_campaigns(source, destination, sourceURL, destinationURL): 
    print "------------------------------------------------------------------------"

    # Only migrate active option
    onlyMigrateActiveCampaigns = True

    if onlyMigrateActiveCampaigns == True: 
        print "Migrating ACTIVE Campaigns...."
    else: 
        print "Migrating ACTIVE and INACTIVE Campaigns...."

    # Set how many Campaigns to fetch at a time from the command line parameters
    command1 = '/campaigns?limit=1' 
    command2 = '/campaigns/'
        
    # Initial some of the variables needed to do the fetch and db load 
    fetchComplete = False
    totalNumberOfCampaigns = 0
        
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
            totalNumberOfCampaignsFetched = 0
        else: 
            fetchComplete = True
        
        if 'total_count' in event:
            campaignCount = event['total_count']
            totalNumberOfCampaignsFetched += len(event['data'])
        
            x = 0
            campaignCounter = 1
            while campaignCounter <= totalNumberOfCampaignsFetched:
                campaignId = event['data'][x]['id']
                campaignStatus = event['data'][x]['state']     

                # Check if the option to only cache active is set
                if (onlyMigrateActiveCampaigns == True and campaignStatus == "Active") or (onlyMigrateActiveCampaigns == False):
                    # Remove the Vids from the JSON 
                    event['data'][x] = remove_values(event['data'][x], "vid")
                    
                    print "Migrating Campaign " + campaignId
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
                        print "Error Migrating Campaign " + campaignId
                        print postResponse
                    else:
                        print "Successfully Migrated Campaign " + campaignId

                # Increment the counters and flush the lists 
                totalNumberOfCampaigns += 1
                campaignCounter += 1
                x += 1
                
        if totalNumberOfCampaigns == campaignCount: 
            fetchComplete = True
            
    # Close the response channel 
    response1.close()

    print "Total Number of Campaigns Processed: " +str(totalNumberOfCampaigns)
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
sourceLogin = "<source environment credentials>"
destinationLogin = "<destination environment credentials>"

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
    result = migrate_rate_plans(source, destination, sourceURL, destinationURL)
    result = migrate_season_sets(source, destination, sourceURL, destinationURL)
    result = migrate_billing_plans(source, destination, sourceURL, destinationURL)
    result = migrate_products(source, destination, sourceURL, destinationURL)
    result = migrate_campaigns(source, destination, sourceURL, destinationURL)
