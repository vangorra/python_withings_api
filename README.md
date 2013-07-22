# Python library for the Withings API

Withings Body metrics Services API
<http://www.withings.com/en/api/wbsapiv2>

Uses Oauth 1.0 to authentify. You need to obtain a consumer key
and consumer secret from Withings by creating an application
here: <https://oauth.withings.com/partner/add>

Installation:

    pip install -e git+https://github.com/carlosescri/python-withings.git#egg=withings-dev

Usage:

    auth = WithingsAuth(CONSUMER_KEY, CONSUMER_SECRET)
    authorize_url = auth.get_authorize_url()
    print "Go to %s allow the app and copy your oauth_verifier" % authorize_url
    oauth_verifier = raw_input('Please enter your oauth_verifier: ')
    creds = auth.get_credentials(oauth_verifier)

    client = WithingsApi(creds)
    measures = client.get_measures(limit=1)
    print "Your last measured weight: %skg" % measures[0].weight 
