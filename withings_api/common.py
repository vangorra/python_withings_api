"""Common classes and functions."""

from datetime import tzinfo
from enum import Enum
from typing import NamedTuple, Optional, Tuple
from dateutil import tz

import arrow
from arrow import Arrow


class SleepModel(Enum):
    """Sleep model."""

    TRACKER = 16
    SLEEP_MONITOR = 32


class SleepDataState(Enum):
    """Sleep states."""

    AWAKE = 0
    LIGHT = 1
    DEEP = 2
    REM = 3


class MeasureGroupAttribution(Enum):
    """Measure group attributions."""

    DEVICE_ENTRY_FOR_USER = 0
    DEVICE_ENTRY_FOR_USER_AMBIGUOUS = 1
    MANUAL_USER_ENTRY = 2
    MANUAL_USER_DURING_ACCOUNT_CREATION = 4
    MEASURE_AUTO = 5
    MEASURE_USER_CONFIRMED = 7
    SAME_AS_DEVICE_ENTRY_FOR_USER = 8


class MeasureCategory(Enum):
    """Measure categories."""

    REAL = 1
    USER_OBJECTIVES = 2


class MeasureType(Enum):
    """Measure types."""

    WEIGHT = 1
    HEIGHT = 4
    FAT_FREE_MASS = 5
    FAT_RATIO = 6
    FAT_MASS_WEIGHT = 8
    DIASTOLIC_BLOOD_PRESSURE = 9
    SYSTOLIC_BLOOD_PRESSURE = 10
    HEART_RATE = 11
    TEMPERATURE = 12
    SP02 = 54
    BODY_TEMPERATURE = 71
    SKIN_TEMPERATURE = 73
    MUSCLE_MASS = 76
    HYDRATION = 77
    BONE_MASS = 88
    PULSE_WAVE_VELOCITY = 91


class SubscriptionParameter(Enum):
    """Data to subscribe to."""

    WEIGHT = 1
    CIRCULATORY = 4
    ACTIVITY = 16
    SLEEP = 44
    USER = 46
    BED_IN = 50
    BED_OUT = 51


class GetActivityField(Enum):
    """Fields for the getactivity api call."""

    STEPS = 'steps'
    DISTANCE = 'distance'
    ELEVATION = 'elevation'
    SOFT = 'soft'
    MODERATE = 'moderate'
    INTENSE = 'intense'
    ACTIVE = 'active'
    CALORIES = 'calories'
    TOTAL_CALORIES = 'totalcalories'
    HR_AVERAGE = 'hr_average'
    HR_MIN = 'hr_min'
    HR_MAX = 'hr_max'
    HR_ZONE_0 = 'hr_zone_0'
    HR_ZONE_1 = 'hr_zone_1'
    HR_ZONE_2 = 'hr_zone_2'
    HR_ZONE_3 = 'hr_zone_3'


class GetSleepField(Enum):
    """Fields for getsleep api call."""

    HR = 'hr'
    RR = 'rr'


class GetSleepSummaryField(Enum):
    """Fields for get sleep summary api call."""

    REMSLEEPDURATION = 'remsleepduration'
    WAKEUPDURATION = 'wakeupduration'
    LIGHTSLEEPDURATION = 'lightsleepduration'
    DEEPSLEEPDURATION = 'deepsleepduration'
    WAKEUPCOUNT = 'wakeupcount'
    DURATIONTOSLEEP = 'durationtosleep'
    DURATIONTOWAKEUP = 'durationtowakeup'
    HR_AVERAGE = 'hr_average'
    HR_MIN = 'hr_min'
    HR_MAX = 'hr_max'
    RR_AVERAGE = 'rr_average'
    RR_MIN = 'rr_min'
    RR_MAX = 'rr_max'


SleepTimestamp = NamedTuple('SleepTimestamp', [
    ('timestamp', Arrow),
])

GetSleepSerie = NamedTuple('GetSleepSerie', [
    ('enddate', Arrow),
    ('startdate', Arrow),
    ('state', SleepDataState),
    ('hr', Optional[SleepTimestamp]),
    ('rr', Optional[SleepTimestamp]),
])

GetSleepResponse = NamedTuple('GetSleepResponse', [
    ('model', SleepModel),
    ('series', Tuple[GetSleepSerie]),
])

GetSleepSummaryData = NamedTuple('GetSleepSummaryData', [
    ('remsleepduration', int),
    ('wakeupduration', int),
    ('lightsleepduration', int),
    ('deepsleepduration', int),
    ('wakeupcount', int),
    ('durationtosleep', int),
    ('durationtowakeup', int),
    ('hr_average', int),
    ('hr_min', int),
    ('hr_max', int),
    ('rr_average', int),
    ('rr_min', int),
    ('rr_max', int),
])

GetSleepSummarySerie = NamedTuple('GetSleepSummarySerie', [
    ('timezone', tzinfo),
    ('model', SleepModel),
    ('startdate', Arrow),
    ('enddate', Arrow),
    ('date', Arrow),
    ('modified', Arrow),
    ('data', GetSleepSummaryData),
])

