# Python library for the Nokia Health API

[![Build Status](https://travis-ci.org/orcasgit/python-nokia.svg?branch=master)](https://travis-ci.org/orcasgit/python-nokia) [![Coverage Status](https://coveralls.io/repos/orcasgit/python-nokia/badge.png?branch=master)](https://coveralls.io/r/orcasgit/python-nokia?branch=master) [![Requirements Status](https://requires.io/github/orcasgit/python-nokia/requirements.svg?branch=requires-io-master)](https://requires.io/github/orcasgit/python-nokia/requirements/?branch=requires-io-master)

Nokia Health API
<https://developer.health.nokia.com/api/doc>

Uses Oauth 1.0 to authentify. You need to obtain a consumer key
and consumer secret from Nokia by creating an application
here: <https://developer.health.nokia.com/en/partner/add>

**Installation:**

    pip install nokia

**Usage:**

``` python
from nokia import NokiaAuth, NokiaApi
from settings import CONSUMER_KEY, CONSUMER_SECRET

auth = NokiaAuth(CONSUMER_KEY, CONSUMER_SECRET)
authorize_url = auth.get_authorize_url()
print("Go to %s allow the app and copy your oauth_verifier" % authorize_url)

oauth_verifier = raw_input('Please enter your oauth_verifier: ')
creds = auth.get_credentials(oauth_verifier)

client = NokiaApi(creds)
measures = client.get_measures(limit=1)
print("Your last measured weight: %skg" % measures[0].weight)
```
**Saving Credentials:**


	nokia saveconfig --consumer-key [consumerkey] --consumer-secret [consumersecret] --config nokia.cfg`

 Which will save the necessary credentials to `nokia.cfg`
 
 **Using Saved Credentials**
  
```
from nokia import NokiaAuth, NokiaApi, NokiaCredentials
from settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, USER_ID

creds = NokiaCredentials(ACCESS_TOKEN, 
						ACCESS_TOKEN_SECRET, 
						CONSUMER_KEY, 
						CONSUMER_SECRET, 
						USER_ID)
client = NokiaApi(creds)

measures = client.get_measures(limit=1)
print("Your last measured weight: %skg" % measures[0].weight)
```
 
 
 **Running From Command line:**

```
nokia [command] --config nokia.cfg 
```

