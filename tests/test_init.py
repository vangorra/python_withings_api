from unittest.mock import MagicMock
import datetime
from dateutil import tz
import re

import arrow
import pytest
import requests
import responses
from withings_api import (
    WithingsApi,
    WithingsAuth,
)

from withings_api.common import (
    SleepDataState,
    SleepModel,
    GetActivityResponse,
    GetActivityActivity,
    GetSleepResponse,
    GetSleepSerie,
    GetSleepSummaryResponse,
    GetSleepSummarySerie,
    GetSleepSummaryData,
    GetSleepSummaryField,
    GetMeasResponse,
    GetMeasGroup,
    SleepTimestamp,
    GetMeasMeasure,
    MeasureType,
    MeasureGroupAttrib,
    MeasureCategory,
    ListSubscriptionsResponse,
    ListSubscriptionProfile,
    SubscriptionParameter,
    Credentials,
    GetActivityField,
    GetSleepField,
)


@responses.activate
@pytest.fixture()
def withings_api():
    client_id = 'my_client_id'
    consumer_secret = 'my_consumer_secret'
    credentials = Credentials(
        access_token='my_access_token',
        token_expiry=arrow.utcnow().timestamp + 10000,
        token_type='Bearer',
        refresh_token='my_refresh_token',
        user_id='my_user_id',
        client_id=client_id,
        consumer_secret=consumer_secret,
    )

    return WithingsApi(credentials)


@responses.activate
@pytest.fixture()
def catch_all_withings_api(withings_api: WithingsApi):
    responses.add(
        method=responses.GET,
        url=re.compile('https://wbsapi.withings.net/.*'),
        status=200,
        json={
            'status': 0,
            'body': {}
        }
    )

    return withings_api


@responses.activate
def test_authorize():
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
            'userid': 'fake_user_id',
        },
        status=200
    )

    auth = WithingsAuth(
        client_id,
        consumer_secret,
        callback_uri=callback_uri
    )

    url = auth.get_authorize_url()

    assert url.startswith(
        'https://account.withings.com/oauth2_user/authorize2'
        '?response_type=code&client_id=fake_client_id'
        '&redirect_uri=http%3A%2F%2F127.0.0.1%3A8080'
        '&scope=user.metrics&state='
    )

    creds = auth.get_credentials('FAKE_CODE')

    assert creds == Credentials(
        access_token='fake_access_token',
        token_expiry=100000011,
        token_type='Bearer',
        refresh_token='fake_refresh_token',
        user_id='fake_user_id',
        client_id=client_id,
        consumer_secret=consumer_secret,
    )


@responses.activate
def test_request_exception(withings_api: WithingsApi):
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
        withings_api.get_meas()


@responses.activate
def test_refresh_token():
    client_id = 'my_client_id'
    consumer_secret = 'my_consumer_secret'

    credentials = Credentials(
        access_token='my_access_token',
        token_expiry=arrow.utcnow().timestamp - 1,
        token_type='Bearer',
        refresh_token='my_refresh_token',
        user_id='my_user_id',
        client_id=client_id,
        consumer_secret=consumer_secret,
    )

    responses.add(
        method=responses.POST,
        url=re.compile('https://account.withings.com/oauth2/token.*'),
        status=200,
        json={
            'access_token': 'my_access_token_new',
            'expires_in': 11,
            'token_type': 'Bearer',
            'refresh_token': 'my_refresh_token_new',
            'userid': 'my_user_id',
        }
    )

    responses.add(
        method=responses.GET,
        url=re.compile('https://wbsapi.withings.net/v2/measure.*'),
        status=200,
        json={
            'status': 0,
            'body': {},
        }
    )

    refresh_callback = MagicMock()
    api = WithingsApi(credentials, refresh_callback)
    api.get_activity()

    refresh_callback.assert_called_with(api.get_credentials())
    new_credentials = api.get_credentials()
    assert new_credentials.access_token == 'my_access_token_new'
    assert new_credentials.refresh_token == 'my_refresh_token_new'
    assert new_credentials.token_expiry > credentials.token_expiry


