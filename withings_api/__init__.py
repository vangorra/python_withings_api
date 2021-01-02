"""
Python library for the Withings Health API.

Withings Health API
<https://developer.health.withings.com/api>
"""
from abc import abstractmethod
import datetime
from types import LambdaType
from typing import Any, Callable, Dict, Iterable, Optional, Union, cast

import arrow
from oauthlib.oauth2 import WebApplicationClient
from requests_oauthlib import OAuth2Session
from typing_extensions import Final

from .common import (
    AuthScope,
    Credentials2,
    CredentialsType,
    GetActivityField,
    GetSleepField,
    GetSleepSummaryField,
    HeartGetResponse,
    HeartListResponse,
    MeasureGetActivityResponse,
    MeasureGetMeasGroupCategory,
    MeasureGetMeasResponse,
    MeasureType,
    NotifyAppli,
    NotifyGetResponse,
    NotifyListResponse,
    SleepGetResponse,
    SleepGetSummaryResponse,
    UserGetDeviceResponse,
    maybe_upgrade_credentials,
    response_body_or_raise,
)

DateType = Union[arrow.Arrow, datetime.date, datetime.datetime, int, str]
ParamsType = Dict[str, Union[str, int, bool]]


def update_params(
    params: ParamsType, name: str, current_value: Any, new_value: Any = None
) -> None:
    """Add a conditional param to a params dict."""
    if current_value is None:
        return

    if isinstance(new_value, LambdaType):
        params[name] = new_value(current_value)
    else:
        params[name] = new_value or current_value


