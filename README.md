# Python withings-api [![Build status](https://github.com/vangorra/python_withings_api/workflows/Build/badge.svg?branch=master)](https://github.com/vangorra/python_withings_api/actions?workflow=Build) [![Coverage Status](https://coveralls.io/repos/github/vangorra/python_withings_api/badge.svg?branch=master)](https://coveralls.io/github/vangorra/python_withings_api?branch=master) [![PyPI](https://img.shields.io/pypi/v/withings-api)](https://pypi.org/project/withings-api/)
Python library for the Withings Health API


Withings Health API
<https://developer.withings.com/oauth2/>

Uses OAuth 2.0 to authenticate. You need to obtain a client id
and consumer secret from Withings by creating an application
here: <http://developer.withings.com/oauth2/>

## Installation

    pip install withings-api

## Usage
For a complete example, checkout the integration test in `scripts/integration_test.py`. It has a working example on how to use the API.
```python
from withings_api import WithingsAuth, WithingsApi, AuthScope
from withings_api.common import get_measure_value, MeasureType

auth = WithingsAuth(
    client_id='your client id',
    consumer_secret='your consumer secret',
    callback_uri='your callback uri',
    mode='demo',  # Used for testing. Remove this when getting real user data.
    scope=(
        AuthScope.USER_ACTIVITY,
        AuthScope.USER_METRICS,
        AuthScope.USER_INFO,
        AuthScope.USER_SLEEP_EVENTS,
    )
)

authorize_url = auth.get_authorize_url()
# Have the user goto authorize_url and authorize the app. They will be redirected back to your redirect_uri.

credentials = auth.get_credentials('code from the url args of redirect_uri')

# Now you are ready to make calls for data.
api = WithingsApi(credentials)

meas_result = api.measure_get_meas()
weight_or_none = get_measure_value(meas_result, with_measure_type=MeasureType.WEIGHT)
```

## Building
Building, testing and lintings of the project is all done with one script. You only need a few dependencies.

Dependencies:
- python3 in your path.
- The python3 `venv` module.

The build script will setup the venv, dependencies, test and lint and bundle the project.
```bash
./scripts/build.sh
```

## Integration Testing
There exists a simple integration test that runs against Withings' demo data. It's best to run this after you have
successful builds. 

Note: after changing the source, you need to run build for the integration test to pickup the changes.

```bash
./scripts/build.sh
source ./venv/bin/activate
./scripts/integration_test.py --client-id <your client id> --consumer-secret <your consumer secret> --callback-uri <your clalback uri>
```
The integration test will cache the credentials in a `<project root>/.credentials` file between runs. If you get an error saying
the access token expired, then remove that credentials file and try again.
