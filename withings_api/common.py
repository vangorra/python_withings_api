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
    TypeVar,
    Callable,
)
from dateutil import tz

import arrow
from arrow import Arrow

from .const import (
    STATUS_SUCCESS,
    STATUS_INVALID_PARAMS,
    STATUS_AUTH_FAILED,
    STATUS_BAD_STATE,
    STATUS_ERROR_OCCURRED,
    STATUS_TIMEOUT,
    STATUS_TOO_MANY_REQUESTS,
    STATUS_UNAUTHORIZED,
)


class SleepModel(IntEnum):
    """Sleep model."""

    TRACKER = 16
    SLEEP_MONITOR = 32


def new_sleep_model(value: Optional[int]) -> SleepModel:
    """Create enum base on primitive."""
    return cast(SleepModel, enum_or_raise(value, SleepModel))


class SleepState(IntEnum):
    """Sleep states."""

    AWAKE = 0
    LIGHT = 1
    DEEP = 2
    REM = 3


def new_sleep_state(value: Optional[int]) -> SleepState:
    """Create enum base on primitive."""
    return cast(SleepState, enum_or_raise(value, SleepState))


class MeasureGetMeasGroupAttrib(IntEnum):
    """Measure group attributions."""

    UNKNOWN = -1
    DEVICE_ENTRY_FOR_USER = 0
    DEVICE_ENTRY_FOR_USER_AMBIGUOUS = 1
    MANUAL_USER_ENTRY = 2
    MANUAL_USER_DURING_ACCOUNT_CREATION = 4
    MEASURE_AUTO = 5
    MEASURE_USER_CONFIRMED = 7
    SAME_AS_DEVICE_ENTRY_FOR_USER = 8


def new_measure_group_attrib(value: Optional[int]) -> MeasureGetMeasGroupAttrib:
    """Create enum base on primitive."""
    return cast(
        MeasureGetMeasGroupAttrib, enum_or_raise(value, MeasureGetMeasGroupAttrib)
    )


class MeasureGetMeasGroupCategory(IntEnum):
    """Measure categories."""

    REAL = 1
    USER_OBJECTIVES = 2


def new_measure_category(value: Optional[int]) -> MeasureGetMeasGroupCategory:
    """Create enum base on primitive."""
    return cast(
        MeasureGetMeasGroupCategory, enum_or_raise(value, MeasureGetMeasGroupCategory)
    )


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


class NotifyAppli(IntEnum):
    """Data to notify_subscribe to."""

    WEIGHT = 1
    CIRCULATORY = 4
    ACTIVITY = 16
    SLEEP = 44
    USER = 46
    BED_IN = 50
    BED_OUT = 51


def new_notify_appli(value: Optional[int]) -> NotifyAppli:
    """Create enum base on primitive."""
    return cast(NotifyAppli, enum_or_raise(value, NotifyAppli))


class GetActivityField(Enum):
    """Fields for the getactivity api call."""

    STEPS = "steps"
    DISTANCE = "distance"
    ELEVATION = "elevation"
    SOFT = "soft"
    MODERATE = "moderate"
    INTENSE = "intense"
    ACTIVE = "active"
    CALORIES = "calories"
    TOTAL_CALORIES = "totalcalories"
    HR_AVERAGE = "hr_average"
    HR_MIN = "hr_min"
    HR_MAX = "hr_max"
    HR_ZONE_0 = "hr_zone_0"
    HR_ZONE_1 = "hr_zone_1"
    HR_ZONE_2 = "hr_zone_2"
    HR_ZONE_3 = "hr_zone_3"


class GetSleepField(Enum):
    """Fields for getsleep api call."""

    HR = "hr"
    RR = "rr"


class GetSleepSummaryField(Enum):
    """Fields for get sleep summary api call."""

    REM_SLEEP_DURATION = "remsleepduration"
    WAKEUP_DURATION = "wakeupduration"
    LIGHT_SLEEP_DURATION = "lightsleepduration"
    DEEP_SLEEP_DURATION = "deepsleepduration"
    WAKEUP_COUNT = "wakeupcount"
    DURATION_TO_SLEEP = "durationtosleep"
    DURATION_TO_WAKEUP = "durationtowakeup"
    HR_AVERAGE = "hr_average"
    HR_MIN = "hr_min"
    HR_MAX = "hr_max"
    RR_AVERAGE = "rr_average"
    RR_MIN = "rr_min"
    RR_MAX = "rr_max"