class AbstractWithingsApi:
    """Abstract class for customizing which requests module you want."""

    URL: Final = "https://wbsapi.withings.net"
    PATH_V2_USER: Final = "v2/user"
    PATH_V2_MEASURE: Final = "v2/measure"
    PATH_MEASURE: Final = "measure"
    PATH_V2_SLEEP: Final = "v2/sleep"
    PATH_NOTIFY: Final = "notify"
    PATH_V2_HEART: Final = "v2/heart"

    @abstractmethod
    def _request(
        self, path: str, params: Dict[str, Any], method: str = "GET"
    ) -> Dict[str, Any]:
        """Fetch data from the Withings API."""

    def request(
        self, path: str, params: Dict[str, Any], method: str = "GET"
    ) -> Dict[str, Any]:
        """Request a specific service."""
        return response_body_or_raise(
            self._request(method=method, path=path, params=params)
        )

    def user_get_device(self) -> UserGetDeviceResponse:
        """
        Get user device.

        Some data related to user profile are available through those services.
        """
        return UserGetDeviceResponse(
            **self.request(path=self.PATH_V2_USER, params={"action": "getdevice"})
        )

    def measure_get_activity(
        self,
        data_fields: Iterable[GetActivityField] = GetActivityField,
        startdateymd: Optional[DateType] = None,
        enddateymd: Optional[DateType] = None,
        offset: Optional[int] = None,
        lastupdate: Optional[DateType] = None,
    ) -> MeasureGetActivityResponse:
        """Get user created activities."""
        params: Final[ParamsType] = {}

        update_params(
            params,
            "startdateymd",
            startdateymd,
            lambda val: arrow.get(val).format("YYYY-MM-DD"),
        )
        update_params(
            params,
            "enddateymd",
            enddateymd,
            lambda val: arrow.get(val).format("YYYY-MM-DD"),
        )
        update_params(params, "offset", offset)
        update_params(
            params,
            "data_fields",
            data_fields,
            lambda fields: ",".join([field.value for field in fields]),
        )
        update_params(
            params, "lastupdate", lastupdate, lambda val: arrow.get(val).timestamp
        )
        update_params(params, "action", "getactivity")

        return MeasureGetActivityResponse(
            **self.request(path=self.PATH_V2_MEASURE, params=params)
        )

    def measure_get_meas(
        self,
        meastype: Optional[MeasureType] = None,
        category: Optional[MeasureGetMeasGroupCategory] = None,
        startdate: Optional[DateType] = None,
        enddate: Optional[DateType] = None,
        offset: Optional[int] = None,
        lastupdate: Optional[DateType] = None,
    ) -> MeasureGetMeasResponse:
        """Get measures."""
        params: Final[ParamsType] = {}

        update_params(params, "meastype", meastype, lambda val: val.value)
        update_params(params, "category", category, lambda val: val.value)
        update_params(
            params, "startdate", startdate, lambda val: arrow.get(val).timestamp
        )
        update_params(params, "enddate", enddate, lambda val: arrow.get(val).timestamp)
        update_params(params, "offset", offset)
        update_params(
            params, "lastupdate", lastupdate, lambda val: arrow.get(val).timestamp
        )
        update_params(params, "action", "getmeas")

        return MeasureGetMeasResponse(
            **self.request(path=self.PATH_MEASURE, params=params)
        )

    def sleep_get(
        self,
        data_fields: Iterable[GetSleepField],
        startdate: Optional[DateType] = None,
        enddate: Optional[DateType] = None,
    ) -> SleepGetResponse:
        """Get sleep data."""
        params: Final[ParamsType] = {}

        update_params(
            params, "startdate", startdate, lambda val: arrow.get(val).timestamp
        )
        update_params(params, "enddate", enddate, lambda val: arrow.get(val).timestamp)
        update_params(
            params,
            "data_fields",
            data_fields,
            lambda fields: ",".join([field.value for field in fields]),
        )
        update_params(params, "action", "get")

        return SleepGetResponse(**self.request(path=self.PATH_V2_SLEEP, params=params))

    def sleep_get_summary(
        self,
        data_fields: Iterable[GetSleepSummaryField],
        startdateymd: Optional[DateType] = None,
        enddateymd: Optional[DateType] = None,
        offset: Optional[int] = None,
        lastupdate: Optional[DateType] = None,
    ) -> SleepGetSummaryResponse:
        """Get sleep summary."""
        params: Final[ParamsType] = {}

        update_params(
            params,
            "startdateymd",
            startdateymd,
            lambda val: arrow.get(val).format("YYYY-MM-DD"),
        )
        update_params(
            params,
            "enddateymd",
            enddateymd,
            lambda val: arrow.get(val).format("YYYY-MM-DD"),
        )
        update_params(
            params,
            "data_fields",
            data_fields,
            lambda fields: ",".join([field.value for field in fields]),
        )
        update_params(params, "offset", offset)
        update_params(
            params, "lastupdate", lastupdate, lambda val: arrow.get(val).timestamp
        )
        update_params(params, "action", "getsummary")

        return SleepGetSummaryResponse(
            **self.request(path=self.PATH_V2_SLEEP, params=params)
        )

    def heart_get(self, signalid: int) -> HeartGetResponse:
        """Get ECG recording."""
        params: Final[ParamsType] = {}

        update_params(params, "signalid", signalid)
        update_params(params, "action", "get")

        return HeartGetResponse(**self.request(path=self.PATH_V2_HEART, params=params))

    def heart_list(
        self,
        startdate: Optional[DateType] = None,
        enddate: Optional[DateType] = None,
        offset: Optional[int] = None,
    ) -> HeartListResponse:
        """Get heart list."""
        params: Final[ParamsType] = {}

        update_params(
            params, "startdate", startdate, lambda val: arrow.get(val).timestamp,
        )
        update_params(
            params, "enddate", enddate, lambda val: arrow.get(val).timestamp,
        )
        update_params(params, "offset", offset)
        update_params(params, "action", "list")

        return HeartListResponse(**self.request(path=self.PATH_V2_HEART, params=params))

    def notify_get(
        self, callbackurl: str, appli: Optional[NotifyAppli] = None
    ) -> NotifyGetResponse:
        """
        Get subscription.

        Return the last notification service that a user was subscribed to,
        and its expiry date.
        """
        params: Final[ParamsType] = {}

        update_params(params, "callbackurl", callbackurl)
        update_params(params, "appli", appli, lambda appli: appli.value)
        update_params(params, "action", "get")

        return NotifyGetResponse(**self.request(path=self.PATH_NOTIFY, params=params))

    def notify_list(self, appli: Optional[NotifyAppli] = None) -> NotifyListResponse:
        """List notification configuration for this user."""
        params: Final[ParamsType] = {}

        update_params(params, "appli", appli, lambda appli: appli.value)
        update_params(params, "action", "list")

        return NotifyListResponse(**self.request(path=self.PATH_NOTIFY, params=params))

    def notify_revoke(
        self, callbackurl: Optional[str] = None, appli: Optional[NotifyAppli] = None
    ) -> None:
        """
        Revoke a subscription.

        This service disables the notification between the API and the
        specified applications for the user.
        """
        params: Final[ParamsType] = {}

        update_params(params, "callbackurl", callbackurl)
        update_params(params, "appli", appli, lambda appli: appli.value)
        update_params(params, "action", "revoke")

        self.request(path=self.PATH_NOTIFY, params=params)

    def notify_subscribe(
        self,
        callbackurl: str,
        appli: Optional[NotifyAppli] = None,
        comment: Optional[str] = None,
    ) -> None:
        """Subscribe to receive notifications when new data is available."""
        params: Final[ParamsType] = {}

        update_params(params, "callbackurl", callbackurl)
        update_params(params, "appli", appli, lambda appli: appli.value)
        update_params(params, "comment", comment)
        update_params(params, "action", "subscribe")

        self.request(path=self.PATH_NOTIFY, params=params)

    def notify_update(
        self,
        callbackurl: str,
        appli: NotifyAppli,
        new_callbackurl: str,
        new_appli: Optional[NotifyAppli] = None,
        comment: Optional[str] = None,
    ) -> None:
        """Update the callbackurl and or appli of a created notification."""
        params: Final[ParamsType] = {}

        update_params(params, "callbackurl", callbackurl)
        update_params(params, "appli", appli, lambda appli: appli.value)
        update_params(params, "new_callbackurl", new_callbackurl)
        update_params(params, "new_appli", new_appli, lambda new_appli: new_appli.value)
        update_params(params, "comment", comment)
        update_params(params, "action", "update")

        self.request(path=self.PATH_NOTIFY, params=params)


