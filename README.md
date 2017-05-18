# Python library for the Withings API

[![Build Status](https://travis-ci.org/orcasgit/python-withings.svg?branch=master)](https://travis-ci.org/orcasgit/python-withings) [![Coverage Status](https://coveralls.io/repos/orcasgit/python-withings/badge.png?branch=master)](https://coveralls.io/r/orcasgit/python-withings?branch=master) [![Requirements Status](https://requires.io/github/orcasgit/python-withings/requirements.svg?branch=requires-io-master)](https://requires.io/github/orcasgit/python-withings/requirements/?branch=requires-io-master)

Withings Body metrics Services API
<http://oauth.withings.com/api/doc>

Uses Oauth 1.0 to authentify. You need to obtain a consumer key
and consumer secret from Withings by creating an application
here: <https://oauth.withings.com/partner/add>

Installation:

    pip install https://github.com/orcasgit/python-withings/archive/master.zip#egg=withings-0.4.0

Usage:

``` python
from withings import WithingsAuth, WithingsApi
from settings import CONSUMER_KEY, CONSUMER_SECRET

auth = WithingsAuth(CONSUMER_KEY, CONSUMER_SECRET)
authorize_url = auth.get_authorize_url()
print "Go to %s allow the app and copy your oauth_verifier" % authorize_url

oauth_verifier = raw_input('Please enter your oauth_verifier: ')
creds = auth.get_credentials(oauth_verifier)

client = WithingsApi(creds)
measures = client.get_measures(limit=1)
print "Your last measured weight: %skg" % measures[0].weight 
```