class AuthScope(Enum):
    """Authorization scopes."""

    USER_INFO = "user.info"
    USER_METRICS = "user.metrics"
    USER_ACTIVITY = "user.activity"
    USER_SLEEP_EVENTS = "user.sleepevents"


UserGetDeviceDevice = NamedTuple(
    "UserGetDeviceDevice",
    [
        ("type", str),
        ("model", str),
        ("battery", str),
        ("deviceid", str),
        ("timezone", tzinfo),
    ],
)


UserGetDeviceResponse = NamedTuple(
    "GetDeviceResponse", [("devices", Tuple[UserGetDeviceDevice, ...])]
)


SleepGetTimestamp = NamedTuple("SleepGetTimestamp", [("timestamp", Arrow)])

SleepGetSerie = NamedTuple(
    "SleepGetSerie",
    [
        ("enddate", Arrow),
        ("startdate", Arrow),
        ("state", SleepState),
        ("hr", Optional[SleepGetTimestamp]),
        ("rr", Optional[SleepGetTimestamp]),
    ],
)

SleepGetResponse = NamedTuple(
    "GetSleepResponse", [("model", SleepModel), ("series", Tuple[SleepGetSerie, ...])]
)

GetSleepSummaryData = NamedTuple(
    "GetSleepSummaryData",
    [
        ("remsleepduration", Optional[int]),
        ("wakeupduration", Optional[int]),
        ("lightsleepduration", Optional[int]),
        ("deepsleepduration", Optional[int]),
        ("wakeupcount", Optional[int]),
        ("durationtosleep", Optional[int]),
        ("durationtowakeup", Optional[int]),
        ("hr_average", Optional[int]),
        ("hr_min", Optional[int]),
        ("hr_max", Optional[int]),
        ("rr_average", Optional[int]),
        ("rr_min", Optional[int]),
        ("rr_max", Optional[int]),
    ],
)

GetSleepSummarySerie = NamedTuple(
    "GetSleepSummarySerie",
    [
        ("timezone", tzinfo),
        ("model", SleepModel),
        ("startdate", Arrow),
        ("enddate", Arrow),
        ("date", Arrow),
        ("modified", Arrow),
        ("data", GetSleepSummaryData),
    ],
)

SleepGetSummaryResponse = NamedTuple(
    "GetSleepSummaryResponse",
    [("more", bool), ("offset", int), ("series", Tuple[GetSleepSummarySerie, ...])],
)

MeasureGetMeasMeasure = NamedTuple(
    "MeasureGetMeasMeasure", [("type", MeasureType), ("unit", int), ("value", int)]
)


MeasureGetMeasGroup = NamedTuple(
    "MeasureGetMeasGroup",
    [
        ("attrib", MeasureGetMeasGroupAttrib),
        ("category", MeasureGetMeasGroupCategory),
        ("created", Arrow),
        ("date", Arrow),
        ("deviceid", Optional[str]),
        ("grpid", int),
        ("measures", Tuple[MeasureGetMeasMeasure, ...]),
    ],
)


MeasureGetMeasResponse = NamedTuple(
    "GetMeasResponse",
    [
        ("measuregrps", Tuple[MeasureGetMeasGroup, ...]),
        ("more", Optional[bool]),
        ("offset", Optional[int]),
        ("timezone", tzinfo),
        ("updatetime", Arrow),
    ],
)


MeasureGetActivityActivity = NamedTuple(
    "MeasureGetActivityActivity",
    [
        ("date", Arrow),
        ("timezone", tzinfo),
        ("deviceid", Optional[str]),
        ("brand", int),
        ("is_tracker", bool),
        ("steps", Optional[int]),
        ("distance", Optional[float]),
        ("elevation", Optional[float]),
        ("soft", Optional[int]),
        ("moderate", Optional[int]),
        ("intense", Optional[int]),
        ("active", Optional[int]),
        ("calories", Optional[float]),
        ("totalcalories", float),
        ("hr_average", Optional[int]),
        ("hr_min", Optional[int]),
        ("hr_max", Optional[int]),
        ("hr_zone_0", Optional[int]),
        ("hr_zone_1", Optional[int]),
        ("hr_zone_2", Optional[int]),
        ("hr_zone_3", Optional[int]),
    ],
)

MeasureGetActivityResponse = NamedTuple(
    "GetActivityResponse",
    [
        ("activities", Tuple[MeasureGetActivityActivity, ...]),
        ("more", bool),
        ("offset", int),
    ],
)

