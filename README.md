# Python library for the Withings Health API

[![Build Status](https://travis-ci.org/vangorra/python_withings_api.svg?branch=master)](https://travis-ci.org/vangorra/python_withings_api) 
[![Maintainability](https://api.codeclimate.com/v1/badges/36983f024cf45aab80ba/maintainability)](https://codeclimate.com/github/vangorra/python_withings_api/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/36983f024cf45aab80ba/test_coverage)](https://codeclimate.com/github/vangorra/python_withings_api/test_coverage)

Withings Health API
<https://developer.withings.com/oauth2/>

Uses OAuth 2.0 to authenticate. You need to obtain a client id
and consumer secret from Withings by creating an application
here: <http://developer.withings.com/oauth2/>

**Installation:**

    pip install withings-api

**Usage:**

``` python
from withings_api import WithingsAuth, WithingsApi
from withings_api.common import get_measure_value, MeasureType

auth = WithingsAuth(CLIENT_ID, CONSUMER_SECRET, callback_uri=CALLBACK_URI)
authorize_url = auth.get_authorize_url()
print("Go to %s allow the app and copy the url you are redirected to." % authorize_url)
authorization_response = raw_input('Please enter your full authorization response url: ')
creds = auth.get_credentials(authorization_response)

client = WithingsApi(creds)
get_meas_response = client.get_meas(limit=1)
print("Your last measured weight: %skg" % get_measure_value(
    get_meas_response,
    MeasureType.WEIGHT 
)

creds = client.get_credentials()
```
