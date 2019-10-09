import configparser
from unittest.mock import MagicMock
import arrow
import datetime
from dateutil import tz
import json
import unittest

import arrow
from requests import Session
from withings_api import (
    WithingsApi,
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
    GetMeasResponse,
    GetMeasGroup,
    SleepTimestamp,
    GetMeasMeasure,
    MeasureType,
    MeasureGroupAttribution,
    MeasureCategory,
    ListSubscriptionsResponse,
    ListSubscriptionProfile,
    SubscriptionParameter,
    Credentials,
    get_measure_value,
    is_measure_ambiguous,
)

class TestMeasureValues(unittest.TestCase):
    def test_is_ambiguous(self):
        ambig_attribs = (
            MeasureGroupAttribution.DEVICE_ENTRY_FOR_USER_AMBIGUOUS,
            MeasureGroupAttribution.MANUAL_USER_DURING_ACCOUNT_CREATION,
        )

        groups = tuple(
            GetMeasGroup(
                attrib=attrib,
                category=MeasureCategory.USER_OBJECTIVES,
                created=arrow.utcnow(),
                date=arrow.utcnow(),
                deviceid='dev1',
                grpid='1',
                measures=()
            )
            for attrib in MeasureGroupAttribution
        )

        for group in groups:
            self.assertEqual(
                group.attrib in ambig_attribs,
                is_measure_ambiguous(group)
            )

    def test_get_measure_value(self):
        group = GetMeasGroup(
            attrib=MeasureGroupAttribution.MANUAL_USER_DURING_ACCOUNT_CREATION,
            category=MeasureCategory.USER_OBJECTIVES,
            created=arrow.utcnow(),
            date=arrow.utcnow(),
            deviceid='dev1',
            grpid='1',
            measures=(
                GetMeasMeasure(
                    type=MeasureType.WEIGHT,
                    unit=1,
                    value=10,
                ),
                GetMeasMeasure(
                    type=MeasureType.BONE_MASS,
                    unit=-2,
                    value=20,
                ),
            )
        )

        self.assertIsNone(
            get_measure_value(group, MeasureType.BODY_TEMPERATURE)
        )
        self.assertEqual(
            100,
            get_measure_value(group, MeasureType.WEIGHT)
        )
        self.assertEqual(
            0.2,
            get_measure_value(group, MeasureType.BONE_MASS)
        )

        pass