Credentials = NamedTuple(
    "Credentials",
    [
        ("access_token", str),
        ("token_expiry", int),
        ("token_type", str),
        ("refresh_token", str),
        ("userid", int),
        ("client_id", str),
        ("consumer_secret", str),
    ],
)


NotifyListProfile = NamedTuple(
    "NotifyListProfile",
    [
        ("appli", NotifyAppli),
        ("callbackurl", str),
        ("expires", Arrow),
        ("comment", Optional[str]),
    ],
)

NotifyListResponse = NamedTuple(
    "NotifyListResponse", [("profiles", Tuple[NotifyListProfile, ...])]
)

NotifyGetResponse = NamedTuple(
    "NotifyGetResponse",
    [("appli", NotifyAppli), ("callbackurl", str), ("comment", Optional[str])],
)


GenericType = TypeVar("GenericType")


class UnexpectedTypeException(Exception):
    """Thrown when encountering an unexpected type."""

    def __init__(self, value: Any, expected: Type[GenericType]):
        """Initialize."""
        super().__init__(
            'Expected of "%s" to be "%s" but was "%s."' % (value, expected, type(value))
        )


def enforce_type(value: Any, expected: Type[GenericType]) -> GenericType:
    """Enforce a data type."""
    if not isinstance(value, expected):
        raise UnexpectedTypeException(value, expected)

    return value


def value_or_none(
    value: Any, convert_fn: Callable[[Any], GenericType]
) -> Union[GenericType, None]:
    """Convert a value given a specific conversion function."""
    if value is None:
        return None

    try:
        return convert_fn(value)
    except Exception:  # pylint: disable=broad-except
        return None


def enum_or_raise(value: Optional[Union[str, int]], enum: Type[Enum]) -> Enum:
    """Return Enum or raise exception."""
    if value is None:
        raise Exception("Received None value for enum %s" % enum)

    return enum(value)


def str_or_raise(value: Any) -> str:
    """Return string or raise exception."""
    return enforce_type(str_or_none(value), str)


def str_or_none(value: Any) -> Optional[str]:
    """Return str or None."""
    return value_or_none(value, str)


def bool_or_raise(value: Any) -> bool:
    """Return bool or raise exception."""
    return enforce_type(value, bool)


def bool_or_none(value: Any) -> Optional[bool]:
    """Return bool or None."""
    return value_or_none(value, bool)


def int_or_raise(value: Any) -> int:
    """Return int or raise exception."""
    return enforce_type(int_or_none(value), int)


def int_or_none(value: Any) -> Optional[int]:
    """Return int or None."""
    return value_or_none(value, int)


def float_or_raise(value: Any) -> float:
    """Return float or raise exception."""
    return enforce_type(float_or_none(value), float)


def float_or_none(value: Any) -> Optional[float]:
    """Return float or None."""
    return value_or_none(value, float)


def arrow_or_none(value: Any) -> Optional[Arrow]:
    """Returns Arrow or None."""
    if value is None:
        return None

    return arrow.get(value)


def timezone_or_none(value: Any) -> Optional[tzinfo]:
    """Returns tzinfo or None."""
    if value is None:
        return None

    return tz.gettz(value)


def arrow_or_raise(value: Any) -> Arrow:
    """Return Arrow or raise exception."""
    return enforce_type(arrow_or_none(value), Arrow)


def timezone_or_raise(value: Any) -> tzinfo:
    """Return tzinfo or raise exception."""
    return enforce_type(timezone_or_none(value), tzinfo)


def dict_or_raise(value: Any) -> Dict[Any, Any]:
    """Return dict or raise exception."""
    return enforce_type(value, dict)


def dict_or_none(value: Any) -> Optional[Dict[Any, Any]]:
    """Return dict or None."""
    return value_or_none(value, dict)


def new_credentials(
    client_id: str, consumer_secret: str, data: Dict[str, Any]
) -> Credentials:
    """Create Credentials from config and json."""
    return Credentials(
        access_token=str_or_raise(data.get("access_token")),
        token_expiry=arrow.utcnow().timestamp + data.get("expires_in"),
        token_type=str_or_raise(data.get("token_type")),
        refresh_token=str_or_raise(data.get("refresh_token")),
        userid=int_or_raise(data.get("userid")),
        client_id=str_or_raise(client_id),
        consumer_secret=str_or_raise(consumer_secret),
    )


def new_user_get_device_device(data: dict) -> UserGetDeviceDevice:
    """Create GetDeviceDevice from json."""
    return UserGetDeviceDevice(
        type=str_or_raise(data.get("type")),
        model=str_or_raise(data.get("model")),
        battery=str_or_raise(data.get("battery")),
        deviceid=str_or_raise(data.get("deviceid")),
        timezone=timezone_or_raise(data.get("timezone")),
    )