class WithingsAuth:
    """Handles management of oauth2 authorization calls."""

    URL: Final = "https://account.withings.com"
    PATH_AUTHORIZE: Final = "oauth2_user/authorize2"
    PATH_TOKEN: Final = "oauth2/token"  # nosec

    def __init__(
        self,
        client_id: str,
        consumer_secret: str,
        callback_uri: str,
        scope: Iterable[AuthScope] = tuple(),
        mode: Optional[str] = None,
    ):
        """Initialize new object."""
        self._client_id: Final = client_id
        self._consumer_secret: Final = consumer_secret
        self._callback_uri: Final = callback_uri
        self._scope: Final = scope
        self._mode: Final = mode
        self._session: Final = OAuth2Session(
            self._client_id,
            redirect_uri=self._callback_uri,
            scope=",".join((scope.value for scope in self._scope)),
        )

    def get_authorize_url(self) -> str:
        """Generate the authorize url."""
        url: Final = str(
            self._session.authorization_url("%s/%s" % (self.URL, self.PATH_AUTHORIZE))[
                0
            ]
        )

        if self._mode:
            return url + "&mode=" + self._mode

        return url

    def get_credentials(self, code: str) -> Credentials2:
        """Get the oauth credentials."""
        response: Final = self._session.fetch_token(
            "%s/%s" % (self.URL, self.PATH_TOKEN),
            code=code,
            client_secret=self._consumer_secret,
            include_client_id=True,
        )

        return Credentials2(
            **{
                **response,
                **dict(
                    client_id=self._client_id, consumer_secret=self._consumer_secret
                ),
            }
        )


class WithingsApi(AbstractWithingsApi):
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

    def __init__(
        self,
        credentials: CredentialsType,
        refresh_cb: Optional[Callable[[Credentials2], None]] = None,
    ):
        """Initialize new object."""
        self._credentials = maybe_upgrade_credentials(credentials)
        self._refresh_cb: Final = refresh_cb or self._blank_refresh_cb
        token: Final = {
            "access_token": self._credentials.access_token,
            "refresh_token": self._credentials.refresh_token,
            "token_type": self._credentials.token_type,
            "expires_in": self._credentials.expires_in,
        }

        self._client: Final = OAuth2Session(
            self._credentials.client_id,
            token=token,
            client=WebApplicationClient(  # nosec
                self._credentials.client_id,
                token=token,
                default_token_placement="query",
            ),
            auto_refresh_url="%s/%s" % (WithingsAuth.URL, WithingsAuth.PATH_TOKEN),
            auto_refresh_kwargs={
                "action": "requesttoken",
                "client_id": self._credentials.client_id,
                "client_secret": self._credentials.consumer_secret,
            },
            token_updater=self._update_token,
        )

    def _blank_refresh_cb(self, creds: Credentials2) -> None:
        """The default callback which does nothing."""

    def get_credentials(self) -> Credentials2:
        """Get the current oauth credentials."""
        return self._credentials

    def refresh_token(self) -> None:
        """Manually refresh the token."""
        token_dict: Final = self._client.refresh_token(
            token_url=self._client.auto_refresh_url
        )
        self._update_token(token=token_dict)

    def _update_token(self, token: Dict[str, Union[str, int]]) -> None:
        """Set the oauth token."""
        self._credentials = Credentials2(
            access_token=token["access_token"],
            expires_in=token["expires_in"],
            token_type=self._credentials.token_type,
            refresh_token=token["refresh_token"],
            userid=self._credentials.userid,
            client_id=self._credentials.client_id,
            consumer_secret=self._credentials.consumer_secret,
        )

        self._refresh_cb(self._credentials)

    def _request(
        self, path: str, params: Dict[str, Any], method: str = "GET"
    ) -> Dict[str, Any]:
        return cast(
            Dict[str, Any],
            self._client.request(
                method=method,
                url="%s/%s" % (self.URL.strip("/"), path.strip("/")),
                params=params,
            ).json(),
        )
