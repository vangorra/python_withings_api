# Python library for the Withings Health API

[![Build Status](https://travis-ci.org/orcasgit/python-withings.svg?branch=master)](https://travis-ci.org/orcasgit/python-withings) [![Coverage Status](https://coveralls.io/repos/orcasgit/python-withings/badge.png?branch=master)](https://coveralls.io/r/orcasgit/python-withings?branch=master) [![Requirements Status](https://requires.io/github/orcasgit/python-withings/requirements.svg?branch=master)](https://requires.io/github/orcasgit/python-withings/requirements/?branch=master)

Withings Health API
<https://developer.withings.com/oauth2/>

Uses OAuth 2.0 to authenticate. You need to obtain a client id
and consumer secret from Withings by creating an application
here: <http://developer.withings.com/oauth2/>

**Installation:**

    pip install withings

**Usage:**

``` python
from withings import WithingsAuth, WithingsApi
from settings import CLIENT_ID, CONSUMER_SECRET, CALLBACK_URI

auth = WithingsAuth(CLIENT_ID, CONSUMER_SECRET, callback_uri=CALLBACK_URI)
authorize_url = auth.get_authorize_url()
print("Go to %s allow the app and copy the url you are redirected to." % authorize_url)
authorization_response = raw_input('Please enter your full authorization response url: ')
creds = auth.get_credentials(authorization_response)

client = WithingsApi(creds)
measures = client.get_measures(limit=1)
print("Your last measured weight: %skg" % measures[0].weight)

creds = client.get_credentials()
```
**Saving Credentials:**


	withings saveconfig --consumer-key [consumerkey] --consumer-secret [consumersecret] --callback-url [callbackurl] --config withings.cfg`

 Which will save the necessary credentials to `withings.cfg`
 
 **Using Saved Credentials**
  
``` python
from withings import WithingsAuth, WithingsApi, WithingsCredentials
from settings import CLIENT_ID, CONSUMER_SECRET, ACCESS_TOKEN, TOKEN_EXPIRY, TOKEN_TYPE, REFRESH_TOKEN, USER_ID

creds = WithingsCredentials(ACCESS_TOKEN, TOKEN_EXPIRY, TOKEN_TYPE, REFRESH_TOKEN, USER_ID, CLIENT_ID, CONSUMER_SECRET )
client = WithingsApi(creds)

measures = client.get_measures(limit=1)
print("Your last measured weight: %skg" % measures[0].weight)
```


