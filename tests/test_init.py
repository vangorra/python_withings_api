from unittest.mock import MagicMock
import datetime
import re
from urllib import parse

from .common import TIMEZONE0, TIMEZONE_STR0, TIMEZONE1, TIMEZONE_STR1

import arrow
import pytest
import requests
import responses
from withings_api import (
    WithingsApi,
    WithingsAuth,
)

from withings_api.common import (
    SleepState,
    SleepModel,
    MeasureGetActivityResponse,
    MeasureGetActivityActivity,
    SleepGetResponse,
    SleepGetSerie,
    SleepGetSummaryResponse,
    GetSleepSummarySerie,
    GetSleepSummaryData,
    GetSleepSummaryField,
    MeasureGetMeasResponse,
    MeasureGetMeasGroup,
    SleepGetTimestamp,
    MeasureGetMeasMeasure,
    MeasureType,
    MeasureGetMeasGroupAttrib,
    MeasureGetMeasGroupCategory,
    NotifyListResponse,
    NotifyListProfile,
    NotifyAppli,
    Credentials,
    GetActivityField,
    GetSleepField,
    AuthScope,
    NotifyGetResponse,
    UserGetDeviceResponse,
    UserGetDeviceDevice,
)


@pytest.fixture()
def withings_api() -> WithingsApi:
    client_id = 'my_client_id'
    consumer_secret = 'my_consumer_secret'
    credentials = Credentials(
        access_token='my_access_token',
        token_expiry=arrow.utcnow().timestamp + 10000,
        token_type='Bearer',
        refresh_token='my_refresh_token',
        userid='my_userid',
        client_id=client_id,
        consumer_secret=consumer_secret,
    )

    return WithingsApi(credentials)


@responses.activate
def test_authorize() -> None:
    client_id = 'fake_client_id'
    consumer_secret = 'fake_consumer_secret'
    callback_uri = 'http://127.0.0.1:8080'
    arrow.utcnow = MagicMock(return_value=arrow.get(100000000))

    responses.add(
        method=responses.POST,
        url='https://account.withings.com/oauth2/token',
        json={
            'access_token': 'fake_access_token',
            'expires_in': 11,
            'token_type': 'Bearer',
            'refresh_token': 'fake_refresh_token',
            'userid': 'fake_userid',
        },
        status=200
    )

    auth = WithingsAuth(
        client_id,
        consumer_secret,
        callback_uri=callback_uri,
        scope=(
            AuthScope.USER_METRICS,
            AuthScope.USER_ACTIVITY,
        )
    )

    url = auth.get_authorize_url()

    assert url.startswith(
        'https://account.withings.com/oauth2_user/authorize2'
    )

    assert_url_query_contains(url, {
        'response_type': 'code',
        'client_id': 'fake_client_id',
        'redirect_uri': 'http://127.0.0.1:8080',
        'scope': 'user.metrics,user.activity',
    })

    params = dict(parse.parse_qsl(parse.urlsplit(url).query))
    assert 'scope' in params
    assert len(params['scope']) > 0

    creds = auth.get_credentials('FAKE_CODE')

    assert creds == Credentials(
        access_token='fake_access_token',
        token_expiry=100000011,
        token_type='Bearer',
        refresh_token='fake_refresh_token',
        userid='fake_userid',
        client_id=client_id,
        consumer_secret=consumer_secret,
    )


@responses.activate
def test_request_exception(withings_api: WithingsApi) -> None:
    responses.add(
        method=responses.GET,
        url=re.compile('https://wbsapi.withings.net/.*'),
        status=200,
        json={
            'status': 100,
            'body': {}
        }
    )

    with pytest.raises(requests.exceptions.RequestException):
        withings_api.measure_get_meas()


