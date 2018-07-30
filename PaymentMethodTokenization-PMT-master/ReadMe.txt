PaymentMethodTokenization-PMT

PMT(REST HOA)

This folder contains sample code to make PMT call via REST in PRODTEST environment

Steps:

1.Open the file hmac_forRESTHOA_prodtest.pl and edit the following field values: 

$private_key (Vindicia provides a key) 
$token(Create you own value for this field, ex:TokenJuly30)



2.Open the shell(or command prompt) and execute the following command: 
perl hmac_forRESTHOA_prodtest.pl 
(This is a sample file to generate the signed one time token)

Example:

hariprko01-mac:HOA#-PMTFiles hariprko$ perl hmac_forRESTHOA_prodtest.pl
Token: TokenJuly30
Full Token Value: TokenJuly30#POST#/payment_methods
Signed: 5cd80b78a11050080b10db4ccf653f9486c917f61fc23315be0d1d3c7958f971
hariprko01-mac:HOA#-PMTFiles hariprko$ 

Save the value received in "Signed:"



3.Edit the PaymentMethodTokenForm.html file:

For " vin_session_id", give the value provided in Step1.($token)
For "vin_session_hash", give the value that is saved in Step2

Make sure the following values are pointed to PRODTES Urls. 

vindiciaServer: "secure.prodtest.sj.vindicia.com", // to load the iframes from 
vindiciaRestServer: "api.prodtest.vindicia.com", // to submit the JSON data to



For "vindiciaAuthId", get the value from Header section after entering the REST user credentials that are provided by Vindicia.

After the changes are done, load your application , enter the credit card credentials, submit and in the response retrieve the values for "vid" which will be used later to update the existing Account with this new Payment Method.
Example response:

{
   "object": "PaymentMethod",
   "id": "TokenJuly30",
   "vid": "444354f265cefac930ea24b7b63cf4a883267e4c"
}



Using REST, to make Account.Update call, 
make the method = "POST" and 
end point = https://api.prodtest.vindicia.com/accounts/AccountID1532986706979


Check the file Account_Udpate_with_PMT_JSONRequest for the JSON request sample code. Check the file Account_Udpate_with_PMT_JSONResponse for the response received.
