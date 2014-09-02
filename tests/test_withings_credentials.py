import unittest

from withings import WithingsAuth, WithingsCredentials


class TestWithingsCredentials(unittest.TestCase):

    def test_attributes(self):
        """
        Make sure the WithingsCredentials objects have the right attributes
        """
        creds = WithingsCredentials(access_token=1, access_token_secret=1,
                                    consumer_key=1, consumer_secret=1,
                                    user_id=1)
        assert hasattr(creds, 'access_token')
        self.assertEqual(creds.access_token, 1)
        assert hasattr(creds, 'access_token_secret')
        self.assertEqual(creds.access_token_secret, 1)
        assert hasattr(creds, 'consumer_key')
        self.assertEqual(creds.consumer_key, 1)
        assert hasattr(creds, 'consumer_secret')
        self.assertEqual(creds.consumer_secret, 1)
        assert hasattr(creds, 'user_id')
        self.assertEqual(creds.user_id, 1)

    def test_attribute_defaults(self):
        """
        Make sure WithingsCredentials attributes have the proper defaults
        """
        creds = WithingsCredentials()
        self.assertEqual(creds.access_token, None)
        self.assertEqual(creds.access_token_secret, None)
        self.assertEqual(creds.consumer_key, None)
        self.assertEqual(creds.consumer_secret, None)
        self.assertEqual(creds.user_id, None)
