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

import arrow
from arrow.parser import ParserError
from oauthlib.oauth2 import WebApplicationClient
import requests
from requests_oauthlib import OAuth2Session

__title__ = 'withings'
__version__ = '1.1.0'
__author__ = 'Maxime Bouroumeau-Fuseau, and ORCAS'
__license__ = 'MIT'
__copyright__ = 'Copyright 2012-2018 Maxime Bouroumeau-Fuseau, and ORCAS'

__all__ = [str('WithingsCredentials'), str('WithingsAuth'), str('WithingsApi'),
           str('WithingsMeasures'), str('WithingsMeasureGroup')]


class WithingsCredentials:
    """Stores information about oauth2 credentials."""

    def __init__(self, access_token=None, token_expiry=None, token_type=None,
                 refresh_token=None, user_id=None,
                 client_id=None, consumer_secret=None):
        """Initialize new object."""
        self.access_token = access_token
        self.token_expiry = token_expiry
        self.token_type = token_type
        self.refresh_token = refresh_token
        self.user_id = user_id
        self.client_id = client_id
        self.consumer_secret = consumer_secret


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
        tokens = self._oauth().fetch_token(
            '%s/oauth2/token' % self.URL,
            code=code,
            client_secret=self.consumer_secret,
            include_client_id=True
        )

        return WithingsCredentials(
            access_token=tokens['access_token'],
            token_expiry=str(
                current_timstamp() + int(tokens['expires_in'])
            ),
            token_type=tokens['token_type'],
            refresh_token=tokens['refresh_token'],
            user_id=tokens['userid'],
            client_id=self.client_id,
            consumer_secret=self.consumer_secret,
        )

    def migrate_from_oauth1(self, access_token, access_token_secret):
        """Migrate from oauth1 to oauth2 api."""
        session = OAuth2Session(self.client_id, auto_refresh_kwargs={
            'client_id': self.client_id,
            'client_secret': self.consumer_secret,
        })
        return session.refresh_token(
            '{}/oauth2/token'.format(self.URL),
            refresh_token='{}:{}'.format(access_token, access_token_secret)
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


def current_timstamp():
    """
    Calculate seconds since 1970-01-01 (timestamp).

    Perform calculation in a way that works in Python 2 and Python3.
    https://docs.python.org/3/library/datetime.html#datetime.datetime.timestamp
    """
    return int((
        datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
    ).total_seconds())


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

    def __init__(self, credentials, refresh_cb=None):
        """Initialize new object."""
        self.credentials = credentials
        self.refresh_cb = refresh_cb
        self.token = {
            'access_token': credentials.access_token,
            'refresh_token': credentials.refresh_token,
            'token_type': credentials.token_type,
            'expires_in': str(
                int(credentials.token_expiry) - current_timstamp()
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

    def get_credentials(self):
        """Get the current oauth credentials."""
        return self.credentials

    def set_token(self, token):
        """Set the oauth token."""
        self.token = token
        self.credentials.token_expiry = str(
            current_timstamp() + int(self.token['expires_in'])
        )
        self.credentials.access_token = self.token['access_token']
        self.credentials.refresh_token = self.token['refresh_token']
        if self.refresh_cb:
            self.refresh_cb(token)

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

    def get_user(self):
        """Get user information."""
        return self.request('user', 'getbyuserid')

    def get_activities(self, **kwargs):
        """Get user created activities."""
        response = self.request(
            'measure',
            'getactivity',
            params=kwargs,
            version='v2'
        )
        activities = response.get('activities', [response])
        return [WithingsActivity(act) for act in activities]

    def get_measures(self, **kwargs):
        """Get measures."""
        response = self.request('measure', 'getmeas', kwargs)
        return WithingsMeasures(response)

    def get_sleep(self, **kwargs):
        """Get sleep data."""
        response = self.request('sleep', 'get', params=kwargs, version='v2')
        return WithingsSleep(response)

    def get_sleep_summary(self, **kwargs):
        """Get sleep summary."""
        response = self.request(
            'sleep',
            'getsummary',
            params=kwargs,
            version='v2'
        )

        return WithingsSleepSummary(response)

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

    def list_subscriptions(self, appli=1):
        """List current subscriptions from withings profile."""
        response = self.request('notify', 'list', {'appli': appli})
        return response['profiles']


class WithingsObject:
    """Generic object that dynamically maps withings data."""

    def __init__(self, data):
        """Initialize new object."""
        self.set_attributes(data)

    def set_attributes(self, data):
        """Set the attributes of  based on arbitrary dict or array."""
        self.data = data
        for key, val in data.items():
            try:
                setattr(self, key, arrow.get(val) if is_date(key) else val)
            except ParserError:
                setattr(self, key, val)


class WithingsActivity(WithingsObject):
    """Represents as withings activity."""

    pass


class WithingsMeasures(list, WithingsObject):
    """Represents a list of measure groups."""

    def __init__(self, data):
        """Initialize new object."""
        super(WithingsMeasures, self).__init__(
            [WithingsMeasureGroup(g) for g in data['measuregrps']])
        self.set_attributes(data)


class WithingsMeasureGroup(WithingsObject):
    """Represents a group of measures."""

    MEASURE_TYPES = (
        ('weight', 1),
        ('height', 4),
        ('fat_free_mass', 5),
        ('fat_ratio', 6),
        ('fat_mass_weight', 8),
        ('diastolic_blood_pressure', 9),
        ('systolic_blood_pressure', 10),
        ('heart_pulse', 11),
        ('temperature', 12),
        ('spo2', 54),
        ('body_temperature', 71),
        ('skin_temperature', 72),
        ('muscle_mass', 76),
        ('hydration', 77),
        ('bone_mass', 88),
        ('pulse_wave_velocity', 91)
    )

    measures = None
    category = None
    attrib = None

    def __init__(self, data):
        """Initialize new object."""
        super(WithingsMeasureGroup, self).__init__(data)
        for measure_name, measure_type in self.MEASURE_TYPES:
            self.__setattr__(measure_name, self.get_measure(measure_type))

    def is_ambiguous(self):
        """Return true if this group is ambiguous data."""
        return self.attrib == 1 or self.attrib == 4

    def is_measure(self):
        """Return true if this group is a measure."""
        return self.category == 1

    def is_target(self):
        """Return true if this group is the target."""
        return self.category == 2

    def get_measure(self, measure_type):
        """Get all the measures of a specific type."""
        for measure in self.measures:
            if measure['type'] == measure_type:
                return measure['value'] * pow(10, measure['unit'])
        return None


class WithingsSleepSeries(WithingsObject):
    """Represents withings sleep series data."""

    startdate = None
    enddate = None

    def __init__(self, data):
        """Initialize new object."""
        super(WithingsSleepSeries, self).__init__(data)
        self.timedelta = self.enddate - self.startdate


class WithingsSleep(WithingsObject):
    """Represent withings sleep data."""

    def __init__(self, data):
        """Initialize new object."""
        super(WithingsSleep, self).__init__(data)
        self.series = [WithingsSleepSeries(series) for series in self.series]


class WithingsSleepSummarySeries(WithingsObject):
    """Represents sleep summary series."""

    startdate = None
    enddate = None

    def __init__(self, data):
        """Initialize new object."""
        _data = data
        _data.update(_data.pop('data'))
        super(WithingsSleepSummarySeries, self).__init__(_data)
        self.timedelta = self.enddate - self.startdate


class WithingsSleepSummary(WithingsObject):
    """Represents sleep summary."""

    def __init__(self, data):
        """Initialize new object."""
        super(WithingsSleepSummary, self).__init__(data)
        self.series = [
            WithingsSleepSummarySeries(series) for series in self.series
        ]