@responses.activate
def test_refresh_token() -> None:
    client_id = 'my_client_id'
    consumer_secret = 'my_consumer_secret'

    credentials = Credentials(
        access_token='my_access_token,_old',
        token_expiry=arrow.utcnow().timestamp - 1,
        token_type='Bearer',
        refresh_token='my_refresh_token_old',
        userid='my_userid',
        client_id=client_id,
        consumer_secret=consumer_secret,
    )

    responses.add(
        method=responses.POST,
        url=re.compile('https://account.withings.com/oauth2/token.*'),
        status=200,
        json={
            'access_token': 'my_access_token',
            'expires_in': 11,
            'token_type': 'Bearer',
            'refresh_token': 'my_refresh_token',
            'userid': 'my_userid',
        }
    )

    responses_add_measure_get_activity()

    refresh_callback = MagicMock()
    api = WithingsApi(credentials, refresh_callback)
    api.measure_get_activity()

    refresh_callback.assert_called_with(api.get_credentials())
    new_credentials = api.get_credentials()
    assert new_credentials.access_token == 'my_access_token'
    assert new_credentials.refresh_token == 'my_refresh_token'
    assert new_credentials.token_expiry > credentials.token_expiry


def responses_add_user_get_device() -> None:
    responses.add(
        method=responses.GET,
        url=re.compile(
            'https://wbsapi.withings.net/v2/user?.*action=getdevice(&.*)?'
        ),
        status=200,
        json={
            'status': 0,
            'body': {
                'devices': [
                    {
                        'type': 'type0',
                        'model': 'model0',
                        'battery': 'battery0',
                        'deviceid': 'deviceid0',
                        'timezone': TIMEZONE_STR0,
                    },
                    {
                        'type': 'type1',
                        'model': 'model1',
                        'battery': 'battery1',
                        'deviceid': 'deviceid1',
                        'timezone': TIMEZONE_STR1,
                    }
                ]
            }
         }
    )


@responses.activate
def test_user_get_device(withings_api: WithingsApi) -> None:
    responses_add_user_get_device()
    assert withings_api.user_get_device() == UserGetDeviceResponse(
        devices=(
            UserGetDeviceDevice(
                type='type0',
                model='model0',
                battery='battery0',
                deviceid='deviceid0',
                timezone=TIMEZONE0,
            ),
            UserGetDeviceDevice(
                type='type1',
                model='model1',
                battery='battery1',
                deviceid='deviceid1',
                timezone=TIMEZONE1,
            )
        )
    )

    assert_url_path(
        responses.calls[0].request.url,
        '/v2/user'
    )
    assert_url_query_contains(
        responses.calls[0].request.url,
        {
            'action': 'getdevice',
        }
    )


def responses_add_measure_get_activity() -> None:
    responses.add(
        method=responses.GET,
        url=re.compile(
            'https://wbsapi.withings.net/v2/measure?.*action=getactivity(&.*)?'
        ),
        status=200,
        json={
            'status': 0,
            'body': {
                'more': False,
                'offset': 0,
                'activities': [
                    {
                        'date': '2019-01-01',
                        'timezone': TIMEZONE_STR0,
                        'is_tracker': True,
                        'deviceid': 'dev1',
                        'brand': 100,
                        'steps': 101,
                        'distance': 102,
                        'elevation': 103,
                        'soft': 104,
                        'moderate': 105,
                        'intense': 106,
                        'active': 107,
                        'calories': 108,
                        'totalcalories': 109,
                        'hr_average': 110,
                        'hr_min': 111,
                        'hr_max': 112,
                        'hr_zone_0': 113,
                        'hr_zone_1': 114,
                        'hr_zone_2': 115,
                        'hr_zone_3': 116,
                    },
                    {
                        'date': '2019-01-02',
                        'timezone': TIMEZONE_STR1,
                        'is_tracker': False,
                        'deviceid': 'dev2',
                        'brand': 200,
                        'steps': 201,
                        'distance': 202,
                        'elevation': 203,
                        'soft': 204,
                        'moderate': 205,
                        'intense': 206,
                        'active': 207,
                        'calories': 208,
                        'totalcalories': 209,
                        'hr_average': 210,
                        'hr_min': 211,
                        'hr_max': 212,
                        'hr_zone_0': 213,
                        'hr_zone_1': 214,
                        'hr_zone_2': 215,
                        'hr_zone_3': 216,
                    },
                ],
            },
        }
    )