def new_user_get_device_response(data: dict) -> UserGetDeviceResponse:
    """Create GetDeviceResponse from json."""
    return UserGetDeviceResponse(
        devices=tuple(
            new_user_get_device_device(device) for device in data.get("devices", ())
        )
    )


def new_notify_list_profile(data: dict) -> NotifyListProfile:
    """Create ListSubscriptionProfile from json."""
    return NotifyListProfile(
        appli=new_notify_appli(data.get("appli")),
        callbackurl=str_or_raise(data.get("callbackurl")),
        expires=arrow_or_raise(data.get("expires")),
        comment=str_or_none(data.get("comment")),
    )


def new_notify_list_response(data: dict) -> NotifyListResponse:
    """Create NotifyListResponse from json."""
    return NotifyListResponse(
        profiles=tuple(
            new_notify_list_profile(profile) for profile in data.get("profiles", ())
        )
    )


def new_notify_get_response(data: dict) -> NotifyGetResponse:
    """Create NotifyGetResponse from json."""
    return NotifyGetResponse(
        appli=new_notify_appli(data.get("appli")),
        callbackurl=str_or_raise(data.get("callbackurl")),
        comment=str_or_none(data.get("comment")),
    )


def new_sleep_timestamp(data: Optional[Dict[Any, Any]]) -> Optional[SleepGetTimestamp]:
    """Create SleepTimestamp from json."""
    if data is None:
        return data

    return SleepGetTimestamp(arrow_or_raise(data.get("$timestamp")))


def new_sleep_get_serie(data: dict) -> SleepGetSerie:
    """Create GetSleepSerie from json."""
    return SleepGetSerie(
        enddate=arrow_or_raise(data.get("enddate")),
        startdate=arrow_or_raise(data.get("startdate")),
        state=new_sleep_state(data.get("state")),
        hr=new_sleep_timestamp(dict_or_none(data.get("hr"))),
        rr=new_sleep_timestamp(dict_or_none(data.get("rr"))),
    )


def new_sleep_get_response(data: dict) -> SleepGetResponse:
    """Create GetSleepResponse from json."""
    return SleepGetResponse(
        model=new_sleep_model(data.get("model")),
        series=tuple(new_sleep_get_serie(serie) for serie in data.get("series", ())),
    )


def new_get_sleep_summary_data(data: dict) -> GetSleepSummaryData:
    """Create GetSleepSummarySerie from json."""
    return GetSleepSummaryData(
        remsleepduration=int_or_none(data.get("remsleepduration")),
        wakeupduration=int_or_none(data.get("wakeupduration")),
        lightsleepduration=int_or_none(data.get("lightsleepduration")),
        deepsleepduration=int_or_none(data.get("deepsleepduration")),
        wakeupcount=int_or_none(data.get("wakeupcount")),
        durationtosleep=int_or_none(data.get("durationtosleep")),
        durationtowakeup=int_or_none(data.get("durationtowakeup")),
        hr_average=int_or_none(data.get("hr_average")),
        hr_min=int_or_none(data.get("hr_min")),
        hr_max=int_or_none(data.get("hr_max")),
        rr_average=int_or_none(data.get("rr_average")),
        rr_min=int_or_none(data.get("rr_min")),
        rr_max=int_or_none(data.get("rr_max")),
    )


def new_get_sleep_summary_serie(data: dict) -> GetSleepSummarySerie:
    """Create GetSleepSummarySerie from json."""
    timezone = timezone_or_raise(data.get("timezone"))

    return GetSleepSummarySerie(
        date=arrow_or_raise(data.get("date")).replace(tzinfo=timezone),
        enddate=arrow_or_raise(data.get("enddate")).replace(tzinfo=timezone),
        model=new_sleep_model(data.get("model")),
        modified=arrow_or_raise(data.get("modified")).replace(tzinfo=timezone),
        startdate=arrow_or_raise(data.get("startdate")).replace(tzinfo=timezone),
        timezone=timezone,
        data=new_get_sleep_summary_data(dict_or_raise(data.get("data"))),
    )


def new_sleep_get_summary_response(data: dict) -> SleepGetSummaryResponse:
    """Create GetSleepSummaryResponse from json."""
    return SleepGetSummaryResponse(
        more=bool_or_raise(data.get("more")),
        offset=int_or_raise(data.get("offset")),
        series=tuple(
            new_get_sleep_summary_serie(serie) for serie in data.get("series", ())
        ),
    )