GetSleepSummaryResponse = NamedTuple('GetSleepSummaryResponse', [
    ('more', bool),
    ('offset', int),
    ('series', Tuple[GetSleepSummarySerie]),
])

GetMeasMeasure = NamedTuple('GetMeasMeasure', [
    ('type', MeasureType),
    ('unit', int),
    ('value', int),
])

GetMeasGroup = NamedTuple('GetMeasGroup', [
    ('attrib', MeasureGroupAttribution),
    ('category', MeasureCategory),
    ('created', Arrow),
    ('date', Arrow),
    ('deviceid', str),
    ('grpid', str),
    ('measures', Tuple[GetMeasMeasure]),
])

GetMeasResponse = NamedTuple('GetMeasResponse', [
    ('measuregrps', Tuple[GetMeasGroup]),
    ('more', bool),
    ('offset', int),
    ('timezone', tzinfo),
    ('updatetime', Arrow),
])

GetActivityActivity = NamedTuple('GetActivityActivities', [
    ('date', Arrow),
    ('timezone', tzinfo),
    ('deviceid', str),
    ('brand', int),
    ('is_tracker', bool),
    ('steps', int),
    ('distance', float),
    ('elevation', float),
    ('soft', int),
    ('moderate', int),
    ('intense', int),
    ('active', int),
    ('calories', float),
    ('totalcalories', float),
    ('hr_average', int),
    ('hr_min', int),
    ('hr_max', int),
    ('hr_zone_0', int),
    ('hr_zone_1', int),
    ('hr_zone_2', int),
    ('hr_zone_3', int),
])

GetActivityResponse = NamedTuple('GetActivityResponse', [
    ('activities', Tuple[GetActivityActivity]),
    ('more', bool),
    ('offset', int),
])

Credentials = NamedTuple('Credentials', [
    ('access_token', str),
    ('token_expiry', int),
    ('token_type', str),
    ('refresh_token', str),
    ('user_id', str),
    ('client_id', str),
    ('consumer_secret', str),
])


ListSubscriptionProfile = NamedTuple('ListSubscriptionProfile', [
    ('appli', SubscriptionParameter),
    ('callbackurl', str),
    ('expires', Arrow),
    ('comment', str),
])

ListSubscriptionsResponse = NamedTuple('ListSubscriptionsResponse', [
    ('profiles', Tuple[ListSubscriptionProfile]),
])


def new_credentials(
        client_id: str,
        consumer_secret: str,
        data: dict
) -> Credentials:
    """Create Credentials from config and json."""
    return Credentials(
        access_token=data.get('access_token'),
        token_expiry=arrow.utcnow().timestamp + data.get('expires_in'),
        token_type=data.get('token_type'),
        refresh_token=data.get('refresh_token'),
        user_id=data.get('userid'),
        client_id=client_id,
        consumer_secret=consumer_secret,
    )


def new_list_subscription_profile(data: dict) -> ListSubscriptionProfile:
    """Create ListSubscriptionProfile from json."""
    return ListSubscriptionProfile(
        appli=SubscriptionParameter(data.get('appli')),
        callbackurl=data.get('callbackurl'),
        expires=arrow.get(int(data.get('expires'))),
        comment=data.get('comment'),
    )


def new_list_subscription_response(data: dict) -> ListSubscriptionsResponse:
    """Create ListSubscriptionsResponse from json."""
    return ListSubscriptionsResponse(
        profiles=tuple(
            new_list_subscription_profile(profile)
            for profile in data.get('profiles', ())
        )
    )


def new_sleep_timestamp(data: dict) -> Optional[SleepTimestamp]:
    """Create SleepTimestamp from json."""
    if not data:
        return

    return SleepTimestamp(arrow.get(data.get('$timestamp')))


def new_get_sleep_serie(data: dict) -> GetSleepSerie:
    """Create GetSleepSerie from json."""
    return GetSleepSerie(
        enddate=arrow.get(data.get("enddate")),
        startdate=arrow.get(data.get("startdate")),
        state=SleepDataState(data.get("state")),
        hr=new_sleep_timestamp(data.get('hr')),
        rr=new_sleep_timestamp(data.get('rr')),
    )


def new_get_sleep_response(data: dict) -> GetSleepResponse:
    """Create GetSleepResponse from json."""
    return GetSleepResponse(
        model=SleepModel(data.get('model')),
        series=tuple(
            new_get_sleep_serie(serie)
            for serie in data.get('series', ())
        )
    )