@responses.activate
def test_get_activities(withings_api: WithingsApi):
    timezone_str0 = 'Europe/London'
    timezone_str1 = 'America/Los_Angeles'
    timezone0 = tz.gettz(timezone_str0)
    timezone1 = tz.gettz(timezone_str1)

    responses.add(
        method=responses.GET,
        url='https://wbsapi.withings.net/v2/measure?access_token=my_access_token&userid=my_user_id&action=getactivity',
        status=200,
        json={
            'status': 0,
            'body': {
                'more': False,
                'offset': 0,
                'activities': [
                    {
                        'date': '2019-01-01',
                        'timezone': timezone_str0,
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
                        'timezone': timezone_str1,
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
    assert withings_api.get_activity() == GetActivityResponse(
        more=False,
        offset=0,
        activities=(
            GetActivityActivity(
                date=arrow.get('2019-01-01').replace(tzinfo=timezone0),
                timezone=timezone0,
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
            GetActivityActivity(
                date=arrow.get('2019-01-02').replace(tzinfo=timezone1),
                timezone=timezone1,
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


@responses.activate
def test_get_meas(withings_api: WithingsApi):
    timezone_str0 = 'Europe/London'
    timezone_str1 = 'America/Los_Angeles'
    timezone0 = tz.gettz(timezone_str0)
    timezone1 = tz.gettz(timezone_str1)

    responses.add(
        method=responses.GET,
        url='https://wbsapi.withings.net/measure?access_token=my_access_token&userid=my_user_id&action=getmeas',
        status=200,
        json={
            'status': 0,
            'body': {
                'more': False,
                'offset': 0,
                'updatetime': 1409596058,
                'timezone': timezone_str0,
                'measuregrps': [
                    {
                        'attrib': MeasureGroupAttrib.MANUAL_USER_DURING_ACCOUNT_CREATION,
                        'category': MeasureCategory.REAL,
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
                        'attrib': MeasureGroupAttrib.DEVICE_ENTRY_FOR_USER_AMBIGUOUS,
                        'category': MeasureCategory.USER_OBJECTIVES,
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
    assert withings_api.get_meas() == GetMeasResponse(
        more=False,
        offset=0,
        timezone=timezone0,
        updatetime=arrow.get(1409596058).replace(tzinfo=timezone0),
        measuregrps=(
            GetMeasGroup(
                attrib=MeasureGroupAttrib.MANUAL_USER_DURING_ACCOUNT_CREATION,
                category=MeasureCategory.REAL,
                created=arrow.get(1111111111).replace(tzinfo=timezone0),
                date=arrow.get('2019-01-01').replace(tzinfo=timezone0),
                deviceid='dev1',
                grpid='grp1',
                measures=(
                    GetMeasMeasure(
                        type=MeasureType.HEIGHT,
                        unit=110,
                        value=110,
                    ),
                    GetMeasMeasure(
                        type=MeasureType.WEIGHT,
                        unit=120,
                        value=120,
                    )
                ),
            ),
            GetMeasGroup(
                attrib=MeasureGroupAttrib.DEVICE_ENTRY_FOR_USER_AMBIGUOUS,
                category=MeasureCategory.USER_OBJECTIVES,
                created=arrow.get(2222222222).replace(tzinfo=timezone0),
                date=arrow.get('2019-01-02').replace(tzinfo=timezone0),
                deviceid='dev2',
                grpid='grp2',
                measures=(
                    GetMeasMeasure(
                        type=MeasureType.BODY_TEMPERATURE,
                        unit=210,
                        value=210,
                    ),
                    GetMeasMeasure(
                        type=MeasureType.BONE_MASS,
                        unit=220,
                        value=220,
                    )
                ),
            )
        )
    )


@responses.activate
def test_get_sleep(withings_api: WithingsApi):
    timezone_str0 = 'Europe/London'
    timezone_str1 = 'America/Los_Angeles'
    timezone0 = tz.gettz(timezone_str0)
    timezone1 = tz.gettz(timezone_str1)

    responses.add(
        method=responses.GET,
        url='https://wbsapi.withings.net/v2/sleep?access_token=my_access_token&userid=my_user_id&action=get',
        status=200,
        json={
            'status': 0,
            'body': {
                "series": [
                    {
                        "startdate": 1387235398,
                        "state": SleepDataState.AWAKE,
                        "enddate": 1387235758
                    },
                    {
                        "startdate": 1387243618,
                        "state": SleepDataState.LIGHT,
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
    assert withings_api.get_sleep() == GetSleepResponse(
        model=SleepModel.TRACKER,
        series=(
            GetSleepSerie(
                startdate=arrow.get(1387235398),
                state=SleepDataState.AWAKE,
                enddate=arrow.get(1387235758),
                hr=None,
                rr=None,
            ),
            GetSleepSerie(
                startdate=arrow.get(1387243618),
                state=SleepDataState.LIGHT,
                enddate=arrow.get(1387244518),
                hr=SleepTimestamp(arrow.get(123)),
                rr=SleepTimestamp(arrow.get(456)),
            )
        )
    )


@responses.activate
def test_get_sleep_summary(withings_api: WithingsApi):
    timezone_str0 = 'Europe/London'
    timezone_str1 = 'America/Los_Angeles'
    timezone0 = tz.gettz(timezone_str0)
    timezone1 = tz.gettz(timezone_str1)

    responses.add(
        method=responses.GET,
        url='https://wbsapi.withings.net/v2/sleep?access_token=my_access_token&userid=my_user_id&action=getsummary',
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
                        'timezone': timezone_str0,
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
                        'timezone': timezone_str1,
                    }
                ]
            }
        }
    )
    assert withings_api.get_sleep_summary() == GetSleepSummaryResponse(
        more=False,
        offset=1,
        series=(
            GetSleepSummarySerie(
                date=arrow.get('2018-10-30').replace(tzinfo=timezone0),
                enddate=arrow.get(1540897020).replace(tzinfo=timezone0),
                model=SleepModel.TRACKER,
                modified=arrow.get(1540897246).replace(tzinfo=timezone0),
                startdate=arrow.get(1540857420).replace(tzinfo=timezone0),
                timezone=timezone0,
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
                date=arrow.get('2018-10-31').replace(tzinfo=timezone1),
                enddate=arrow.get(1540973400).replace(tzinfo=timezone1),
                model=SleepModel.TRACKER,
                modified=arrow.get(1541020749).replace(tzinfo=timezone1),
                startdate=arrow.get(1540944960).replace(tzinfo=timezone1),
                timezone=timezone1,
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


@responses.activate
def test_get_subscriptions(withings_api: WithingsApi):
    timezone_str0 = 'Europe/London'
    timezone_str1 = 'America/Los_Angeles'
    timezone0 = tz.gettz(timezone_str0)
    timezone1 = tz.gettz(timezone_str1)

    responses.add(
        method=responses.GET,
        url='https://wbsapi.withings.net/notify?access_token=my_access_token&callbackurl=http%3A%2F%2Flocalhost%2Fcallback&comment=comment1&userid=my_user_id&action=subscribe',
        status=200,
        json={
            'status': 0,
            'body': {}
        }
    )
    withings_api.subscribe('http://localhost/callback', 'comment1')

    # Subscription revoke.
    responses.add(
        method=responses.GET,
        url='https://wbsapi.withings.net/notify?access_token=my_access_token&callbackurl=http%3A%2F%2Flocalhost%2Fcallback&userid=my_user_id&action=revoke',
        status=200,
        json={
            'status': 0,
            'body': {}
        }
    )
    withings_api.unsubscribe('http://localhost/callback')

    # Subscription list.
    responses.add(
        method=responses.GET,
        url='https://wbsapi.withings.net/notify?access_token=my_access_token&appli=1&userid=my_user_id&action=list',
        status=200,
        json={
            'status': 0,
            'body': {
                'profiles': [
                    {
                        'appli': SubscriptionParameter.WEIGHT.real,
                        'callbackurl': 'http://localhost/callback',
                        'comment': 'fake_comment1',
                        'expires': '10000000',
                    },
                    {
                        'appli': SubscriptionParameter.CIRCULATORY.real,
                        'callbackurl': 'http://localhost/callback2',
                        'comment': 'fake_comment2',
                        'expires': '20000000',
                    },
                ]
            }
        }
    )
    assert withings_api.is_subscribed('http://localhost/callback')
    assert not withings_api.is_subscribed('http://localhost/callbackX')
    assert withings_api.list_subscriptions() == ListSubscriptionsResponse(
        profiles=(
            ListSubscriptionProfile(
                appli=SubscriptionParameter.WEIGHT,
                callbackurl='http://localhost/callback',
                comment='fake_comment1',
                expires=arrow.get(10000000)
            ),
            ListSubscriptionProfile(
                appli=SubscriptionParameter.CIRCULATORY,
                callbackurl='http://localhost/callback2',
                comment='fake_comment2',
                expires=arrow.get(20000000)
            ),
        ),
    )


@responses.activate
def test_get_meas_params(catch_all_withings_api: WithingsApi):
    catch_all_withings_api.get_meas(
        meastype=MeasureType.BONE_MASS,
        category=MeasureCategory.USER_OBJECTIVES,
        startdate=arrow.get('2019-01-01'),
        enddate=100000000,
        offset=12,
        lastupdate=datetime.date(2019, 1, 2)
    )

    assert responses.calls[0].request.url == 'https://wbsapi.withings.net/measure?access_token=my_access_token&meastype=MeasureType.BONE_MASS&category=MeasureCategory.USER_OBJECTIVES&startdate=1546300800&enddate=100000000&offset=12&lastupdate=1546387200&userid=my_user_id&action=getmeas'


@responses.activate
def test_get_activity_params(catch_all_withings_api: WithingsApi):
    catch_all_withings_api.get_activity(
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

    assert responses.calls[0].request.url == 'https://wbsapi.withings.net/v2/measure?access_token=my_access_token&startdateymd=2019-01-01&enddateymd=2019-01-02&offset=2&data_fields=active%2Ccalories%2Celevation&lastupdate=10000000&userid=my_user_id&action=getactivity'


@responses.activate
def test_get_sleep_params(catch_all_withings_api: WithingsApi):
    catch_all_withings_api.get_sleep(
        startdate='2019-01-01',
        enddate=arrow.get('2019-01-02'),
        data_fields=(
            GetSleepField.HR,
            GetSleepField.HR,
        )
    )

    assert responses.calls[0].request.url == 'https://wbsapi.withings.net/v2/sleep?access_token=my_access_token&startdate=1546300800&enddate=1546387200&data_fields=hr%2Chr&userid=my_user_id&action=get'


@responses.activate
def test_get_sleep_summary_params(catch_all_withings_api: WithingsApi):
    catch_all_withings_api.get_sleep_summary(
        startdateymd='2019-01-01',
        enddateymd=arrow.get('2019-01-02'),
        data_fields=(
            GetSleepSummaryField.DEEPSLEEPDURATION,
            GetSleepSummaryField.HR_AVERAGE,
        ),
        lastupdate=10000000
    )

    assert responses.calls[0].request.url == 'https://wbsapi.withings.net/v2/sleep?access_token=my_access_token&startdateymd=2019-01-01&enddateymd=2019-01-02&data_fields=deepsleepduration%2Chr_average&lastupdate=10000000&userid=my_user_id&action=getsummary'
