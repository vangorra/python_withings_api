"""Common classes and functions."""

from datetime import tzinfo
from enum import Enum, IntEnum
from typing import (
    cast,
    NamedTuple,
    Optional,
    Tuple,
    Union,
    Any,
    Type,
    Dict,
)
from dateutil import tz

import arrow
from arrow import Arrow


class SleepModel(IntEnum):
    """Sleep model."""

    TRACKER = 16
    SLEEP_MONITOR = 32


def new_sleep_model(value: Optional[int]) -> SleepModel:
    """Create enum base on primitive."""
    return cast(SleepModel, enum_or_raise(value, SleepModel))


class SleepDataState(IntEnum):
    """Sleep states."""

    AWAKE = 0
    LIGHT = 1
    DEEP = 2
    REM = 3


def new_sleep_data_state(value: Optional[int]) -> SleepDataState:
    """Create enum base on primitive."""
    return cast(SleepDataState, enum_or_raise(value, SleepDataState))


class MeasureGroupAttrib(IntEnum):
    """Measure group attributions."""

    DEVICE_ENTRY_FOR_USER = 0
    DEVICE_ENTRY_FOR_USER_AMBIGUOUS = 1
    MANUAL_USER_ENTRY = 2
    MANUAL_USER_DURING_ACCOUNT_CREATION = 4
    MEASURE_AUTO = 5
    MEASURE_USER_CONFIRMED = 7
    SAME_AS_DEVICE_ENTRY_FOR_USER = 8


def new_measure_group_attrib(value: Optional[int]) -> MeasureGroupAttrib:
    """Create enum base on primitive."""
    return cast(MeasureGroupAttrib, enum_or_raise(value, MeasureGroupAttrib))


class MeasureCategory(IntEnum):
    """Measure categories."""

    REAL = 1
    USER_OBJECTIVES = 2


def new_measure_category(value: Optional[int]) -> MeasureCategory:
    """Create enum base on primitive."""
    return cast(MeasureCategory, enum_or_raise(value, MeasureCategory))


class MeasureType(IntEnum):
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


def new_measure_type(value: Optional[int]) -> MeasureType:
    """Create enum base on primitive."""
    return cast(MeasureType, enum_or_raise(value, MeasureType))


class SubscriptionParameter(IntEnum):
    """Data to subscribe to."""

    WEIGHT = 1
    CIRCULATORY = 4
    ACTIVITY = 16
    SLEEP = 44
    USER = 46
    BED_IN = 50
    BED_OUT = 51


def new_subscription_parameter(value: Optional[int]) -> SubscriptionParameter:
    """Create enum base on primitive."""
    return cast(
        SubscriptionParameter,
        enum_or_raise(value, SubscriptionParameter)
    )


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
    ('series', Tuple[GetSleepSerie, ...]),
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
    ('series', Tuple[GetSleepSummarySerie, ...]),
])

GetMeasMeasure = NamedTuple('GetMeasMeasure', [
    ('type', MeasureType),
    ('unit', int),
    ('value', int),
])


GetMeasGroup = NamedTuple('GetMeasGroup', [
    ('attrib', MeasureGroupAttrib),
    ('category', MeasureCategory),
    ('created', Arrow),
    ('date', Arrow),
    ('deviceid', str),
    ('grpid', str),
    ('measures', Tuple[GetMeasMeasure, ...]),
])


GetMeasResponse = NamedTuple('GetMeasResponse', [
    ('measuregrps', Tuple[GetMeasGroup, ...]),
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
    ('activities', Tuple[GetActivityActivity, ...]),
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
    ('profiles', Tuple[ListSubscriptionProfile, ...]),
])


def enforce_type(value: Any, expected: Type[Any]) -> Any:
    """Enforce a data type."""
    if not isinstance(value, expected):
        raise Exception(
            'Expected of "%s" to be "%s" but it was not.' % (
                value, expected
            )
        )

    return value


def enum_or_raise(
        value: Optional[Union[str, int]],
        enum: Type[Enum]
) -> Enum:
    """Return Enum or raise exception."""
    if value is None:
        raise Exception('Received None value for enum %s' % enum)

    return enum(value)


