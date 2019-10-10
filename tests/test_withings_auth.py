import arrow
from withings_api import WithingsAuth
from requests_oauthlib import OAuth2Session

from unittest.mock import MagicMock
from withings_api.common import Credentials


class TestWithingsAuth:
    def setup(self):
        self.client_id = 'fake_client_id'
        self.consumer_secret = 'fake_consumer_secret'
        callback_uri = 'http://127.0.0.1:8080'
        token = {
            'access_token': 'fake_access_token',
            'expires_in': 11,
            'token_type': 'Bearer',
            'refresh_token': 'fake_refresh_token',
            'userid': 'fake_user_id'
        }
        OAuth2Session.fetch_token = MagicMock(return_value=token)
        OAuth2Session.refresh_token = MagicMock(return_value=token)
        arrow.utcnow = MagicMock(return_value=arrow.get(100000000))

        self.auth = WithingsAuth(
            self.client_id,
            self.consumer_secret,
            callback_uri=callback_uri
        )

    def test_get_authorize_url(self):
        """ Make sure the get_authorize_url function works as expected """

        url = self.auth.get_authorize_url()

        assert url.startswith(
            'https://account.withings.com/oauth2_user/authorize2'
            '?response_type=code&client_id=fake_client_id'
            '&redirect_uri=http%3A%2F%2F127.0.0.1%3A8080'
            '&scope=user.metrics&state='
        )

    def test_get_credentials(self):
        """ Make sure the get_credentials function works as expected """
        creds = self.auth.get_credentials('FAKE_CODE')

        assert creds == Credentials(
            access_token='fake_access_token',
            token_expiry=100000011,
            token_type='Bearer',
            refresh_token='fake_refresh_token',
            user_id='fake_user_id',
            client_id=self.client_id,
            consumer_secret=self.consumer_secret,
        )
