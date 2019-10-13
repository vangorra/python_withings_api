"""
Python library for the Withings Health API.

Withings Health API
<https://developer.health.withings.com/api>
"""

from __future__ import unicode_literals

import json
from typing import Callable, Union, Any, Iterable, Dict
import datetime
from types import LambdaType

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
    MeasureType,
    MeasureCategory,
    ListSubscriptionsResponse,
    Credentials,
    GetActivityField,
    GetSleepField,
    GetSleepSummaryField,
    AuthScope,
)

DateType = Union[arrow.Arrow, datetime.date, datetime.datetime, int, str]


def update_params(
        params: dict,
        name: str,
        current_value: Any,
        new_value: Any = None
):
    """Add a conditional param to a params dict."""
    if current_value is None:
        return

    if isinstance(new_value, LambdaType):
        params[name] = new_value(current_value)
    else:
        params[name] = new_value or current_value


class WithingsAuth:
    """Handles management of oauth2 authorization calls."""

    URL = 'https://account.withings.com'

    def __init__(
            self,
            client_id: str,
            consumer_secret: str,
            callback_uri: str = None,
            scope: Iterable[AuthScope] = tuple(),
            mode: str = 'demo'
    ):
        """Initialize new object."""
        self._client_id = client_id
        self._consumer_secret = consumer_secret
        self._callback_uri = callback_uri
        self._scope = scope
        self._mode = mode
        self._session = OAuth2Session(
            self._client_id,
            redirect_uri=self._callback_uri,
            scope=','.join((scope.value for scope in self._scope))
        )

    def get_authorize_url(self) -> str:
        """Generate the authorize url."""
        url = self._session.authorization_url(
            '%s/oauth2_user/authorize2' % self.URL
        )[0]

        if self._mode:
            url = url + '&mode=' + self._mode

        return url

    def get_credentials(self, code) -> Credentials:
        """Get the oauth credentials."""
        response = self._session.fetch_token(
            '%s/oauth2/token' % self.URL,
            code=code,
            client_secret=self._consumer_secret,
            include_client_id=True
        )

        return new_credentials(
            self._client_id,
            self._consumer_secret,
            response
        )