def new_get_sleep_summary_data(data: dict) -> GetSleepSummaryData:
    """Create GetSleepSummarySerie from json."""
    return GetSleepSummaryData(
        remsleepduration=data.get('remsleepduration'),
        wakeupduration=data.get('wakeupduration'),
        lightsleepduration=data.get('lightsleepduration'),
        deepsleepduration=data.get('deepsleepduration'),
        wakeupcount=data.get('wakeupcount'),
        durationtosleep=data.get('durationtosleep'),
        durationtowakeup=data.get('durationtowakeup'),
        hr_average=data.get('hr_average'),
        hr_min=data.get('hr_min'),
        hr_max=data.get('hr_max'),
        rr_average=data.get('rr_average'),
        rr_min=data.get('rr_min'),
        rr_max=data.get('rr_max'),
    )


def new_get_sleep_summary_serie(data: dict) -> GetSleepSummarySerie:
    """Create GetSleepSummarySerie from json."""
    timezone = tz.gettz(data.get('timezone'))

    return GetSleepSummarySerie(
        date=arrow.get(data.get('date')).replace(tzinfo=timezone),
        enddate=arrow.get(data.get('enddate')).replace(tzinfo=timezone),
        model=SleepModel(data.get('model')),
        modified=arrow.get(data.get('modified')).replace(tzinfo=timezone),
        startdate=arrow.get(data.get('startdate')).replace(tzinfo=timezone),
        timezone=timezone,
        data=new_get_sleep_summary_data(data.get('data'))
    )


def new_get_sleep_summary_response(data: dict) -> GetSleepSummaryResponse:
    """Create GetSleepSummaryResponse from json."""
    return GetSleepSummaryResponse(
        more=data.get('more'),
        offset=data.get('offset'),
        series=tuple(
            new_get_sleep_summary_serie(serie)
            for serie in data.get('series', ())
        )
    )


def new_get_meas_measure(data: dict) -> GetMeasMeasure:
    """Create GetMeasMeasure from json."""
    value = data.get('value')
    unit = data.get('unit')
    return GetMeasMeasure(
        value=value,
        type=MeasureType(data.get('type')),
        unit=unit
    )


def new_get_meas_group(data: dict, timezone: tzinfo) -> GetMeasGroup:
    """Create GetMeasGroup from json."""
    attrib = MeasureGroupAttribution(data.get('attrib'))

    return GetMeasGroup(
        grpid=data.get('grpid'),
        attrib=attrib,
        date=arrow.get(data.get('date')).replace(tzinfo=timezone),
        created=arrow.get(data.get('created')).replace(tzinfo=timezone),
        category=MeasureCategory(data.get('category')),
        deviceid=data.get('deviceid'),
        measures=tuple(
            new_get_meas_measure(measure)
            for measure in data.get('measures', ())
        )
    )


def new_get_meas_response(data: dict) -> GetMeasResponse:
    """Create GetMeasResponse from json."""
    timezone = tz.gettz(data.get('timezone'))

    return GetMeasResponse(
        measuregrps=tuple(
            new_get_meas_group(group, timezone)
            for group in data.get('measuregrps', ())
        ),
        more=data.get('more'),
        offset=data.get('offset'),
        timezone=timezone,
        updatetime=arrow.get(data.get('updatetime')).replace(tzinfo=timezone)
    )


def new_get_activity_activity(data: dict) -> GetActivityActivity:
    """Create GetActivityActivity from json."""
    timezone = tz.gettz(data.get('timezone'))

    return GetActivityActivity(
        date=arrow.get(data.get('date')).replace(tzinfo=timezone),
        timezone=timezone,
        deviceid=data.get('deviceid'),
        brand=data.get('brand'),
        is_tracker=data.get('is_tracker'),
        steps=data.get('steps'),
        distance=data.get('distance'),
        elevation=data.get('elevation'),
        soft=data.get('soft'),
        moderate=data.get('moderate'),
        intense=data.get('intense'),
        active=data.get('active'),
        calories=data.get('calories'),
        totalcalories=data.get('totalcalories'),
        hr_average=data.get('hr_average'),
        hr_min=data.get('hr_min'),
        hr_max=data.get('hr_max'),
        hr_zone_0=data.get('hr_zone_0'),
        hr_zone_1=data.get('hr_zone_1'),
        hr_zone_2=data.get('hr_zone_2'),
        hr_zone_3=data.get('hr_zone_3'),
    )


def new_get_activity_response(data: dict) -> GetActivityResponse:
    """Create GetActivityResponse from json."""
    return GetActivityResponse(
        activities=tuple(
            new_get_activity_activity(activity)
            for activity in data.get('activities', ())
        ),
        more=data.get('more'),
        offset=data.get('offset')
    )


def is_measure_ambiguous(
        group: GetMeasGroup
) -> bool:
    """Determine if a group is made from ambiguous data."""
    return group.attrib in (
        MeasureGroupAttribution.DEVICE_ENTRY_FOR_USER_AMBIGUOUS,
        MeasureGroupAttribution.MANUAL_USER_DURING_ACCOUNT_CREATION,
    )


def get_measure_value(
        group: GetMeasGroup,
        measure_type: MeasureType
) -> Optional[int]:
    """Return a measurement value from a group."""
    for measure in group.measures:
        if measure.type == measure_type:
            return measure.value * pow(10, measure.unit)
