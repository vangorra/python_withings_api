# -*- coding: utf-8 -*-
# 
"""
Python library for the Withings API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Withings Body metrics Services API
<http://www.withings.com/en/api/wbsapiv2>

Uses Oauth 1.0 to authentify. You need to obtain a consumer key
and consumer secret from Withings by creating an application
here: <https://oauth.withings.com/partner/add>

Usage:

auth = WithingsAuth(CONSUMER_KEY, CONSUMER_SECRET)
authorize_url = auth.get_authorize_url()
print "Go to %s allow the app and copy your oauth_verifier" % authorize_url
oauth_verifier = raw_input('Please enter your oauth_verifier: ')
creds = auth.get_credentials(oauth_verifier)

client = WithingsApi(creds)
measures = client.get_measures(limit=1)
print "Your last measured weight: %skg" % measures[0].weight 

"""

__title__ = 'withings'
__version__ = '0.1'
__author__ = 'Maxime Bouroumeau-Fuseau'
__license__ = 'MIT'
__copyright__ = 'Copyright 2012 Maxime Bouroumeau-Fuseau'

__all__ = ['WithingsCredentials', 'WithingsAuth', 'WithingsApi', 'WithingsMeasures', 'WithingsMeasureGroup']

import requests
from requests.auth import OAuth1
from oauth_hook import OAuthHook
from urlparse import parse_qs
import json
import datetime


class WithingsCredentials(object):
    def __init__(self, access_token=None, access_token_secret=None, consumer_key=None, consumer_secret=None, user_id=None):
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.user_id = user_id


class WithingsAuth(object):
    URL = 'https://oauth.withings.com/account'

    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

    def get_authorize_url(self):
        oauth_hook = OAuthHook(consumer_key=self.consumer_key, consumer_secret=self.consumer_secret)
        response = requests.post('%s/request_token' % self.URL, hooks={'pre_request': oauth_hook})
        qs = parse_qs(response.text)
        self.oauth_token = qs['oauth_token'][0]
        self.oauth_secret = qs['oauth_token_secret'][0]
        return "%s/authorize?oauth_token=%s" % (self.URL, self.oauth_token)

    def get_credentials(self, oauth_verifier):
        oauth_hook = OAuthHook(self.oauth_token, self.oauth_secret, self.consumer_key, self.consumer_secret)
        response = requests.post('%s/access_token' % self.URL, {'oauth_verifier': oauth_verifier}, 
                                 hooks={'pre_request': oauth_hook})
        response = parse_qs(response.content)
        return WithingsCredentials(response['oauth_token'][0], response['oauth_token_secret'][0], 
                              self.consumer_key, self.consumer_secret, response['userid'][0])


class WithingsApi(object):
    URL = 'http://wbsapi.withings.net'

    def __init__(self, credentials):
        self.credentials = credentials
        self.oauth = OAuth1(unicode(credentials.consumer_key), unicode(credentials.consumer_secret),
                    unicode(credentials.access_token), unicode(credentials.access_token_secret),
                    signature_type='query')
        self.client = requests.session(auth=self.oauth, params={'userid': credentials.user_id})

    def request(self, service, action, params=None, method='GET'):
        if params is None:
            params = {}
        params['action'] = action
        r = self.client.request(method, '%s/%s' % (self.URL, service), params=params)
        response = json.loads(r.content)
        if response['status'] != 0:
            raise Exception("Error code %s" % response['status'])
        return response.get('body', None)

    def get_user(self):
        return self.request('user', 'getbyuserid')

    def get_measures(self, **kwargs):
        r = self.request('measure', 'getmeas', kwargs)
        return WithingsMeasures(r)

    def subscribe(self, callback_url, comment, appli=1):
        params = {'callbackurl': callback_url,
                  'comment': comment,
                  'appli': appli}
        self.request('notify', 'subscribe', params)

    def unsubscribe(self, callback_url, appli=1):
        params = {'callbackurl': callback_url, 'appli': appli}
        self.request('notify', 'revoke', params)

    def is_subscribed(self, callback_url, appli=1):
        params = {'callbackurl': callback_url, 'appli': appli}
        try:
            self.request('notify', 'get', params)
            return True
        except:
            return False

    def list_subscriptions(self, appli=1):
        r = self.request('notify', 'list', {'appli': appli})
        return r['profiles']


class WithingsMeasures(list):
    def __init__(self, data):
        super(WithingsMeasures, self).__init__([WithingsMeasureGroup(g) for g in data['measuregrps']])
        self.updatetime = datetime.datetime.fromtimestamp(data['updatetime'])


class WithingsMeasureGroup(object):
    MEASURE_TYPES = (('weight', 1), ('height', 4), ('fat_free_mass', 5),
                     ('fat_ratio', 6), ('fat_mass_weight', 8),
                     ('diastolic_blood_pressure', 9), ('systolic_blood_pressure', 10),
                     ('heart_pulse', 11))

    def __init__(self, data):
        self.data = data
        self.grpid = data['grpid']
        self.attrib = data['attrib']
        self.date = datetime.datetime.fromtimestamp(data['date'])
        self.measures = data['measures']
        for n, t in self.MEASURE_TYPES:
            self.__setattr__(n, self.get_measure(t))

    def is_ambiguous(self):
        return self.attrib == 1 or self.attrib == 4

    def is_measure(self):
        return self.category == 1

    def is_target(self):
        return self.category == 2

    def get_measure(self, measure_type):
        for m in self.measures:
            if m['type'] == measure_type:
                return m['value'] * pow(10, m['unit'])
        return None