def str_or_raise(value: Any) -> str:
    """Return string or raise exception."""
    return enforce_type(value and str(value), str)


def bool_or_raise(value: Any) -> bool:
    """Return bool or raise exception."""
    return enforce_type(value, bool)


def int_or_raise(value: Any) -> int:
    """Return int or raise exception."""
    return enforce_type(value and int(value), int)


def float_or_raise(value: Any) -> float:
    """Return float or raise exception."""
    return enforce_type(value and float(value), float)


def arrow_or_raise(value: Any) -> Arrow:
    """Return Arrow or raise exception."""
    return enforce_type(value and arrow.get(value), Arrow)


def timezone_or_raise(value: Any) -> tzinfo:
    """Return tzinfo or raise exception."""
    return enforce_type(value and tz.gettz(value), tzinfo)


def dict_or_raise(value: Any) -> Dict[Any, Any]:
    """Return dict or raise exception."""
    return enforce_type(value and dict(value), dict)


def dict_or_none(value: Any) -> Optional[Dict[Any, Any]]:
    """Return dict or None."""
    return value and dict(value)


def new_credentials(
        client_id: str,
        consumer_secret: str,
        data: Dict[str, Any]
) -> Credentials:
    """Create Credentials from config and json."""
    return Credentials(
        access_token=str_or_raise(data.get('access_token')),
        token_expiry=arrow.utcnow().timestamp + data.get('expires_in'),
        token_type=str_or_raise(data.get('token_type')),
        refresh_token=str_or_raise(data.get('refresh_token')),
        user_id=str_or_raise(data.get('userid')),
        client_id=str_or_raise(client_id),
        consumer_secret=str_or_raise(consumer_secret),
    )


def new_list_subscription_profile(data: dict) -> ListSubscriptionProfile:
    """Create ListSubscriptionProfile from json."""
    return ListSubscriptionProfile(
        appli=new_subscription_parameter(data.get('appli')),
        callbackurl=str_or_raise(data.get('callbackurl')),
        expires=arrow_or_raise(data.get('expires')),
        comment=str_or_raise(data.get('comment')),
    )


def new_list_subscription_response(data: dict) -> ListSubscriptionsResponse:
    """Create ListSubscriptionsResponse from json."""
    return ListSubscriptionsResponse(
        profiles=tuple(
            new_list_subscription_profile(profile)
            for profile in data.get('profiles', ())
        )
    )


def new_sleep_timestamp(
        data: Optional[Dict[Any, Any]]
) -> Optional[SleepTimestamp]:
    """Create SleepTimestamp from json."""
    if data is None:
        return data

    return SleepTimestamp(arrow_or_raise(data.get('$timestamp')))


def new_get_sleep_serie(data: dict) -> GetSleepSerie:
    """Create GetSleepSerie from json."""
    return GetSleepSerie(
        enddate=arrow_or_raise(data.get("enddate")),
        startdate=arrow_or_raise(data.get("startdate")),
        state=new_sleep_data_state(data.get("state")),
        hr=new_sleep_timestamp(dict_or_none(data.get('hr'))),
        rr=new_sleep_timestamp(dict_or_none(data.get('rr'))),
    )


def new_get_sleep_response(data: dict) -> GetSleepResponse:
    """Create GetSleepResponse from json."""
    return GetSleepResponse(
        model=new_sleep_model(data.get('model')),
        series=tuple(
            new_get_sleep_serie(serie)
            for serie in data.get('series', ())
        )
    )


def new_get_sleep_summary_data(data: dict) -> GetSleepSummaryData:
    """Create GetSleepSummarySerie from json."""
    return GetSleepSummaryData(
        remsleepduration=int_or_raise(data.get('remsleepduration')),
        wakeupduration=int_or_raise(data.get('wakeupduration')),
        lightsleepduration=int_or_raise(data.get('lightsleepduration')),
        deepsleepduration=int_or_raise(data.get('deepsleepduration')),
        wakeupcount=int_or_raise(data.get('wakeupcount')),
        durationtosleep=int_or_raise(data.get('durationtosleep')),
        durationtowakeup=int_or_raise(data.get('durationtowakeup')),
        hr_average=int_or_raise(data.get('hr_average')),
        hr_min=int_or_raise(data.get('hr_min')),
        hr_max=int_or_raise(data.get('hr_max')),
        rr_average=int_or_raise(data.get('rr_average')),
        rr_min=int_or_raise(data.get('rr_min')),
        rr_max=int_or_raise(data.get('rr_max')),
    )