@responses.activate
def test_measure_get_activity(withings_api: WithingsApi) -> None:
    responses_add_measure_get_activity()
    assert withings_api.measure_get_activity() == MeasureGetActivityResponse(
        more=False,
        offset=0,
        activities=(
            MeasureGetActivityActivity(
                date=arrow.get('2019-01-01').replace(tzinfo=TIMEZONE0),
                timezone=TIMEZONE0,
                is_tracker=True,
                deviceid='dev1',
                brand=100,
                steps=101,
                distance=102,
                elevation=103,
                soft=104,
                moderate=105,
                intense=106,
                active=107,
                calories=108,
                totalcalories=109,
                hr_average=110,
                hr_min=111,
                hr_max=112,
                hr_zone_0=113,
                hr_zone_1=114,
                hr_zone_2=115,
                hr_zone_3=116,
            ),
            MeasureGetActivityActivity(
                date=arrow.get('2019-01-02').replace(tzinfo=TIMEZONE1),
                timezone=TIMEZONE1,
                is_tracker=False,
                deviceid='dev2',
                brand=200,
                steps=201,
                distance=202,
                elevation=203,
                soft=204,
                moderate=205,
                intense=206,
                active=207,
                calories=208,
                totalcalories=209,
                hr_average=210,
                hr_min=211,
                hr_max=212,
                hr_zone_0=213,
                hr_zone_1=214,
                hr_zone_2=215,
                hr_zone_3=216,
            )
        )
    )


def responses_add_measure_get_meas() -> None:
    responses.add(
        method=responses.GET,
        url=re.compile(
            'https://wbsapi.withings.net/measure?.*action=getmeas(&.*)?'
        ),
        status=200,
        json={
            'status': 0,
            'body': {
                'more': False,
                'offset': 0,
                'updatetime': 1409596058,
                'timezone': TIMEZONE_STR0,
                'measuregrps': [
                    {
                        'attrib': MeasureGetMeasGroupAttrib
                        .MANUAL_USER_DURING_ACCOUNT_CREATION,
                        'category': MeasureGetMeasGroupCategory.REAL,
                        'created': 1111111111,
                        'date': '2019-01-01',
                        'deviceid': 'dev1',
                        'grpid': 'grp1',
                        'measures': [
                            {
                                'type': MeasureType.HEIGHT,
                                'unit': 110,
                                'value': 110,
                            },
                            {
                                'type': MeasureType.WEIGHT,
                                'unit': 120,
                                'value': 120,
                            },
                        ]
                    },
                    {
                        'attrib': MeasureGetMeasGroupAttrib
                        .DEVICE_ENTRY_FOR_USER_AMBIGUOUS,
                        'category':
                            MeasureGetMeasGroupCategory.USER_OBJECTIVES,
                        'created': 2222222222,
                        'date': '2019-01-02',
                        'deviceid': 'dev2',
                        'grpid': 'grp2',
                        'measures': [
                            {
                                'type': MeasureType.BODY_TEMPERATURE,
                                'unit': 210,
                                'value': 210,
                            },
                            {
                                'type': MeasureType.BONE_MASS,
                                'unit': 220,
                                'value': 220,
                            },
                        ],
                    },
                ],
            }
        }
    )


@responses.activate
def test_measure_get_meas(withings_api: WithingsApi) -> None:
    responses_add_measure_get_meas()
    assert withings_api.measure_get_meas() == MeasureGetMeasResponse(
        more=False,
        offset=0,
        timezone=TIMEZONE0,
        updatetime=arrow.get(1409596058).replace(tzinfo=TIMEZONE0),
        measuregrps=(
            MeasureGetMeasGroup(
                attrib=MeasureGetMeasGroupAttrib
                .MANUAL_USER_DURING_ACCOUNT_CREATION,
                category=MeasureGetMeasGroupCategory.REAL,
                created=arrow.get(1111111111).replace(tzinfo=TIMEZONE0),
                date=arrow.get('2019-01-01').replace(tzinfo=TIMEZONE0),
                deviceid='dev1',
                grpid='grp1',
                measures=(
                    MeasureGetMeasMeasure(
                        type=MeasureType.HEIGHT,
                        unit=110,
                        value=110,
                    ),
                    MeasureGetMeasMeasure(
                        type=MeasureType.WEIGHT,
                        unit=120,
                        value=120,
                    )
                ),
            ),
            MeasureGetMeasGroup(
                attrib=MeasureGetMeasGroupAttrib
                .DEVICE_ENTRY_FOR_USER_AMBIGUOUS,
                category=MeasureGetMeasGroupCategory.USER_OBJECTIVES,
                created=arrow.get(2222222222).replace(tzinfo=TIMEZONE0),
                date=arrow.get('2019-01-02').replace(tzinfo=TIMEZONE0),
                deviceid='dev2',
                grpid='grp2',
                measures=(
                    MeasureGetMeasMeasure(
                        type=MeasureType.BODY_TEMPERATURE,
                        unit=210,
                        value=210,
                    ),
                    MeasureGetMeasMeasure(
                        type=MeasureType.BONE_MASS,
                        unit=220,
                        value=220,
                    )
                ),
            )
        )
    )