class WithingsApi:
    """
    Provides entrypoint for calling the withings api.

    While withings-api takes care of automatically refreshing the OAuth2
    token so you can seamlessly continue making API calls, it is important
    that you persist the updated tokens somewhere associated with the user,
    such as a database table. That way when your application restarts it will
    have the updated tokens to start with. Pass a ``refresh_cb`` function to
    the API constructor and we will call it with the updated token when it gets
    refreshed.

    class WithingsUser:
        def refresh_cb(self, creds):
            my_savefn(creds)

    user = ...
    creds = ...
    api = WithingsApi(creds, refresh_cb=user.refresh_cb)
    """

    URL = 'https://wbsapi.withings.net'

    def __init__(
            self,
            credentials: Credentials,
            refresh_cb: Callable[[Credentials], None] = None
    ):
        """Initialize new object."""
        self._credentials = credentials
        self._refresh_cb = refresh_cb
        token = {
            'access_token': credentials.access_token,
            'refresh_token': credentials.refresh_token,
            'token_type': credentials.token_type,
            'expires_in': str(
                int(credentials.token_expiry) - arrow.utcnow().timestamp
            ),
        }

        self._client = OAuth2Session(
            credentials.client_id,
            token=token,
            client=WebApplicationClient(
                credentials.client_id,
                token=token,
                default_token_placement='query'
            ),
            auto_refresh_url='{}/oauth2/token'.format(WithingsAuth.URL),
            auto_refresh_kwargs={
                'client_id': credentials.client_id,
                'client_secret': credentials.consumer_secret,
            },
            token_updater=self._update_token
        )

    def get_credentials(self) -> Credentials:
        """Get the current oauth credentials."""
        return self._credentials

    def _update_token(self, token):
        """Set the oauth token."""
        self._credentials = Credentials(
            access_token=token.get('access_token'),
            token_expiry=arrow.utcnow().timestamp + token.get('expires_in'),
            token_type=self._credentials.token_type,
            refresh_token=token.get('refresh_token'),
            user_id=self._credentials.user_id,
            client_id=self._credentials.client_id,
            consumer_secret=self._credentials.consumer_secret,
        )

        if self._refresh_cb:
            self._refresh_cb(self._credentials)

    def request(
            self,
            path: str,
            params: Dict[str, Any],
            method='GET'
    ):
        """Request a specific service."""
        params = (params or {}).copy()
        params['userid'] = self._credentials.user_id
        response = self._client.request(
            method=method,
            url='%s/%s' % (self.URL.strip('/'), path.strip('/')),
            params=params
        )
        parsed_response = json.loads(response.content.decode())
        if parsed_response['status'] != 0:
            raise requests.exceptions.RequestException(
                "Error code %s" % parsed_response['status'],
                response=response
            )
        return parsed_response.get('body', None)

    def get_activity(
            self,
            startdateymd: DateType = None,
            enddateymd: DateType = None,
            offset: int = None,
            data_fields: Iterable[GetActivityField] = None,
            lastupdate: DateType = None
    ) -> GetActivityResponse:
        """Get user created activities."""
        params = {}  # type: Dict[str, Any]

        update_params(
            params,
            'startdateymd',
            startdateymd,
            lambda val: arrow.get(val).format('YYYY-MM-DD')
        )
        update_params(
            params,
            'enddateymd',
            enddateymd,
            lambda val: arrow.get(val).format('YYYY-MM-DD')
        )
        update_params(
            params,
            'offset',
            offset
        )
        update_params(
            params,
            'data_fields',
            data_fields,
            lambda fields: ','.join([field.value for field in fields])
        )
        update_params(
            params,
            'lastupdate',
            lastupdate,
            lambda val: arrow.get(val).timestamp
        )
        update_params(
            params,
            'action',
            'getactivity'
        )

        return new_get_activity_response(
            self.request(
                path='v2/measure',
                params=params
            )
        )

    def get_meas(
            self,
            meastype: MeasureType = None,
            category: MeasureCategory = None,
            startdate: DateType = None,
            enddate: DateType = None,
            offset: int = None,
            lastupdate: DateType = None
    ) -> GetMeasResponse:
        """Get measures."""
        params = {}  # type: Dict[str, Any]

        update_params(
            params,
            'meastype',
            meastype,
            lambda val: val.value
        )
        update_params(
            params,
            'category',
            category,
            lambda val: val.value
        )
        update_params(
            params,
            'startdate',
            startdate,
            lambda val: arrow.get(val).timestamp
        )
        update_params(
            params,
            'enddate',
            enddate,
            lambda val: arrow.get(val).timestamp
        )
        update_params(params, 'offset', offset)
        update_params(
            params,
            'lastupdate',
            lastupdate,
            lambda val: arrow.get(val).timestamp
        )
        update_params(
            params,
            'action',
            'getmeas'
        )

        return new_get_meas_response(
            self.request(
                path='measure',
                params=params
            )
        )

    def get_sleep(
            self,
            startdate: DateType = None,
            enddate: DateType = None,
            data_fields: Iterable[GetSleepField] = None
    ) -> GetSleepResponse:
        """Get sleep data."""
        params = {}  # type: Dict[str, Any]

        update_params(
            params,
            'startdate',
            startdate,
            lambda val: arrow.get(val).timestamp
        )
        update_params(
            params,
            'enddate',
            enddate,
            lambda val: arrow.get(val).timestamp
        )
        update_params(
            params,
            'data_fields',
            data_fields,
            lambda fields: ','.join([field.value for field in fields])
        )
        update_params(
            params,
            'action',
            'get'
        )

        return new_get_sleep_response(
            self.request(
                path='v2/sleep',
                params=params
            )
        )

    def get_sleep_summary(
            self,
            startdateymd: DateType = None,
            enddateymd: DateType = None,
            data_fields: Iterable[GetSleepSummaryField] = None,
            lastupdate: DateType = None
    ) -> GetSleepSummaryResponse:
        """Get sleep summary."""
        params = {}  # type: Dict[str, Any]

        update_params(
            params,
            'startdateymd',
            startdateymd,
            lambda val: arrow.get(val).format('YYYY-MM-DD')
        )
        update_params(
            params,
            'enddateymd',
            enddateymd,
            lambda val: arrow.get(val).format('YYYY-MM-DD')
        )
        update_params(
            params,
            'data_fields',
            data_fields,
            lambda fields: ','.join([field.value for field in fields])
        )
        update_params(
            params,
            'lastupdate',
            lastupdate,
            lambda val: arrow.get(val).timestamp
        )
        update_params(
            params,
            'action',
            'getsummary'
        )

        return new_get_sleep_summary_response(
            self.request(
                path='v2/sleep',
                params=params
            )
        )

    def subscribe(self, callback_url, comment, **kwargs):
        """Subscribe an application."""
        params = {
            'action': 'subscribe',
            'callbackurl': callback_url,
            'comment': comment,
        }
        params.update(kwargs)
        self.request(path='notify', params=params)

    def unsubscribe(self, callback_url, **kwargs):
        """Unsubscribe an application."""
        params = {'action': 'revoke', 'callbackurl': callback_url}
        params.update(kwargs)
        self.request(path='notify', params=params)

    def is_subscribed(self, callback_url, appli=1):
        """Return true if withings profile has a subscription."""
        for profile in self.list_subscriptions(appli=appli).profiles:
            if profile.callbackurl == callback_url:
                return True

        return False

    def list_subscriptions(self, appli=1) -> ListSubscriptionsResponse:
        """List current subscriptions from withings profile."""
        response = self.request(
            path='notify',
            params={'action': 'list', 'appli': appli}
        )
        return new_list_subscription_response(response)
