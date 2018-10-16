import arrow
import datetime
import json
import unittest

from requests import Session
from nokia import (
    NokiaActivity,
    NokiaApi,
    NokiaCredentials,
    NokiaMeasureGroup,
    NokiaMeasures,
    NokiaSleep,
    NokiaSleepSeries
)

try:
    import configparser
except ImportError:  # Python 2.x fallback
    import ConfigParser as configparser

try:
    from unittest.mock import MagicMock
except ImportError:  # Python 2.x fallback
    from mock import MagicMock


class TestNokiaApi(unittest.TestCase):
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
        if self.mock_api:
            creds_args = {a: 'fake' + a for a in creds_attrs}
            creds_args.update({
                'token_expiry': '123412341234',
                'token_type': 'Bearer',
            })
            self.creds = NokiaCredentials(**creds_args)
        else:
            config = configparser.ConfigParser()
            config.read('nokia.conf')
            creds_args = {a: config.get('nokia', a) for a in creds_attrs}
            self.creds = NokiaCredentials(**creds_args)
        self.api = NokiaApi(self.creds)

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

    def test_attributes(self):
        """ Make sure the NokiaApi objects have the right attributes """
        assert hasattr(NokiaApi, 'URL')
        creds = NokiaCredentials(user_id='FAKEID', token_expiry='123412341234')
        api = NokiaApi(creds)
        assert hasattr(api, 'credentials')
        assert hasattr(api, 'token')
        assert hasattr(api, 'client')
        assert hasattr(api, 'refresh_cb')

    def test_attribute_defaults(self):
        """
        Make sure NokiaApi object attributes have the correct defaults
        """
        self.assertEqual(NokiaApi.URL, 'https://wbsapi.withings.net')
        creds = NokiaCredentials(user_id='FAKEID', token_expiry='123412341234')
        api = NokiaApi(creds)
        self.assertEqual(api.credentials, creds)
        self.assertEqual(api.client.params, {})
        self.assertEqual(api.client.token, api.token)
        self.assertEqual(api.refresh_cb, None)

    def test_get_credentials(self):
        """
        Make sure NokiaApi returns the credentials as expected
        """
        creds = NokiaCredentials(token_expiry=0)
        api = NokiaApi(creds)

    def test_set_token(self):
        """
        Make sure NokiaApi.set_token makes the expected changes
        """
        timestamp = int((
            datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
        ).total_seconds())
        creds = NokiaCredentials(token_expiry=timestamp)
        api = NokiaApi(creds)
        token = {
            'access_token': 'fakeat',
            'refresh_token': 'fakert',
            'expires_in': 100,
        }

        api.set_token(token)

        self.assertEqual(api.token, token)
        self.assertEqual(api.get_credentials().access_token, 'fakeat')
        self.assertEqual(api.get_credentials().refresh_token, 'fakert')
        # Need to check 100 or 101 in case a second ticked over during testing
        self.assertTrue(
            int(api.credentials.token_expiry) == (timestamp + 100) or
            int(api.credentials.token_expiry) == (timestamp + 101)
        )

    def test_set_token_refresh_cb(self):
        """
        Make sure set_token calls refresh_cb when specified
        """
        timestamp = int((
            datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
        ).total_seconds())
        creds = NokiaCredentials(token_expiry=timestamp)
        refresh_cb = MagicMock()
        api = NokiaApi(creds, refresh_cb=refresh_cb)
        token = {
            'access_token': 'fakeat',
            'refresh_token': 'fakert',
            'expires_in': 100,
        }

        api.set_token(token)

        self.assertEqual(api.token, token)
        refresh_cb.assert_called_once_with(token)

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

    def test_get_user(self):
        """ Check that the get_user method fetches the right URL """
        self.mock_request({
            'users': [
                {'id': 1111111, 'birthdate': 364305600, 'lastname': 'Baggins',
                 'ispublic': 255, 'firstname': 'Frodo', 'fatmethod': 131,
                 'gender': 0, 'shortname': 'FRO'}
            ]
        })
        resp = self.api.get_user()
        Session.request.assert_called_once_with(
            'GET',
            self._req_url('https://wbsapi.withings.net/user'),
            **self._req_kwargs({'action': 'getbyuserid'})
        )
        self.assertEqual(type(resp), dict)
        assert 'users' in resp
        self.assertEqual(type(resp['users']), list)
        self.assertEqual(len(resp['users']), 1)
        self.assertEqual(resp['users'][0]['firstname'], 'Frodo')
        self.assertEqual(resp['users'][0]['lastname'], 'Baggins')

    def test_get_sleep(self):
        """
        Check that get_sleep fetches the appropriate URL, the response looks
        correct, and the return value is a NokiaSleep object with the
        correct attributes
        """
        body = {
            "series": [{
                "startdate": 1387235398,
                "state": 0,
                "enddate": 1387235758
            }, {
                "startdate": 1387243618,
                "state": 1,
                "enddate": 1387244518
            }],
            "model": 16
        }
        self.mock_request(body)
        resp = self.api.get_sleep()
        Session.request.assert_called_once_with(
            'GET',
            self._req_url('https://wbsapi.withings.net/v2/sleep'),
            **self._req_kwargs({'action': 'get'})
        )
        self.assertEqual(type(resp), NokiaSleep)
        self.assertEqual(resp.model, body['model'])
        self.assertEqual(type(resp.series), list)
        self.assertEqual(len(resp.series), 2)
        self.assertEqual(type(resp.series[0]), NokiaSleepSeries)
        self.assertEqual(resp.series[0].startdate.timestamp,
                         body['series'][0]['startdate'])
        self.assertEqual(resp.series[0].enddate.timestamp,
                         body['series'][0]['enddate'])
        self.assertEqual(resp.series[1].state, 1)

    def test_get_activities(self):
        """
        Check that get_activities fetches the appropriate URL, the response
        looks correct, and the return value is a list of NokiaActivity
        objects
        """
        body = {
           "date": "2013-04-10",
           "steps": 6523,
           "distance": 4600,
           "calories": 408.52,
           "elevation": 18.2,
           "soft": 5880,
           "moderate": 1080,
           "intense": 540,
           "timezone": "Europe/Berlin"
        }
        self.mock_request(body)
        resp = self.api.get_activities()
        Session.request.assert_called_once_with(
            'GET',
            self._req_url('https://wbsapi.withings.net/v2/measure'),
            **self._req_kwargs({'action': 'getactivity'})
        )
        self.assertEqual(type(resp), list)
        self.assertEqual(len(resp), 1)
        self.assertEqual(type(resp[0]), NokiaActivity)
        # No need to assert all attributes, that happens elsewhere
        self.assertEqual(resp[0].data, body)

        # Test multiple activities
        new_body = {
            'activities': [
                body, {
                   "date": "2013-04-11",
                   "steps": 223,
                   "distance": 400,
                   "calories": 108.52,
                   "elevation": 1.2,
                   "soft": 160,
                   "moderate": 42,
                   "intense": 21,
                   "timezone": "Europe/Berlin"
                }
            ]
        }
        self.mock_request(new_body)
        resp = self.api.get_activities()
        Session.request.assert_called_once_with(
            'GET',
            self._req_url('https://wbsapi.withings.net/v2/measure'),
            **self._req_kwargs({'action': 'getactivity'})
        )
        self.assertEqual(type(resp), list)
        self.assertEqual(len(resp), 2)
        self.assertEqual(type(resp[0]), NokiaActivity)
        self.assertEqual(type(resp[1]), NokiaActivity)
        self.assertEqual(resp[0].data, new_body['activities'][0])
        self.assertEqual(resp[1].data, new_body['activities'][1])

    def test_get_measures(self):
        """
        Check that get_measures fetches the appriate URL, the response looks
        correct, and the return value is a NokiaMeasures object
        """
        body = {
            'updatetime': 1409596058,
            'measuregrps': [
                {'attrib': 2, 'measures': [
                    {'unit': -1, 'type': 1, 'value': 860}
                ], 'date': 1409361740, 'category': 1, 'grpid': 111111111},
                {'attrib': 2, 'measures': [
                    {'unit': -2, 'type': 4, 'value': 185}
                ], 'date': 1409361740, 'category': 1, 'grpid': 111111112}
            ]
        }
        self.mock_request(body)
        resp = self.api.get_measures()
        Session.request.assert_called_once_with(
            'GET',
            self._req_url('https://wbsapi.withings.net/measure'),
            **self._req_kwargs({'action': 'getmeas'})
        )
        self.assertEqual(type(resp), NokiaMeasures)
        self.assertEqual(len(resp), 2)
        self.assertEqual(type(resp[0]), NokiaMeasureGroup)
        self.assertEqual(resp[0].weight, 86.0)
        self.assertEqual(resp[1].height, 1.85)

        # Test limit=1
        body['measuregrps'].pop()
        self.mock_request(body)
        resp = self.api.get_measures(limit=1)
        Session.request.assert_called_once_with(
            'GET',
            self._req_url('https://wbsapi.withings.net/measure'),
            **self._req_kwargs({'action': 'getmeas', 'limit': 1})
        )
        self.assertEqual(len(resp), 1)
        self.assertEqual(resp[0].weight, 86.0)

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
        self.assertEquals(resp, True)

        # Not subscribed
        self.mock_request(None, status=343)
        resp = self.api.is_subscribed('http://www.example.com/')
        Session.request.assert_called_once_with(
            'GET', url, **self._req_kwargs(params))
        self.assertEquals(resp, False)

    def test_list_subscriptions(self):
        """
        Check that list_subscriptions fetches the right URL and returns the
        expected results
        """
        self.mock_request({'profiles': [
            {'comment': 'fake_comment', 'expires': 2147483647}
        ]})
        resp = self.api.list_subscriptions()
        Session.request.assert_called_once_with(
            'GET',
            self._req_url('https://wbsapi.withings.net/notify'),
            **self._req_kwargs({'action': 'list', 'appli': 1})
        )
        self.assertEqual(type(resp), list)
        self.assertEqual(len(resp), 1)
        self.assertEqual(resp[0]['comment'], 'fake_comment')
        self.assertEqual(resp[0]['expires'], 2147483647)

        # No subscriptions
        self.mock_request({'profiles': []})
        resp = self.api.list_subscriptions()
        Session.request.assert_called_once_with(
            'GET',
            self._req_url('https://wbsapi.withings.net/notify'),
            **self._req_kwargs({'action': 'list', 'appli': 1})
        )
        self.assertEqual(type(resp), list)
        self.assertEqual(len(resp), 0)

    def mock_request(self, body, status=0):
        if self.mock_api:
            json_content = {'status': status}
            if body is not None:
                json_content['body'] = body
            response = MagicMock()
            response.content = json.dumps(json_content).encode('utf8')
            Session.request = MagicMock(return_value=response)
