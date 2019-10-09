import unittest

import arrow
from withings_api import WithingsAuth
from requests_oauthlib import OAuth2Session

from unittest.mock import MagicMock
from withings_api.common import Credentials


class TestWithingsAuth(unittest.TestCase):
    def setUp(self):
        self.client_id = 'fake_client_id'
        self.consumer_secret = 'fake_consumer_secret'
        self.callback_uri = 'http://127.0.0.1:8080'
        self.auth_args = (
            self.client_id,
            self.consumer_secret,
        )
        self.token = {
            'access_token': 'fake_access_token',
            'expires_in': 11,
            'token_type': 'Bearer',
            'refresh_token': 'fake_refresh_token',
            'userid': 'fake_user_id'
        }
        OAuth2Session.authorization_url = MagicMock(return_value=('URL', ''))
        OAuth2Session.fetch_token = MagicMock(return_value=self.token)
        OAuth2Session.refresh_token = MagicMock(return_value=self.token)
        arrow.utcnow = MagicMock(return_value=arrow.get(100000000))

    def test_attributes(self):
        """ Make sure the WithingsAuth objects have the right attributes """
        assert hasattr(WithingsAuth, 'URL')
        self.assertEqual(WithingsAuth.URL,
                         'https://account.withings.com')
        auth = WithingsAuth(*self.auth_args, callback_uri=self.callback_uri)
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
        auth = WithingsAuth(*self.auth_args, callback_uri=self.callback_uri)
        # Returns the OAuth2Session.authorization_url results
        self.assertEqual(auth.get_authorize_url(), 'URL')
        OAuth2Session.authorization_url.assert_called_once_with(
            '{}/oauth2_user/authorize2'.format(WithingsAuth.URL)
        )

    def test_get_credentials(self):
        """ Make sure the get_credentials function works as expected """
        auth = WithingsAuth(*self.auth_args, callback_uri=self.callback_uri)
        # Returns an authorized Credentials object
        creds = auth.get_credentials('FAKE_CODE')

        self.assertEqual(
            creds,
            Credentials(
                access_token='fake_access_token',
                token_expiry=100000011,
                token_type='Bearer',
                refresh_token='fake_refresh_token',
                user_id='fake_user_id',
                client_id=self.client_id,
                consumer_secret=self.consumer_secret,
            )
        )
