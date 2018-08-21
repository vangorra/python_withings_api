import unittest

from nokia import NokiaAuth, NokiaCredentials


class TestNokiaCredentials(unittest.TestCase):

    def test_attributes(self):
        """
        Make sure the NokiaCredentials objects have the right attributes
        """
        creds = NokiaCredentials(access_token=1, token_expiry=2, token_type=3,
                                 refresh_token=4, user_id=5, client_id=6,
                                 consumer_secret=7)
        assert hasattr(creds, 'access_token')
        self.assertEqual(creds.access_token, 1)
        assert hasattr(creds, 'token_expiry')
        self.assertEqual(creds.token_expiry, 2)
        assert hasattr(creds, 'token_type')
        self.assertEqual(creds.token_type, 3)
        assert hasattr(creds, 'refresh_token')
        self.assertEqual(creds.refresh_token, 4)
        assert hasattr(creds, 'user_id')
        self.assertEqual(creds.user_id, 5)
        assert hasattr(creds, 'client_id')
        self.assertEqual(creds.client_id, 6)
        assert hasattr(creds, 'consumer_secret')
        self.assertEqual(creds.consumer_secret, 7)

    def test_attribute_defaults(self):
        """
        Make sure NokiaCredentials attributes have the proper defaults
        """
        creds = NokiaCredentials()
        self.assertEqual(creds.access_token, None)
        self.assertEqual(creds.token_expiry, None)
        self.assertEqual(creds.token_type, None)
        self.assertEqual(creds.token_expiry, None)
        self.assertEqual(creds.user_id, None)
        self.assertEqual(creds.client_id, None)
        self.assertEqual(creds.consumer_secret, None)
