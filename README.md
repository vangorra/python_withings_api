# Python library for the Nokia Health API

[![Build Status](https://travis-ci.org/orcasgit/python-nokia.svg?branch=master)](https://travis-ci.org/orcasgit/python-nokia) [![Coverage Status](https://coveralls.io/repos/orcasgit/python-nokia/badge.png?branch=master)](https://coveralls.io/r/orcasgit/python-nokia?branch=master) [![Requirements Status](https://requires.io/github/orcasgit/python-nokia/requirements.svg?branch=master)](https://requires.io/github/orcasgit/python-nokia/requirements/?branch=master)

Nokia Health API
<https://developer.withings.com/oauth2/>

Uses OAuth 2.0 to authenticate. You need to obtain a client id
and consumer secret from Nokia by creating an application
here: <https://account.withings.com/partner/add_oauth2>

**Installation:**

    pip install nokia

**Usage:**

``` python
from nokia import NokiaAuth, NokiaApi
from settings import CLIENT_ID, CONSUMER_SECRET, CALLBACK_URI

auth = NokiaAuth(CLIENT_ID, CONSUMER_SECRET, callback_uri=CALLBACK_URI)
authorize_url = auth.get_authorize_url()
print("Go to %s allow the app and copy the url you are redirected to." % authorize_url)
authorization_response = raw_input('Please enter your full authorization response url: ')
creds = auth.get_credentials(authorization_response)

client = NokiaApi(creds)
measures = client.get_measures(limit=1)
print("Your last measured weight: %skg" % measures[0].weight)

creds = client.get_credentials()
```
**Saving Credentials:**


	nokia saveconfig --consumer-key [consumerkey] --consumer-secret [consumersecret] --callback-url [callbackurl] --config nokia.cfg`

 Which will save the necessary credentials to `nokia.cfg`
 
 **Using Saved Credentials**
  
``` python
from nokia import NokiaAuth, NokiaApi, NokiaCredentials
from settings import CLIENT_ID, CONSUMER_SECRET, ACCESS_TOKEN, TOKEN_EXPIRY, TOKEN_TYPE, REFRESH_TOKEN, USER_ID

creds = NokiaCredentials(ACCESS_TOKEN, TOKEN_EXPIRY, TOKEN_TYPE, REFRESH_TOKEN, USER_ID, CLIENT_ID, CONSUMER_SECRET )
client = NokiaApi(creds)

measures = client.get_measures(limit=1)
print("Your last measured weight: %skg" % measures[0].weight)
```
 
 
 **Running From Command line:**

	nokia [command] --config nokia.cfg 


