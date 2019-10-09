# -*- coding: utf-8 -*-
#
"""
Python library for the Withings Health API.

Withings Health API
<https://developer.health.withings.com/api>
"""

from __future__ import unicode_literals

import datetime
import json
from typing import Callable

import arrow
from oauthlib.oauth2 import WebApplicationClient
import requests
from requests_oauthlib import OAuth2Session

from .common import (
    new_get_activity_response,
    new_get_sleep_response,
    new_get_sleep_summary_response,
    new_get_meas_response,
    new_list_subscription_response,
    new_credentials,
    GetActivityResponse,
    GetSleepResponse,
    GetSleepSummaryResponse,
    GetMeasResponse,
    ListSubscriptionsResponse,
    Credentials,
)


class WithingsAuth:
    """Handles management of oauth authorization calls."""

    URL = 'https://account.withings.com'

    def __init__(self, client_id, consumer_secret, callback_uri=None,
                 scope='user.metrics'):
        """Initialize new object."""
        self.client_id = client_id
        self.consumer_secret = consumer_secret
        self.callback_uri = callback_uri
        self.scope = scope

    def _oauth(self):
        """Create a new oauth2 session."""
        return OAuth2Session(self.client_id,
                             redirect_uri=self.callback_uri,
                             scope=self.scope)

    def get_authorize_url(self):
        """Generate the authorize url."""
        return self._oauth().authorization_url(
            '%s/oauth2_user/authorize2' % self.URL
        )[0]

    def get_credentials(self, code):
        """Get the oauth credentials."""
        response = self._oauth().fetch_token(
            '%s/oauth2/token' % self.URL,
            code=code,
            client_secret=self.consumer_secret,
            include_client_id=True
        )

        return new_credentials(
            self.client_id,
            self.consumer_secret,
            response
        )


def is_date(key):
    """Return true if provided object is a date."""
    return 'date' in key


def is_date_class(val):
    """
    Return true if provided value is an instance of a date object.

    Supports: datetime.date, datetime.datetime, arrow.Arrow.
    """
    return isinstance(val, (datetime.date, datetime.datetime, arrow.Arrow, ))


class WithingsApi:
    """
    Provides entrypoint for calling the withings api.

    While python-withings takes care of automatically refreshing the OAuth2
    token so you can seamlessly continue making API calls, it is important
    that you persist the updated tokens somewhere associated with the user,
    such as a database table. That way when your application restarts it will
    have the updated tokens to start with. Pass a ``refresh_cb`` function to
    the API constructor and we will call it with the updated token when it gets
    refreshed. The token contains ``access_token``, ``refresh_token``,
    ``token_type`` and ``expires_in``. We recommend making the refresh callback
    a method on your user database model class, so you can easily save the
    updates to the user record, like so:

    class WithingsUser(dbModel):
        def refresh_cb(self, token):
            self.access_token = token['access_token']
            self.refresh_token = token['refresh_token']
            self.token_type = token['token_type']
            self.expires_in = token['expires_in']
            self.save()

    Then when you create the api for your user, just pass the callback:

    user = ...
    creds = ...
    api = WithingsApi(creds, refresh_cb=user.refresh_cb)

    Now the updated token will be automatically saved to the DB for later use.
    """

    URL = 'https://wbsapi.withings.net'

    def __init__(
            self, credentials: Credentials,
            refresh_cb: Callable[[Credentials], None] = None
    ):
        """Initialize new object."""
        self.credentials = credentials
        self.refresh_cb = refresh_cb
        self.token = {
            'access_token': credentials.access_token,
            'refresh_token': credentials.refresh_token,
            'token_type': credentials.token_type,
            'expires_in': str(
                int(credentials.token_expiry) - arrow.utcnow().timestamp
            ),
        }
        oauth_client = WebApplicationClient(
            credentials.client_id,
            token=self.token,
            default_token_placement='query'
        )

        self.client = OAuth2Session(
            credentials.client_id,
            token=self.token,
            client=oauth_client,
            auto_refresh_url='{}/oauth2/token'.format(WithingsAuth.URL),
            auto_refresh_kwargs={
                'client_id': credentials.client_id,
                'client_secret': credentials.consumer_secret,
            },
            token_updater=self.set_token
        )

    def get_credentials(self) -> Credentials:
        """Get the current oauth credentials."""
        return self.credentials

    def set_token(self, token):
        """Set the oauth token."""
        self.token = token
        self.credentials = Credentials(
            access_token=token.get('access_token'),
            token_expiry=arrow.utcnow().timestamp + token.get('expires_in'),
            token_type=self.credentials.token_type,
            refresh_token=token.get('refresh_token'),
            user_id=self.credentials.user_id,
            client_id=self.credentials.client_id,
            consumer_secret=self.credentials.consumer_secret,
        )

        if self.refresh_cb:
            self.refresh_cb(self.credentials)

    def request(self, service, action, params=None, method='GET',
                version=None):
        """Request a specific service."""
        params = params or {}
        params['userid'] = self.credentials.user_id
        params['action'] = action
        for key, val in params.items():
            if is_date(key) and is_date_class(val):
                params[key] = arrow.get(val).timestamp
        url_parts = filter(None, [self.URL, version, service])
        response = self.client.request(
            method,
            '/'.join(url_parts),
            params=params
        )
        response = json.loads(response.content.decode())
        if response['status'] != 0:
            raise requests.exceptions.RequestException(
                "Error code %s" % response['status']
            )
        return response.get('body', None)

    def get_activities(self, **kwargs) -> GetActivityResponse:
        """Get user created activities."""
        response = self.request(
            'measure',
            'getactivity',
            params=kwargs,
            version='v2'
        )

        return new_get_activity_response(response)

    def get_measures(self, **kwargs) -> GetMeasResponse:
        """Get measures."""
        response = self.request('measure', 'getmeas', kwargs)
        return new_get_meas_response(response)

    def get_sleep(self, **kwargs) -> GetSleepResponse:
        """Get sleep data."""
        response = self.request('sleep', 'get', params=kwargs, version='v2')
        return new_get_sleep_response(response)

    def get_sleep_summary(self, **kwargs) -> GetSleepSummaryResponse:
        """Get sleep summary."""
        response = self.request(
            'sleep',
            'getsummary',
            params=kwargs,
            version='v2'
        )

        return new_get_sleep_summary_response(response)

    def subscribe(self, callback_url, comment, **kwargs):
        """Subscribe an application."""
        params = {'callbackurl': callback_url, 'comment': comment}
        params.update(kwargs)
        self.request('notify', 'subscribe', params)

    def unsubscribe(self, callback_url, **kwargs):
        """Unsubscribe an application."""
        params = {'callbackurl': callback_url}
        params.update(kwargs)
        self.request('notify', 'revoke', params)

    def is_subscribed(self, callback_url, appli=1):
        """Return true if withings profile has a subscription."""
        params = {'callbackurl': callback_url, 'appli': appli}
        try:
            self.request('notify', 'get', params)
            return True
        except requests.exceptions.RequestException:
            return False

    def list_subscriptions(self, appli=1) -> ListSubscriptionsResponse:
        """List current subscriptions from withings profile."""
        response = self.request('notify', 'list', {'appli': appli})
        return new_list_subscription_response(response)