def new_measure_get_meas_measure(data: dict) -> MeasureGetMeasMeasure:
    """Create GetMeasMeasure from json."""
    return MeasureGetMeasMeasure(
        value=int_or_raise(data.get("value")),
        type=new_measure_type(data.get("type")),
        unit=int_or_raise(data.get("unit")),
    )


def new_measure_get_meas_group(data: dict, timezone: tzinfo) -> MeasureGetMeasGroup:
    """Create GetMeasGroup from json."""
    return MeasureGetMeasGroup(
        grpid=int_or_raise(data.get("grpid")),
        attrib=new_measure_group_attrib(data.get("attrib")),
        date=arrow_or_raise(data.get("date")).replace(tzinfo=timezone),
        created=arrow_or_raise(data.get("created")).replace(tzinfo=timezone),
        category=new_measure_category(data.get("category")),
        deviceid=data.get("deviceid"),
        measures=tuple(
            new_measure_get_meas_measure(measure)
            for measure in data.get("measures", ())
        ),
    )


def new_measure_get_meas_response(data: dict) -> MeasureGetMeasResponse:
    """Create GetMeasResponse from json."""
    timezone = timezone_or_raise(data.get("timezone"))

    return MeasureGetMeasResponse(
        measuregrps=tuple(
            new_measure_get_meas_group(group, timezone)
            for group in data.get("measuregrps", ())
        ),
        more=data.get("more"),
        offset=data.get("offset"),
        timezone=timezone,
        updatetime=arrow_or_raise(data.get("updatetime")).replace(tzinfo=timezone),
    )


def new_measure_get_activity_activity(data: dict) -> MeasureGetActivityActivity:
    """Create GetActivityActivity from json."""
    timezone = timezone_or_raise(data.get("timezone"))

    return MeasureGetActivityActivity(
        date=arrow_or_raise(data.get("date")).replace(tzinfo=timezone),
        timezone=timezone,
        deviceid=str_or_none(data.get("deviceid")),
        brand=int_or_raise(data.get("brand")),
        is_tracker=bool_or_raise(data.get("is_tracker")),
        steps=int_or_none(data.get("steps")),
        distance=float_or_raise(data.get("distance")),
        elevation=float_or_raise(data.get("elevation")),
        soft=int_or_none(data.get("soft")),
        moderate=int_or_none(data.get("moderate")),
        intense=int_or_none(data.get("intense")),
        active=int_or_none(data.get("active")),
        calories=float_or_raise(data.get("calories")),
        totalcalories=float_or_raise(data.get("totalcalories")),
        hr_average=int_or_none(data.get("hr_average")),
        hr_min=int_or_none(data.get("hr_min")),
        hr_max=int_or_none(data.get("hr_max")),
        hr_zone_0=int_or_none(data.get("hr_zone_0")),
        hr_zone_1=int_or_none(data.get("hr_zone_1")),
        hr_zone_2=int_or_none(data.get("hr_zone_2")),
        hr_zone_3=int_or_none(data.get("hr_zone_3")),
    )


def new_measure_get_activity_response(data: dict) -> MeasureGetActivityResponse:
    """Create GetActivityResponse from json."""
    return MeasureGetActivityResponse(
        activities=tuple(
            new_measure_get_activity_activity(activity)
            for activity in data.get("activities", ())
        ),
        more=bool_or_raise(data.get("more")),
        offset=int_or_raise(data.get("offset")),
    )


AMBIGUOUS_GROUP_ATTRIBS = (
    MeasureGetMeasGroupAttrib.DEVICE_ENTRY_FOR_USER_AMBIGUOUS,
    MeasureGetMeasGroupAttrib.MANUAL_USER_DURING_ACCOUNT_CREATION,
)


class MeasureGroupAttribs:
    """Groups of MeasureGetMeasGroupAttrib."""

    ANY = tuple(enum_val for enum_val in MeasureGetMeasGroupAttrib)
    AMBIGUOUS = AMBIGUOUS_GROUP_ATTRIBS
    UNAMBIGUOUS = tuple(
        enum_val
        for enum_val in MeasureGetMeasGroupAttrib
        if enum_val not in AMBIGUOUS_GROUP_ATTRIBS
    )


class MeasureTypes:
    """Groups of MeasureType."""

    ANY = tuple(enum_val for enum_val in MeasureType)


