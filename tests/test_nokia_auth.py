import datetime
import unittest
import time

import pytz

from nokia import NokiaAuth, NokiaCredentials
from requests_oauthlib import OAuth2Session

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock


class TestNokiaAuth(unittest.TestCase):
    def setUp(self):
        self.client_id = 'fake_client_id'
        self.consumer_secret = 'fake_consumer_secret'
        self.callback_uri = 'http://127.0.0.1:8080'
        self.auth_args = (
            self.client_id,
            self.consumer_secret,
            self.callback_uri,
        )
        OAuth2Session.authorization_url = MagicMock(return_value=('URL', ''))
        OAuth2Session.fetch_token = MagicMock(return_value={
            'access_token': 'fake_access_token',
            'expires_in': 0,
            'token_type': 'Bearer',
            'refresh_token': 'fake_refresh_token',
            'userid': 'fake_user_id'
        })

    def test_attributes(self):
        """ Make sure the NokiaAuth objects have the right attributes """
        assert hasattr(NokiaAuth, 'URL')
        self.assertEqual(NokiaAuth.URL,
                         'https://account.health.nokia.com')
        auth = NokiaAuth(*self.auth_args)
        assert hasattr(auth, 'client_id')
        self.assertEqual(auth.client_id, self.client_id)
        assert hasattr(auth, 'consumer_secret')
        self.assertEqual(auth.consumer_secret, self.consumer_secret)
        assert hasattr(auth, 'callback_uri')
        self.assertEqual(auth.callback_uri, self.callback_uri)
        assert hasattr(auth, 'scope')
        self.assertEqual(auth.scope, 'user.metrics')

    def test_get_authorize_url(self):
        """ Make sure the get_authorize_url function works as expected """
        auth = NokiaAuth(*self.auth_args)
        # Returns the OAuth2Session.authorization_url results
        self.assertEqual(auth.get_authorize_url(), 'URL')
        OAuth2Session.authorization_url.assert_called_once_with(
            '{}/oauth2_user/authorize2'.format(NokiaAuth.URL)
        )

    def test_get_credentials(self):
        """ Make sure the get_credentials function works as expected """
        auth = NokiaAuth(*self.auth_args)
        # Returns an authorized NokiaCredentials object
        creds = auth.get_credentials('FAKE_CODE')
        assert isinstance(creds, NokiaCredentials)
        # Check that the attributes of the NokiaCredentials object are
        # correct.
        self.assertEqual(creds.access_token, 'fake_access_token')
        self.assertEqual(creds.token_expiry, str(int(
            time.mktime(datetime.datetime.now(tz=pytz.utc).utctimetuple())
        )))
        self.assertEqual(creds.token_type, 'Bearer')
        self.assertEqual(creds.refresh_token, 'fake_refresh_token')
        self.assertEqual(creds.client_id, self.client_id)
        self.assertEqual(creds.consumer_secret, self.consumer_secret)
        self.assertEqual(creds.user_id, 'fake_user_id')
