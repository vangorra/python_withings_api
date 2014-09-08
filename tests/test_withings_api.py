import json
import time
import unittest

from datetime import datetime
from requests import Session
from withings import (
    WithingsApi,
    WithingsCredentials,
    WithingsMeasureGroup,
    WithingsMeasures
)

try:
    import configparser
except ImportError:  # Python 2.x fallback
    import ConfigParser as configparser

try:
    from unittest.mock import MagicMock
except ImportError:  # Python 2.x fallback
    from mock import MagicMock


class TestWithingsApi(unittest.TestCase):
    def setUp(self):
        self.mock_api = True
        if self.mock_api:
            self.creds = WithingsCredentials()
        else:
            config = ConfigParser.ConfigParser()
            config.read('withings.conf')
            self.creds = WithingsCredentials(
                consumer_key=config.get('withings', 'consumer_key'),
                consumer_secret=config.get('withings', 'consumer_secret'),
                access_token=config.get('withings', 'access_token'),
                access_token_secret=config.get('withings',
                                               'access_token_secret'),
                user_id=config.get('withings', 'user_id'))
        self.api = WithingsApi(self.creds)

    def test_attributes(self):
        """ Make sure the WithingsApi objects have the right attributes """
        assert hasattr(WithingsApi, 'URL')
        creds = WithingsCredentials(user_id='FAKEID')
        api = WithingsApi(creds)
        assert hasattr(api, 'credentials')
        assert hasattr(api, 'oauth')
        assert hasattr(api, 'client')

    def test_attribute_defaults(self):
        """
        Make sure WithingsApi object attributes have the correct defaults
        """
        self.assertEqual(WithingsApi.URL, 'http://wbsapi.withings.net')
        creds = WithingsCredentials(user_id='FAKEID')
        api = WithingsApi(creds)
        self.assertEqual(api.credentials, creds)
        self.assertEqual(api.client.auth, api.oauth)
        self.assertEqual(api.client.params, {'userid': creds.user_id})

    def test_request(self):
        """
        Make sure the request method builds the proper URI and returns the
        request body as a python dict.
        """
        self.mock_request({})
        resp = self.api.request('fake_service', 'fake_action')
        Session.request.assert_called_once_with(
            'GET', 'http://wbsapi.withings.net/fake_service',
            params={'action': 'fake_action'})
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
            'POST', 'http://wbsapi.withings.net/user',
            params={'p2': 'p2', 'action': 'getbyuserid'})
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
            'GET', 'http://wbsapi.withings.net/user',
            params={'action': 'getbyuserid'})
        self.assertEqual(type(resp), dict)
        assert 'users' in resp
        self.assertEqual(type(resp['users']), list)
        self.assertEqual(len(resp['users']), 1)
        self.assertEqual(resp['users'][0]['firstname'], 'Frodo')
        self.assertEqual(resp['users'][0]['lastname'], 'Baggins')

    def test_get_measures(self):
        """
        Check that get_measures fetches the appriate URL, the response looks
        correct, and the return value is a WithingsMeasures object
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
            'GET', 'http://wbsapi.withings.net/measure',
            params={'action': 'getmeas'})
        self.assertEqual(type(resp), WithingsMeasures)
        self.assertEqual(len(resp), 2)
        self.assertEqual(type(resp[0]), WithingsMeasureGroup)
        self.assertEqual(resp[0].weight, 86.0)
        self.assertEqual(resp[1].height, 1.85)

        # Test limit=1
        body['measuregrps'].pop()
        self.mock_request(body)
        resp = self.api.get_measures(limit=1)
        Session.request.assert_called_once_with(
            'GET', 'http://wbsapi.withings.net/measure',
            params={'action': 'getmeas', 'limit': 1})
        self.assertEqual(len(resp), 1)
        self.assertEqual(resp[0].weight, 86.0)

    def test_subscribe(self):
        """
        Check that subscribe fetches the right URL and returns the expected
        results
        """
        # Unspecified appli
        self.mock_request(None)
        resp = self.api.subscribe('http://www.example.com/', 'fake_comment')
        Session.request.assert_called_once_with(
            'GET', 'http://wbsapi.withings.net/notify',
            params={'action': 'subscribe', 'comment': 'fake_comment',
                    'callbackurl': 'http://www.example.com/'})
        self.assertEqual(resp, None)

        # appli=1
        self.mock_request(None)
        resp = self.api.subscribe('http://www.example.com/', 'fake_comment',
                                  appli=1)
        Session.request.assert_called_once_with(
            'GET', 'http://wbsapi.withings.net/notify',
            params={'action': 'subscribe', 'appli': 1,
                    'comment': 'fake_comment',
                    'callbackurl': 'http://www.example.com/'})
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
            'GET', 'http://wbsapi.withings.net/notify',
            params={'action': 'revoke',
                    'callbackurl': 'http://www.example.com/'})
        self.assertEqual(resp, None)

        # appli=1
        self.mock_request(None)
        resp = self.api.unsubscribe('http://www.example.com/', appli=1)
        Session.request.assert_called_once_with(
            'GET', 'http://wbsapi.withings.net/notify',
            params={'action': 'revoke', 'appli': 1,
                    'callbackurl': 'http://www.example.com/'})
        self.assertEqual(resp, None)


    def test_is_subscribed(self):
        """
        Check that is_subscribed fetches the right URL and returns the
        expected results
        """
        url = 'http://wbsapi.withings.net/notify'
        params = {
            'callbackurl': 'http://www.example.com/',
            'action': 'get',
            'appli': 1
        }
        self.mock_request({'expires': 2147483647, 'comment': 'fake_comment'})
        resp = self.api.is_subscribed('http://www.example.com/')
        Session.request.assert_called_once_with('GET', url, params=params)
        self.assertEquals(resp, True)

        # Not subscribed
        self.mock_request(None, status=343)
        resp = self.api.is_subscribed('http://www.example.com/')
        Session.request.assert_called_once_with('GET', url, params=params)
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
            'GET', 'http://wbsapi.withings.net/notify',
            params={'action': 'list', 'appli': 1})
        self.assertEqual(type(resp), list)
        self.assertEqual(len(resp), 1)
        self.assertEqual(resp[0]['comment'], 'fake_comment')
        self.assertEqual(resp[0]['expires'], 2147483647)

        # No subscriptions
        self.mock_request({'profiles': []})
        resp = self.api.list_subscriptions()
        Session.request.assert_called_once_with(
            'GET', 'http://wbsapi.withings.net/notify',
            params={'action': 'list', 'appli': 1})
        self.assertEqual(type(resp), list)
        self.assertEqual(len(resp), 0)

    def mock_request(self, body, status=0):
        if self.mock_api:
            json_content = {'status': status}
            if body != None:
                json_content['body'] = body
            response = MagicMock()
            response.content = json.dumps(json_content).encode('utf8')
            Session.request = MagicMock(return_value=response)