def query_measure_groups(
    from_source: Union[
        MeasureGetMeasGroup, MeasureGetMeasResponse, Tuple[MeasureGetMeasGroup, ...]
    ],
    with_measure_type: Union[MeasureType, Tuple[MeasureType, ...]] = MeasureTypes.ANY,
    with_group_attrib: Union[
        MeasureGetMeasGroupAttrib, Tuple[MeasureGetMeasGroupAttrib, ...]
    ] = MeasureGroupAttribs.ANY,
) -> Tuple[MeasureGetMeasGroup, ...]:
    """Return a groups and measurements based on filters."""
    if isinstance(from_source, MeasureGetMeasResponse):
        iter_groups = cast(MeasureGetMeasResponse, from_source).measuregrps
    elif isinstance(from_source, MeasureGetMeasGroup):
        iter_groups = (cast(MeasureGetMeasGroup, from_source),)
    else:
        iter_groups = cast(Tuple[MeasureGetMeasGroup], from_source)

    if isinstance(with_measure_type, MeasureType):
        iter_measure_type = (cast(MeasureType, with_measure_type),)
    else:
        iter_measure_type = cast(Tuple[MeasureType], with_measure_type)

    if isinstance(with_group_attrib, MeasureGetMeasGroupAttrib):
        iter_group_attrib = (cast(MeasureGetMeasGroupAttrib, with_group_attrib),)
    else:
        iter_group_attrib = cast(Tuple[MeasureGetMeasGroupAttrib], with_group_attrib)

    groups = []
    for group in iter_groups:
        if group.attrib not in iter_group_attrib:
            continue

        measures = []
        for measure in group.measures:
            if measure.type not in iter_measure_type:
                continue

            measures.append(measure)

        groups.append(
            MeasureGetMeasGroup(
                attrib=group.attrib,
                category=group.category,
                created=group.created,
                date=group.date,
                deviceid=group.deviceid,
                grpid=group.grpid,
                measures=tuple(measures),
            )
        )

    return tuple(groups)


def get_measure_value(
    from_source: Union[
        MeasureGetMeasGroup, MeasureGetMeasResponse, Tuple[MeasureGetMeasGroup, ...]
    ],
    with_measure_type: Union[MeasureType, Tuple[MeasureType, ...]],
    with_group_attrib: Union[
        MeasureGetMeasGroupAttrib, Tuple[MeasureGetMeasGroupAttrib, ...]
    ] = MeasureGroupAttribs.ANY,
) -> Optional[float]:
    """Get the first value of a measure that meet the query requirements."""
    groups = query_measure_groups(from_source, with_measure_type, with_group_attrib)

    for group in groups:
        for measure in group.measures:
            return float(measure.value * pow(10, measure.unit))

    return None


class StatusException(Exception):
    """Status exception."""

    def __init__(self, status: Any):
        """Create instance."""
        super().__init__("Error code %s" % str(status))


class AuthFailedException(StatusException):
    """Withings status error code exception."""


class InvalidParamsException(StatusException):
    """Withings status error code exception."""


class UnauthorizedException(StatusException):
    """Withings status error code exception."""


class ErrorOccurredException(StatusException):
    """Withings status error code exception."""


class TimeoutException(StatusException):
    """Withings status error code exception."""


class BadStateException(StatusException):
    """Withings status error code exception."""


class TooManyRequestsException(StatusException):
    """Withings status error code exception."""


class UnknownStatusException(StatusException):
    """Unknown status code but it's still not successful."""


def response_body_or_raise(data: Any) -> Dict[str, Any]:
    """Parse withings response or raise exception."""
    parsed_response = dict_or_raise(data)
    status_any = parsed_response.get("status")
    status = int_or_none(status_any)

    if status is None:
        raise UnknownStatusException(status=status)
    if status in STATUS_SUCCESS:
        return cast(Dict[str, Any], parsed_response.get("body"))
    if status in STATUS_AUTH_FAILED:
        raise AuthFailedException(status=status)
    if status in STATUS_INVALID_PARAMS:
        raise InvalidParamsException(status=status)
    if status in STATUS_UNAUTHORIZED:
        raise UnauthorizedException(status=status)
    if status in STATUS_ERROR_OCCURRED:
        raise ErrorOccurredException(status=status)
    if status in STATUS_TIMEOUT:
        raise TimeoutException(status=status)
    if status in STATUS_BAD_STATE:
        raise BadStateException(status=status)
    if status in STATUS_TOO_MANY_REQUESTS:
        raise TooManyRequestsException(status=status)
    raise UnknownStatusException(status=status)