def new_get_sleep_summary_serie(data: dict) -> GetSleepSummarySerie:
    """Create GetSleepSummarySerie from json."""
    timezone = timezone_or_raise(data.get('timezone'))

    return GetSleepSummarySerie(
        date=arrow_or_raise(data.get('date')).replace(tzinfo=timezone),
        enddate=arrow_or_raise(data.get('enddate')).replace(tzinfo=timezone),
        model=new_sleep_model(data.get('model')),
        modified=arrow_or_raise(data.get('modified')).replace(tzinfo=timezone),
        startdate=arrow_or_raise(
            data.get('startdate')
        ).replace(tzinfo=timezone),
        timezone=timezone,
        data=new_get_sleep_summary_data(dict_or_raise(data.get('data')))
    )


def new_get_sleep_summary_response(data: dict) -> GetSleepSummaryResponse:
    """Create GetSleepSummaryResponse from json."""
    return GetSleepSummaryResponse(
        more=bool_or_raise(data.get('more')),
        offset=int_or_raise(data.get('offset')),
        series=tuple(
            new_get_sleep_summary_serie(serie)
            for serie in data.get('series', ())
        )
    )


def new_get_meas_measure(data: dict) -> GetMeasMeasure:
    """Create GetMeasMeasure from json."""
    return GetMeasMeasure(
        value=int_or_raise(data.get('value')),
        type=new_measure_type(data.get('type')),
        unit=int_or_raise(data.get('unit'))
    )


def new_get_meas_group(data: dict, timezone: tzinfo) -> GetMeasGroup:
    """Create GetMeasGroup from json."""
    return GetMeasGroup(
        grpid=str_or_raise(data.get('grpid')),
        attrib=new_measure_group_attrib(data.get('attrib')),
        date=arrow_or_raise(data.get('date')).replace(tzinfo=timezone),
        created=arrow_or_raise(data.get('created')).replace(tzinfo=timezone),
        category=new_measure_category(data.get('category')),
        deviceid=str_or_raise(data.get('deviceid')),
        measures=tuple(
            new_get_meas_measure(measure)
            for measure in data.get('measures', ())
        )
    )


def new_get_meas_response(data: dict) -> GetMeasResponse:
    """Create GetMeasResponse from json."""
    timezone = timezone_or_raise(data.get('timezone'))

    return GetMeasResponse(
        measuregrps=tuple(
            new_get_meas_group(group, timezone)
            for group in data.get('measuregrps', ())
        ),
        more=bool_or_raise(data.get('more')),
        offset=int_or_raise(data.get('offset')),
        timezone=timezone,
        updatetime=arrow_or_raise(
            data.get('updatetime')
        ).replace(tzinfo=timezone)
    )


def new_get_activity_activity(data: dict) -> GetActivityActivity:
    """Create GetActivityActivity from json."""
    timezone = timezone_or_raise(data.get('timezone'))

    return GetActivityActivity(
        date=arrow_or_raise(data.get('date')).replace(tzinfo=timezone),
        timezone=timezone,
        deviceid=str_or_raise(data.get('deviceid')),
        brand=int_or_raise(data.get('brand')),
        is_tracker=bool_or_raise(data.get('is_tracker')),
        steps=int_or_raise(data.get('steps')),
        distance=float_or_raise(data.get('distance')),
        elevation=float_or_raise(data.get('elevation')),
        soft=int_or_raise(data.get('soft')),
        moderate=int_or_raise(data.get('moderate')),
        intense=int_or_raise(data.get('intense')),
        active=int_or_raise(data.get('active')),
        calories=int_or_raise(data.get('calories')),
        totalcalories=int_or_raise(data.get('totalcalories')),
        hr_average=int_or_raise(data.get('hr_average')),
        hr_min=int_or_raise(data.get('hr_min')),
        hr_max=int_or_raise(data.get('hr_max')),
        hr_zone_0=int_or_raise(data.get('hr_zone_0')),
        hr_zone_1=int_or_raise(data.get('hr_zone_1')),
        hr_zone_2=int_or_raise(data.get('hr_zone_2')),
        hr_zone_3=int_or_raise(data.get('hr_zone_3')),
    )