def responses_add_sleep_get() -> None:
    responses.add(
        method=responses.GET,
        url=re.compile(
            'https://wbsapi.withings.net/v2/sleep?.*action=get(&.+)?'
        ),
        status=200,
        json={
            'status': 0,
            'body': {
                "series": [
                    {
                        "startdate": 1387235398,
                        "state": SleepState.AWAKE,
                        "enddate": 1387235758
                    },
                    {
                        "startdate": 1387243618,
                        "state": SleepState.LIGHT,
                        "enddate": 1387244518,
                        "hr": {
                            "$timestamp": 123,
                        },
                        "rr": {
                            "$timestamp": 456,
                        },
                    }
                ],
                "model": SleepModel.TRACKER,
            }
        }
    )


@responses.activate
def test_sleep_get(withings_api: WithingsApi) -> None:
    responses_add_sleep_get()
    assert withings_api.sleep_get() == SleepGetResponse(
        model=SleepModel.TRACKER,
        series=(
            SleepGetSerie(
                startdate=arrow.get(1387235398),
                state=SleepState.AWAKE,
                enddate=arrow.get(1387235758),
                hr=None,
                rr=None,
            ),
            SleepGetSerie(
                startdate=arrow.get(1387243618),
                state=SleepState.LIGHT,
                enddate=arrow.get(1387244518),
                hr=SleepGetTimestamp(arrow.get(123)),
                rr=SleepGetTimestamp(arrow.get(456)),
            )
        )
    )


def responses_add_sleep_get_summary() -> None:
    responses.add(
        method=responses.GET,
        url=re.compile(
            'https://wbsapi.withings.net/v2/sleep?.*action=getsummary(&.*)?'
        ),
        status=200,
        json={
            'status': 0,
            'body': {
                'more': False,
                'offset': 1,
                'series': [
                    {
                        'data': {
                            'deepsleepduration': 110,
                            'durationtosleep': 111,
                            'durationtowakeup': 112,
                            'lightsleepduration': 113,
                            'wakeupcount': 114,
                            'wakeupduration': 116,
                            'remsleepduration': 116,
                            'hr_average': 117,
                            'hr_min': 118,
                            'hr_max': 119,
                            'rr_average': 120,
                            'rr_min': 121,
                            'rr_max': 122,
                        },
                        'date': '2018-10-30',
                        'enddate': 1540897020,
                        'id': 900363515,
                        'model': SleepModel.TRACKER,
                        'modified': 1540897246,
                        'startdate': 1540857420,
                        'timezone': TIMEZONE_STR0,
                    },
                    {
                        'data': {
                            'deepsleepduration': 210,
                            'durationtosleep': 211,
                            'durationtowakeup': 212,
                            'lightsleepduration': 213,
                            'wakeupcount': 214,
                            'wakeupduration': 216,
                            'remsleepduration': 216,
                            'hr_average': 217,
                            'hr_min': 218,
                            'hr_max': 219,
                            'rr_average': 220,
                            'rr_min': 221,
                            'rr_max': 222,
                        },
                        'date': '2018-10-31',
                        'enddate': 1540973400,
                        'id': 901269807,
                        'model': SleepModel.TRACKER,
                        'modified': 1541020749,
                        'startdate': 1540944960,
                        'timezone': TIMEZONE_STR1,
                    }
                ]
            }
        }
    )


