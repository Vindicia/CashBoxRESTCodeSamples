PaymentMethodTokenization-PMT

PMT(REST HOA)

This folder contains sample code to make PMT call via REST in PRODTEST environment

Steps:

1.Open the file hmac_forRESTHOA_prodtest.pl and edit the following field values: 

$private_key (Vindicia provides a key) 
$token(Create you own value for this field, ex:PMTToken1)



2.Open the shell(or command prompt) and execute the following command: 
perl hmac_forRESTHOA_prodtest.pl 
(This is a sample file to generate the signed one time token)

Example:

hariprko01-mac:HOA#-PMTFiles hariprko$ perl hmac_forRESTHOA_prodtest.pl 
Token: KHPApril12T2 
Full Token Value: KHPApril12T2#POST#/payment_methods 
Signed: 51a87ba13140d8f7b0b25acf78f4e1f8fa12105d9a7f6aee149e61438aa743f2

Save the value received in "Signed:"



3.Edit the PaymentMethodTokenForm.html file:

For " vin_session_id", give the value provided in Step1.($token)
For "vin_session_hash", give the value that is saved in Step2

Make sure the following values are pointed to PRODTES Urls. 

vindiciaServer: "secure.prodtest.sj.vindicia.com", // to load the iframes from vindiciaRestServer: "api.prodtest.vindicia.com", // to submit the JSON data to

For "vindiciaAuthId", get the value from Header section after entering the REST user credentials that are provided by Vindicia.

After the changes are done, load your application , enter the credit card credentials, submit and in the response retrieve the values for "vid" which will be used later to update the existing Account with this new Payment Method.
Example response:

{ "object": "PaymentMethod", "id": "paymeth_104", "vid": "21536bbe3143b8a474448519102423fe51209848" }



Using REST, to make Account.Update call, make the method = "POST" and end point = https://api.prodtest.vindicia.com/accounts/AccountID1523568051076
Check the file Account_Udpate_with_PMT_JSONRequest for the JSON request sample code. Check the file Account_Udpate_with_PMT_JSONResponse for the response received.