def new_get_activity_response(data: dict) -> GetActivityResponse:
    """Create GetActivityResponse from json."""
    return GetActivityResponse(
        activities=tuple(
            new_get_activity_activity(activity)
            for activity in data.get('activities', ())
        ),
        more=bool_or_raise(data.get('more')),
        offset=int_or_raise(data.get('offset')),
    )


AMBIGUOUS_GROUP_ATTRIBS = (
    MeasureGroupAttrib.DEVICE_ENTRY_FOR_USER_AMBIGUOUS,
    MeasureGroupAttrib.MANUAL_USER_DURING_ACCOUNT_CREATION,
)


class MeasureGroupAttribs:
    """Groups of MeasureGroupAttrib."""

    ANY = tuple(enum_val for enum_val in MeasureGroupAttrib)
    AMBIGUOUS = AMBIGUOUS_GROUP_ATTRIBS
    UNAMBIGUOUS = tuple(
        enum_val
        for enum_val in MeasureGroupAttrib
        if enum_val not in AMBIGUOUS_GROUP_ATTRIBS
    )


class MeasureTypes:
    """Groups of MeasureType."""

    ANY = tuple(enum_val for enum_val in MeasureType)


def query_measure_groups(
        from_source: Union[
            GetMeasGroup, GetMeasResponse, Tuple[GetMeasGroup, ...]
        ],
        with_measure_type: Union[
            MeasureType,
            Tuple[MeasureType, ...]
        ] = MeasureTypes.ANY,
        with_group_attrib: Union[
            MeasureGroupAttrib,
            Tuple[MeasureGroupAttrib, ...]
        ] = MeasureGroupAttribs.ANY
) -> Tuple[GetMeasGroup, ...]:
    """Return a groups and measurements based on filters."""
    if isinstance(from_source, GetMeasResponse):
        iter_groups = cast(GetMeasResponse, from_source).measuregrps
    elif isinstance(from_source, GetMeasGroup):
        iter_groups = (cast(GetMeasGroup, from_source),)
    else:
        iter_groups = cast(Tuple[GetMeasGroup], from_source)

    if isinstance(with_measure_type, MeasureType):
        iter_measure_type = (
            cast(MeasureType, with_measure_type),
        )
    else:
        iter_measure_type = cast(
            Tuple[MeasureType], with_measure_type
        )

    if isinstance(with_group_attrib, MeasureGroupAttrib):
        iter_group_attrib = (
            cast(MeasureGroupAttrib, with_group_attrib),
        )
    else:
        iter_group_attrib = cast(
            Tuple[MeasureGroupAttrib],
            with_group_attrib
        )

    groups = []
    for group in iter_groups:
        if group.attrib not in iter_group_attrib:
            continue

        measures = []
        for measure in group.measures:
            if measure.type not in iter_measure_type:
                continue

            measures.append(measure)

        groups.append(GetMeasGroup(
            attrib=group.attrib,
            category=group.category,
            created=group.created,
            date=group.date,
            deviceid=group.deviceid,
            grpid=group.grpid,
            measures=tuple(measures)
        ))

    return tuple(groups)


def get_measure_value(
        from_source: Union[
            GetMeasGroup, GetMeasResponse, Tuple[GetMeasGroup, ...]
        ],
        with_measure_type: Union[
            MeasureType,
            Tuple[MeasureType, ...]
        ],
        with_group_attrib: Union[
            MeasureGroupAttrib,
            Tuple[MeasureGroupAttrib, ...]
        ] = MeasureGroupAttribs.ANY
) -> Optional[float]:
    """Get the first value of a measure that meet the query requirements."""
    groups = query_measure_groups(
        from_source,
        with_measure_type,
        with_group_attrib
    )

    for group in groups:
        for measure in group.measures:
            return measure.value * pow(10, measure.unit)

    return None