@responses.activate
def test_sleep_get_summary(withings_api: WithingsApi) -> None:
    responses_add_sleep_get_summary()
    assert withings_api.sleep_get_summary() == SleepGetSummaryResponse(
        more=False,
        offset=1,
        series=(
            GetSleepSummarySerie(
                date=arrow.get('2018-10-30').replace(tzinfo=TIMEZONE0),
                enddate=arrow.get(1540897020).replace(tzinfo=TIMEZONE0),
                model=SleepModel.TRACKER,
                modified=arrow.get(1540897246).replace(tzinfo=TIMEZONE0),
                startdate=arrow.get(1540857420).replace(tzinfo=TIMEZONE0),
                timezone=TIMEZONE0,
                data=GetSleepSummaryData(
                    deepsleepduration=110,
                    durationtosleep=111,
                    durationtowakeup=112,
                    lightsleepduration=113,
                    wakeupcount=114,
                    wakeupduration=116,
                    remsleepduration=116,
                    hr_average=117,
                    hr_min=118,
                    hr_max=119,
                    rr_average=120,
                    rr_min=121,
                    rr_max=122,
                ),
            ),
            GetSleepSummarySerie(
                date=arrow.get('2018-10-31').replace(tzinfo=TIMEZONE1),
                enddate=arrow.get(1540973400).replace(tzinfo=TIMEZONE1),
                model=SleepModel.TRACKER,
                modified=arrow.get(1541020749).replace(tzinfo=TIMEZONE1),
                startdate=arrow.get(1540944960).replace(tzinfo=TIMEZONE1),
                timezone=TIMEZONE1,
                data=GetSleepSummaryData(
                    deepsleepduration=210,
                    durationtosleep=211,
                    durationtowakeup=212,
                    lightsleepduration=213,
                    wakeupcount=214,
                    wakeupduration=216,
                    remsleepduration=216,
                    hr_average=217,
                    hr_min=218,
                    hr_max=219,
                    rr_average=220,
                    rr_min=221,
                    rr_max=222,
                ),
            ),
        )
    )


def responses_add_notify_get() -> None:
    responses.add(
        method=responses.GET,
        url=re.compile(
            'https://wbsapi.withings.net/notify?.*action=get(&.*)?'
        ),
        status=200,
        json={
            'status': 0,
            'body': {
                'callbackurl': 'http://localhost/callback',
                'appli': NotifyAppli.ACTIVITY.real,
                'comment': 'comment1',
            },
        }
    )


@responses.activate
def test_notify_get(withings_api: WithingsApi) -> None:
    responses_add_notify_get()

    response = withings_api.notify_get(
        callbackurl='http://localhost/callback',
    )
    assert response == NotifyGetResponse(
        callbackurl='http://localhost/callback',
        appli=NotifyAppli.ACTIVITY,
        comment='comment1',
    )


def responses_add_notify_list() -> None:
    responses.add(
        method=responses.GET,
        url=re.compile(
            'https://wbsapi.withings.net/notify?.*action=list(&.*)?'
        ),
        status=200,
        json={
            'status': 0,
            'body': {
                'profiles': [
                    {
                        'appli': NotifyAppli.WEIGHT.real,
                        'callbackurl': 'http://localhost/callback',
                        'comment': 'fake_comment1',
                        'expires': '2019-09-01',
                    },
                    {
                        'appli': NotifyAppli.CIRCULATORY.real,
                        'callbackurl': 'http://localhost/callback2',
                        'comment': 'fake_comment2',
                        'expires': '2019-09-02',
                    },
                ]
            }
        }
    )


@responses.activate
def test_notify_list(withings_api: WithingsApi) -> None:
    responses_add_notify_list()

    assert withings_api.notify_list() == NotifyListResponse(
        profiles=(
            NotifyListProfile(
                appli=NotifyAppli.WEIGHT,
                callbackurl='http://localhost/callback',
                comment='fake_comment1',
                expires=arrow.get('2019-09-01')
            ),
            NotifyListProfile(
                appli=NotifyAppli.CIRCULATORY,
                callbackurl='http://localhost/callback2',
                comment='fake_comment2',
                expires=arrow.get('2019-09-02')
            ),
        ),
    )

    assert_url_path(
        responses.calls[0].request.url,
        '/notify'
    )
    assert_url_query_contains(
        responses.calls[0].request.url,
        {
            'action': 'list',
        }
    )


