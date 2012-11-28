# Python library for the Withings API

Withings Body metrics Services API
<http://www.withings.com/en/api/wbsapiv2>

Uses Oauth 1.0 to authentify. You need to obtain a consumer key
and consumer secret from Withings by creating an application
here: <https://oauth.withings.com/partner/add>

Usage:

    wbs_auth = WithingsAuth(CONSUMER_KEY, CONSUMER_SECRET)
    authorize_url = wbs_auth.get_authorize_url()
    print "Go to %s allow the app and copy your oauth_verifier" % authorize_url
    oauth_verifier = raw_input('Please enter your oauth_verifier: ')
    wbs_creds = wbs_auth.get_credentials(oauth_verifier)

    wbs = WithingsApi(wbs_creds)
    measures = wbs.get_measures(limit=1)
    print "Your last measured weight: %skg" % measures[0].weight 