class TestWithingsApi(unittest.TestCase):
    def setUp(self):
        self.mock_api = True
        creds_attrs = [
            'access_token',
            'token_expiry',
            'token_type',
            'refresh_token',
            'user_id',
            'client_id',
            'consumer_secret',
        ]
        creds_args = {a: 'fake' + a for a in creds_attrs}
        creds_args.update({
            'token_expiry': '123412341234',
            'token_type': 'Bearer',
        })
        self.creds = Credentials(
            access_token='fakeaccess_token',
            token_expiry=123412341234,
            token_type='Bearer',
            refresh_token='fakerefresh_token',
            user_id='fakeuser_id',
            client_id='fakeclient_id',
            consumer_secret='fakeconsumer_secret',
        )
        self.api = WithingsApi(self.creds)

    def _req_url(self, url):
        return url + '?access_token=fakeaccess_token'

    def _req_kwargs(self, extra_params):
        params = {
            'userid': 'fakeuser_id',
        }
        params.update(extra_params)
        return {
            'data': None,
            'headers': None,
            'params': params,
        }

    def test_set_token(self):
        """
        Make sure WithingsApi.set_token makes the expected changes
        """
        timestamp = int((
                                datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
                        ).total_seconds())
        creds = Credentials(
            access_token='AA',
            token_expiry=timestamp,
            token_type='AA',
            refresh_token='AA',
            user_id='AA',
            client_id='AA',
            consumer_secret='AA',
        )
        refresh_cb = MagicMock()
        api = WithingsApi(creds)
        token = {
            'access_token': 'fakeat',
            'refresh_token': 'fakert',
            'expires_in': 100,
        }

        api.set_token(token)

        self.assertEqual(api.token, token)
        refresh_cb.assert_not_called()

    def test_set_token_refresh_cb(self):
        """
        Make sure set_token calls refresh_cb when specified
        """
        timestamp = int((
            datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
        ).total_seconds())
        creds = Credentials(
            access_token='AA',
            token_expiry=timestamp,
            token_type='AA',
            refresh_token='AA',
            user_id='AA',
            client_id='AA',
            consumer_secret='AA',
        )
        refresh_cb = MagicMock()
        api = WithingsApi(creds, refresh_cb=refresh_cb)
        token = {
            'access_token': 'fakeat',
            'refresh_token': 'fakert',
            'expires_in': 100,
        }

        api.set_token(token)

        self.assertEqual(api.token, token)
        refresh_cb.assert_called_once_with(api.credentials)

    def test_request(self):
        """
        Make sure the request method builds the proper URI and returns the
        request body as a python dict.
        """
        self.mock_request({})
        resp = self.api.request('fake_service', 'fake_action')
        Session.request.assert_called_once_with(
            'GET',
            self._req_url('https://wbsapi.withings.net/fake_service'),
            **self._req_kwargs({'action': 'fake_action'})
        )
        self.assertEqual(resp, {})

    def test_request_params(self):
        """
        Check that the request method passes along extra params and works
        with different HTTP methods
        """
        self.mock_request({})
        resp = self.api.request('user', 'getbyuserid', params={'p2': 'p2'},
                                method='POST')
        Session.request.assert_called_once_with(
            'POST',
            self._req_url('https://wbsapi.withings.net/user'),
            **self._req_kwargs({'p2': 'p2', 'action': 'getbyuserid'})
        )
        self.assertEqual(resp, {})

    def test_request_error(self):
        """ Check that requests raises an exception when there is an error """
        self.mock_request('', status=1)
        self.assertRaises(Exception, self.api.request, ('user', 'getbyuserid'))

    def test_get_sleep(self):
        """
        Check that get_sleep fetches the appropriate URL, the response looks
        correct, and the return value is a WithingsSleep object with the
        correct attributes
        """
        body = {
            "series": [
                {
                    "startdate": 1387235398,
                    "state": SleepDataState.AWAKE.value.real,
                    "enddate": 1387235758
                },
                {
                    "startdate": 1387243618,
                    "state": SleepDataState.LIGHT.value.real,
                    "enddate": 1387244518,
                    "hr": {
                        "$timestamp": 123,
                    },
                    "rr": {
                        "$timestamp": 456,
                    },
                }
            ],
            "model": SleepModel.TRACKER.value.real,
        }
        self.mock_request(body)
        resp = self.api.get_sleep()
        Session.request.assert_called_once_with(
            'GET',
            self._req_url('https://wbsapi.withings.net/v2/sleep'),
            **self._req_kwargs({'action': 'get'})
        )

        self.assertEqual(
            resp,
            GetSleepResponse(
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
        )

    def test_get_sleep_summary(self):
        """
        Check that get_sleep_summary fetches the appropriate URL, the response looks
        correct, and the return value is a WithingsSleepSummary object with the
        correct attributes
        """
        body = {
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
                    'model': SleepModel.TRACKER.value.real,
                    'modified': 1540897246,
                    'startdate': 1540857420,
                    'timezone': 'Europe/London',
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
                    'model': SleepModel.TRACKER.value.real,
                    'modified': 1541020749,
                    'startdate': 1540944960,
                    'timezone': 'America/Los_Angeles',
                }
            ]
        }
        self.mock_request(body)
        resp = self.api.get_sleep_summary()
        Session.request.assert_called_once_with(
            'GET',
            self._req_url('https://wbsapi.withings.net/v2/sleep'),
            **self._req_kwargs({'action': 'getsummary'})
        )
        timezone0 = tz.gettz(body.get('series')[0].get('timezone'))
        timezone1 = tz.gettz(body.get('series')[1].get('timezone'))

        self.assertEqual(
            resp,
            GetSleepSummaryResponse(
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
        )

    def test_get_activities(self):
        """
        Check that get_activities fetches the appropriate URL, the response
        looks correct, and the return value is a list of WithingsActivity
        objects
        """
        body = {
            'more': False,
            'offset': 0,
            'activities': [
                {
                    'date': '2019-01-01',
                    'timezone': 'Europe/London',
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
                    'timezone': 'America/Los_Angeles',
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
        }
        self.mock_request(body)
        resp = self.api.get_activities()
        Session.request.assert_called_once_with(
            'GET',
            self._req_url('https://wbsapi.withings.net/v2/measure'),
            **self._req_kwargs({'action': 'getactivity'})
        )

        timezone0 = tz.gettz(body.get('activities')[0].get('timezone'))
        timezone1 = tz.gettz(body.get('activities')[1].get('timezone'))

        self.assertEqual(
            resp,
            GetActivityResponse(
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
        )

    def test_get_measures(self):
        """
        Check that get_measures fetches the appriate URL, the response looks
        correct, and the return value is a WithingsMeasures object
        """
        body = {
            'more': False,
            'offset': 0,
            'updatetime': 1409596058,
            'timezone': 'Europe/London',
            'measuregrps': [
                {
                    'attrib': MeasureGroupAttribution.MANUAL_USER_DURING_ACCOUNT_CREATION.value.real,
                    'category': MeasureCategory.REAL.value.real,
                    'created': 1111111111,
                    'date': '2019-01-01',
                    'deviceid': 'dev1',
                    'grpid': 'grp1',
                    'measures': [
                        {
                            'type': MeasureType.HEIGHT.value.real,
                            'unit': 110,
                            'value': 110,
                        },
                        {
                            'type': MeasureType.WEIGHT.value.real,
                            'unit': 120,
                            'value': 120,
                        },
                    ]
                },
                {
                    'attrib': MeasureGroupAttribution.DEVICE_ENTRY_FOR_USER_AMBIGUOUS.value.real,
                    'category': MeasureCategory.USER_OBJECTIVES.value.real,
                    'created': 2222222222,
                    'date': '2019-01-02',
                    'deviceid': 'dev2',
                    'grpid': 'grp2',
                    'measures': [
                        {
                            'type': MeasureType.BODY_TEMPERATURE.value.real,
                            'unit': 210,
                            'value': 210,
                        },
                        {
                            'type': MeasureType.BONE_MASS.value.real,
                            'unit': 220,
                            'value': 220,
                        },
                    ],
                },
            ],
        }
        self.mock_request(body)
        resp = self.api.get_measures()
        Session.request.assert_called_once_with(
            'GET',
            self._req_url('https://wbsapi.withings.net/measure'),
            **self._req_kwargs({'action': 'getmeas'})
        )

        timezone = tz.gettz(body.get('timezone'))

        self.assertEqual(
            resp,
            GetMeasResponse(
                more=False,
                offset=0,
                timezone=timezone,
                updatetime=arrow.get(1409596058).replace(tzinfo=timezone),
                measuregrps=(
                    GetMeasGroup(
                        attrib=MeasureGroupAttribution.MANUAL_USER_DURING_ACCOUNT_CREATION,
                        category=MeasureCategory.REAL,
                        created=arrow.get(1111111111).replace(tzinfo=timezone),
                        date=arrow.get('2019-01-01').replace(tzinfo=timezone),
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
                        attrib=MeasureGroupAttribution.DEVICE_ENTRY_FOR_USER_AMBIGUOUS,
                        category=MeasureCategory.USER_OBJECTIVES,
                        created=arrow.get(2222222222).replace(tzinfo=timezone),
                        date=arrow.get('2019-01-02').replace(tzinfo=timezone),
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
        )

    def test_get_measures_lastupdate_date(self):
        """Check that dates get converted to timestampse for API calls"""
        self.mock_request({'updatetime': 1409596058, 'measuregrps': []})

        self.api.get_measures(lastupdate=datetime.date(2014, 9, 1))

        Session.request.assert_called_once_with(
            'GET',
            self._req_url('https://wbsapi.withings.net/measure'),
            **self._req_kwargs({'action': 'getmeas', 'lastupdate': 1409529600})
        )

    def test_get_measures_lastupdate_datetime(self):
        """Check that datetimes get converted to timestampse for API calls"""
        self.mock_request({'updatetime': 1409596058, 'measuregrps': []})

        self.api.get_measures(lastupdate=datetime.datetime(2014, 9, 1))

        Session.request.assert_called_once_with(
            'GET',
            self._req_url('https://wbsapi.withings.net/measure'),
            **self._req_kwargs({'action': 'getmeas', 'lastupdate': 1409529600})
        )

    def test_get_measures_lastupdate_arrow(self):
        """Check that arrow dates get converted to timestampse for API calls"""
        self.mock_request({'updatetime': 1409596058, 'measuregrps': []})

        self.api.get_measures(lastupdate=arrow.get('2014-09-01'))

        Session.request.assert_called_once_with(
            'GET',
            self._req_url('https://wbsapi.withings.net/measure'),
            **self._req_kwargs({'action': 'getmeas', 'lastupdate': 1409529600})
        )

    def test_subscribe(self):
        """
        Check that subscribe fetches the right URL and returns the expected
        results
        """
        # Unspecified appli
        self.mock_request(None)
        resp = self.api.subscribe('http://www.example.com/', 'fake_comment')
        Session.request.assert_called_once_with(
            'GET',
            self._req_url('https://wbsapi.withings.net/notify'),
            **self._req_kwargs({
                'action': 'subscribe',
                'comment': 'fake_comment',
                'callbackurl': 'http://www.example.com/',
            })
        )
        self.assertEqual(resp, None)

        # appli=1
        self.mock_request(None)
        resp = self.api.subscribe('http://www.example.com/', 'fake_comment',
                                  appli=1)
        Session.request.assert_called_once_with(
            'GET',
            self._req_url('https://wbsapi.withings.net/notify'),
            **self._req_kwargs({
                'action': 'subscribe',
                'appli': 1,
                'comment': 'fake_comment',
                'callbackurl': 'http://www.example.com/',
            })
        )
        self.assertEqual(resp, None)

    def test_unsubscribe(self):
        """
        Check that unsubscribe fetches the right URL and returns the expected
        results
        """
        # Unspecified appli
        self.mock_request(None)
        resp = self.api.unsubscribe('http://www.example.com/')
        Session.request.assert_called_once_with(
            'GET',
            self._req_url('https://wbsapi.withings.net/notify'),
            **self._req_kwargs({
                'action': 'revoke',
                'callbackurl': 'http://www.example.com/',
            })
        )
        self.assertEqual(resp, None)

        # appli=1
        self.mock_request(None)
        resp = self.api.unsubscribe('http://www.example.com/', appli=1)
        Session.request.assert_called_once_with(
            'GET',
            self._req_url('https://wbsapi.withings.net/notify'),
            **self._req_kwargs({
                'action': 'revoke', 'appli': 1,
                'callbackurl': 'http://www.example.com/',
            })
        )
        self.assertEqual(resp, None)

    def test_is_subscribed(self):
        """
        Check that is_subscribed fetches the right URL and returns the
        expected results
        """
        url = self._req_url('https://wbsapi.withings.net/notify')
        params = {
            'callbackurl': 'http://www.example.com/',
            'action': 'get',
            'appli': 1
        }
        self.mock_request({'expires': 2147483647, 'comment': 'fake_comment'})
        resp = self.api.is_subscribed('http://www.example.com/')
        Session.request.assert_called_once_with(
            'GET', url, **self._req_kwargs(params))
        self.assertEqual(resp, True)

        # Not subscribed
        self.mock_request(None, status=343)
        resp = self.api.is_subscribed('http://www.example.com/')
        Session.request.assert_called_once_with(
            'GET', url, **self._req_kwargs(params))
        self.assertEqual(resp, False)

    def test_list_subscriptions(self):
        """
        Check that list_subscriptions fetches the right URL and returns the
        expected results
        """
        self.mock_request({
            'profiles': [
                {
                    'appli': SubscriptionParameter.WEIGHT.value.real,
                    'callbackurl': 'my_callback_url1',
                    'comment': 'fake_comment1',
                    'expires': '10000000',
                },
                {
                    'appli': SubscriptionParameter.CIRCULATORY.value.real,
                    'callbackurl': 'my_callback_url2',
                    'comment': 'fake_comment2',
                    'expires': '20000000',
                },
            ]
        })
        resp = self.api.list_subscriptions()
        Session.request.assert_called_once_with(
            'GET',
            self._req_url('https://wbsapi.withings.net/notify'),
            **self._req_kwargs({'action': 'list', 'appli': 1})
        )

        self.assertEqual(
            resp,
            ListSubscriptionsResponse(
                profiles=(
                    ListSubscriptionProfile(
                        appli=SubscriptionParameter.WEIGHT,
                        callbackurl='my_callback_url1',
                        comment='fake_comment1',
                        expires=arrow.get(10000000)
                    ),
                    ListSubscriptionProfile(
                        appli=SubscriptionParameter.CIRCULATORY,
                        callbackurl='my_callback_url2',
                        comment='fake_comment2',
                        expires=arrow.get(20000000)
                    ),
                ),
            ),
        )

        # No subscriptions
        self.mock_request({'profiles': []})
        resp = self.api.list_subscriptions()
        Session.request.assert_called_once_with(
            'GET',
            self._req_url('https://wbsapi.withings.net/notify'),
            **self._req_kwargs({'action': 'list', 'appli': 1})
        )

        self.assertEqual(
            resp,
            ListSubscriptionsResponse(
                profiles=()
            )
        )

    def mock_request(self, body, status=0):
        if self.mock_api:
            json_content = {'status': status}
            if body is not None:
                json_content['body'] = body
            response = MagicMock()
            response.content = json.dumps(json_content).encode('utf8')
            Session.request = MagicMock(return_value=response)