@responses.activate
def test_notify_get_params(withings_api: WithingsApi) -> None:
    responses_add_notify_get()
    withings_api.notify_get(
        callbackurl='http://localhost/callback2',
        appli=NotifyAppli.CIRCULATORY
    )

    assert_url_query_contains(
        responses.calls[0].request.url,
        {
            'callbackurl': 'http://localhost/callback2',
            'appli': str(NotifyAppli.CIRCULATORY.real),
        }
    )

    assert_url_path(
        responses.calls[0].request.url,
        '/notify'
    )
    assert_url_query_contains(
        responses.calls[0].request.url,
        {
            'action': 'get',
        }
    )


@responses.activate
def test_notify_list_params(withings_api: WithingsApi) -> None:
    responses_add_notify_list()
    withings_api.notify_list(
        appli=NotifyAppli.CIRCULATORY
    )

    assert_url_query_contains(
        responses.calls[0].request.url,
        {
            'appli': str(NotifyAppli.CIRCULATORY.real),
        }
    )

    assert_url_path(
        responses.calls[0].request.url,
        '/notify'
    )
    assert_url_query_contains(
        responses.calls[0].request.url,
        {
            'action': 'list',
        }
    )


def responses_add_notify_revoke() -> None:
    responses.add(
        method=responses.GET,
        url=re.compile(
            'https://wbsapi.withings.net/notify?.*action=revoke(&.*)?'
        ),
        status=200,
        json={
            'status': 0,
            'body': {}
        }
    )


@responses.activate
def test_notify_revoke_params(withings_api: WithingsApi) -> None:
    responses_add_notify_revoke()
    withings_api.notify_revoke(
        appli=NotifyAppli.CIRCULATORY
    )

    assert_url_query_contains(
        responses.calls[0].request.url,
        {
            'appli': str(NotifyAppli.CIRCULATORY.real),
        }
    )

    assert_url_path(
        responses.calls[0].request.url,
        '/notify'
    )
    assert_url_query_contains(
        responses.calls[0].request.url,
        {
            'action': 'revoke',
        }
    )


def responses_add_notify_subscribe() -> None:
    responses.add(
        method=responses.GET,
        url=re.compile(
            'https://wbsapi.withings.net/notify?.*action=subscribe(&.*)?'
        ),
        status=200,
        json={
            'status': 0,
            'body': {},
        }
    )


@responses.activate
def test_notify_subscribe_params(withings_api: WithingsApi) -> None:
    responses_add_notify_subscribe()
    withings_api.notify_subscribe(
        callbackurl='http://localhost/callback2',
        appli=NotifyAppli.CIRCULATORY,
        comment='comment2',
    )

    assert_url_query_contains(
        responses.calls[0].request.url,
        {
            'callbackurl': 'http://localhost/callback2',
            'appli': str(NotifyAppli.CIRCULATORY.real),
            'comment': 'comment2',
        }
    )

    assert_url_path(
        responses.calls[0].request.url,
        '/notify'
    )
    assert_url_query_contains(
        responses.calls[0].request.url,
        {
            'action': 'subscribe',
        }
    )


def responses_add_notify_update() -> None:
    responses.add(
        method=responses.GET,
        url=re.compile(
            'https://wbsapi.withings.net/notify?.*action=update(&.*)?'
        ),
        status=200,
        json={
            'status': 0,
            'body': {},
        }
    )


@responses.activate
def test_notify_update_params(withings_api: WithingsApi) -> None:
    responses_add_notify_update()
    withings_api.notify_update(
        callbackurl='http://localhost/callback2',
        appli=NotifyAppli.CIRCULATORY,
        new_callbackurl='http://localhost/callback2',
        new_appli=NotifyAppli.SLEEP,
        comment='comment3',
    )

    assert_url_query_contains(
        responses.calls[0].request.url,
        {
            'callbackurl': 'http://localhost/callback2',
            'appli': str(NotifyAppli.CIRCULATORY.real),
            'new_callbackurl': 'http://localhost/callback2',
            'new_appli': str(NotifyAppli.SLEEP.real),
            'comment': 'comment3',
        }
    )

    assert_url_path(
        responses.calls[0].request.url,
        '/notify'
    )
    assert_url_query_contains(
        responses.calls[0].request.url,
        {
            'action': 'update',
        }
    )


