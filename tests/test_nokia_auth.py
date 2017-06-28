import unittest

from nokia import NokiaAuth, NokiaCredentials
from requests_oauthlib import OAuth1Session

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock


class TestNokiaAuth(unittest.TestCase):
    def setUp(self):
        self.consumer_key = 'fake_consumer_key'
        self.consumer_secret = 'fake_consumer_secret'
        self.request_token = {
            'oauth_token': 'fake_oauth_token',
            'oauth_token_secret': 'fake_oauth_token_secret'
        }
        self.access_token = self.request_token
        self.access_token.update({'userid': 'FAKEID'})
        OAuth1Session.fetch_request_token = MagicMock(
            return_value=self.request_token)
        OAuth1Session.authorization_url = MagicMock(return_value='URL')
        OAuth1Session.fetch_access_token = MagicMock(
            return_value=self.access_token)

    def test_attributes(self):
        """ Make sure the NokiaAuth objects have the right attributes """
        assert hasattr(NokiaAuth, 'URL')
        auth = NokiaAuth(self.consumer_key, self.consumer_secret)
        assert hasattr(auth, 'consumer_key')
        self.assertEqual(auth.consumer_key, self.consumer_key)
        assert hasattr(auth, 'consumer_secret')
        self.assertEqual(auth.consumer_secret, self.consumer_secret)

    def test_attribute_defaults(self):
        """ Make sure NokiaAuth attributes have the proper defaults """
        self.assertEqual(NokiaAuth.URL,
                         'https://developer.health.nokia.com/account/')
        auth = NokiaAuth(self.consumer_key, self.consumer_secret)
        self.assertEqual(auth.oauth_token, None)
        self.assertEqual(auth.oauth_secret, None)

    def test_get_authorize_url(self):
        """ Make sure the get_authorize_url function works as expected """
        auth = NokiaAuth(self.consumer_key, self.consumer_secret)
        # Returns the OAuth1Session.authorization_url results
        self.assertEqual(auth.get_authorize_url(), 'URL')
        # oauth_token and oauth_secret have now been set to the values
        # returned by OAuth1Session.fetch_request_token
        self.assertEqual(auth.oauth_token, 'fake_oauth_token')
        self.assertEqual(auth.oauth_secret, 'fake_oauth_token_secret')

    def test_get_credentials(self):
        """ Make sure the get_credentials function works as expected """
        auth = NokiaAuth(self.consumer_key, self.consumer_secret)
        # Returns an authorized NokiaCredentials object
        creds = auth.get_credentials('FAKE_OAUTH_VERIFIER')
        assert isinstance(creds, NokiaCredentials)
        # Check that the attributes of the NokiaCredentials object are
        # correct.
        self.assertEqual(creds.access_token, 'fake_oauth_token')
        self.assertEqual(creds.access_token_secret, 'fake_oauth_token_secret')
        self.assertEqual(creds.consumer_key, self.consumer_key)
        self.assertEqual(creds.consumer_secret, self.consumer_secret)
        self.assertEqual(creds.user_id, 'FAKEID')