@responses.activate
def test_measure_get_meas_params(withings_api: WithingsApi) -> None:
    responses_add_measure_get_meas()
    withings_api.measure_get_meas(
        meastype=MeasureType.BONE_MASS,
        category=MeasureGetMeasGroupCategory.USER_OBJECTIVES,
        startdate=arrow.get('2019-01-01'),
        enddate=100000000,
        offset=12,
        lastupdate=datetime.date(2019, 1, 2)
    )

    assert_url_query_contains(
        responses.calls[0].request.url,
        {
            'meastype': '88',
            'category': '2',
            'startdate': '1546300800',
            'enddate': '100000000',
            'offset': '12',
            'lastupdate': '1546387200',
        }
    )

    assert_url_path(
        responses.calls[0].request.url,
        '/measure'
    )
    assert_url_query_contains(
        responses.calls[0].request.url,
        {
            'action': 'getmeas',
        }
    )


@responses.activate
def test_measure_get_activity_params(withings_api: WithingsApi) -> None:
    responses_add_measure_get_activity()
    withings_api.measure_get_activity(
        startdateymd='2019-01-01',
        enddateymd=arrow.get('2019-01-02'),
        offset=2,
        data_fields=(
            GetActivityField.ACTIVE,
            GetActivityField.CALORIES,
            GetActivityField.ELEVATION,
        ),
        lastupdate=10000000
    )

    assert_url_query_contains(
        responses.calls[0].request.url,
        {
            'startdateymd': '2019-01-01',
            'enddateymd': '2019-01-02',
            'offset': '2',
            'data_fields': 'active,calories,elevation',
            'lastupdate': '10000000',
        }
    )

    assert_url_path(
        responses.calls[0].request.url,
        '/v2/measure'
    )
    assert_url_query_contains(
        responses.calls[0].request.url,
        {
            'action': 'getactivity',
        }
    )


@responses.activate
def test_get_sleep_params(withings_api: WithingsApi) -> None:
    responses_add_sleep_get()
    withings_api.sleep_get(
        startdate='2019-01-01',
        enddate=arrow.get('2019-01-02'),
        data_fields=(
            GetSleepField.HR,
            GetSleepField.HR,
        )
    )

    assert_url_query_contains(
        responses.calls[0].request.url,
        {
            'startdate': '1546300800',
            'enddate': '1546387200',
            'data_fields': 'hr,hr',
        }
    )

    assert_url_path(
        responses.calls[0].request.url,
        '/v2/sleep'
    )
    assert_url_query_contains(
        responses.calls[0].request.url,
        {
            'action': 'get',
        }
    )


@responses.activate
def test_get_sleep_summary_params(withings_api: WithingsApi) -> None:
    responses_add_sleep_get_summary()
    withings_api.sleep_get_summary(
        startdateymd='2019-01-01',
        enddateymd=arrow.get('2019-01-02'),
        data_fields=(
            GetSleepSummaryField.DEEP_SLEEP_DURATION,
            GetSleepSummaryField.HR_AVERAGE,
        ),
        lastupdate=10000000
    )

    assert_url_query_contains(
        responses.calls[0].request.url,
        {
            'startdateymd': '2019-01-01',
            'enddateymd': '2019-01-02',
            'data_fields': 'deepsleepduration,hr_average',
            'lastupdate': '10000000',
        }
    )

    assert_url_path(
        responses.calls[0].request.url,
        '/v2/sleep'
    )
    assert_url_query_contains(
        responses.calls[0].request.url,
        {
            'action': 'getsummary',
        }
    )


def assert_url_query_contains(url: str, expected: dict) -> None:
    params = dict(parse.parse_qsl(parse.urlsplit(url).query))

    for key, value in expected.items():
        assert key in params
        assert params[key] == expected[key]


def assert_url_path(url: str, path: str) -> None:
    assert parse.urlsplit(url).path == path
