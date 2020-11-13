"""Common classes and functions."""

from datetime import tzinfo
from enum import Enum, IntEnum
import sys
import traceback
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)
from recordclass import RecordClass
import arrow
from arrow import Arrow
from dateutil import tz
from typing_extensions import Final

from .const import (
    STATUS_AUTH_FAILED,
    STATUS_BAD_STATE,
    STATUS_ERROR_OCCURRED,
    STATUS_INVALID_PARAMS,
    STATUS_SUCCESS,
    STATUS_TIMEOUT,
    STATUS_TOO_MANY_REQUESTS,
    STATUS_UNAUTHORIZED,
)

import yaml

def named_tuple(self, data):
    if hasattr(data, '_asdict'):
        d = data._asdict()
        if 'timezone' in d:
          d['timezone'] = str(d['timezone'])
        return self.represent_dict(d)
    return self.represent_list(data)

yaml.SafeDumper.yaml_multi_representers[tuple] = named_tuple

def record_class(self, data):
    return self.represent_dict(data)

yaml.SafeDumper.yaml_multi_representers[dict] = record_class

def object_repr(self, data):
    return self.represent_str(str(data))

yaml.SafeDumper.yaml_multi_representers[object] = object_repr

def yamlAdd(c):
  def dump(self, **kwargs):
    yaml.safe_dump(self._asdict(), sys.stdout, **kwargs)
  c.dump = dump
  return c

class SleepModel(IntEnum):
    """Sleep model."""

    TRACKER = 16
    SLEEP_MONITOR = 32


def new_sleep_model(value: Optional[int]) -> SleepModel:
    """Create enum based on primitive."""
    return cast(SleepModel, enum_or_raise(value, SleepModel))


class SleepState(IntEnum):
    """Sleep states."""

    AWAKE = 0
    LIGHT = 1
    DEEP = 2
    REM = 3


def new_sleep_state(value: Optional[int]) -> SleepState:
    """Create enum based on primitive."""
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
    """Create enum based on primitive."""
    return cast(
        MeasureGetMeasGroupAttrib, enum_or_raise(value, MeasureGetMeasGroupAttrib)
    )


class MeasureGetMeasGroupCategory(IntEnum):
    """Measure categories."""

    REAL = 1
    USER_OBJECTIVES = 2


def new_measure_category(value: Optional[int]) -> MeasureGetMeasGroupCategory:
    """Create enum based on primitive."""
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
    SPO2 = 54
    BODY_TEMPERATURE = 71
    SKIN_TEMPERATURE = 73
    MUSCLE_MASS = 76
    HYDRATION = 77
    BONE_MASS = 88
    PULSE_WAVE_VELOCITY = 91
    VO2_MAX = 123


def new_measure_type(value: Optional[int]) -> MeasureType:
    """Create enum based on primitive."""
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
    """Create enum based on primitive."""
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
    SNORING = "snoring"


class GetSleepSummaryField(Enum):
    """Fields for get sleep summary api call."""

    BREATHING_DISTURBANCES_INTENSITY = "breathing_disturbances_intensity"
    DEEP_SLEEP_DURATION = "deepsleepduration"
    DURATION_TO_SLEEP = "durationtosleep"
    DURATION_TO_WAKEUP = "durationtowakeup"
    HR_AVERAGE = "hr_average"
    HR_MAX = "hr_max"
    HR_MIN = "hr_min"
    LIGHT_SLEEP_DURATION = "lightsleepduration"
    REM_SLEEP_DURATION = "remsleepduration"
    RR_AVERAGE = "rr_average"
    RR_MAX = "rr_max"
    RR_MIN = "rr_min"
    SLEEP_SCORE = "sleep_score"
    SNORING = "snoring"
    SNORING_EPISODE_COUNT = "snoringepisodecount"
    WAKEUP_COUNT = "wakeupcount"
    WAKEUP_DURATION = "wakeupduration"


class AuthScope(Enum):
    """Authorization scopes."""

    USER_INFO = "user.info"
    USER_METRICS = "user.metrics"
    USER_ACTIVITY = "user.activity"
    USER_SLEEP_EVENTS = "user.sleepevents"


@yamlAdd
class UserGetDeviceDevice(NamedTuple):
    """UserGetDeviceDevice."""

    type: str
    model: str
    battery: str
    deviceid: str
    timezone: tzinfo


@yamlAdd
class UserGetDeviceResponse(NamedTuple):
    """UserGetDeviceResponse."""

    devices: Tuple[UserGetDeviceDevice, ...]


@yamlAdd
class SleepGetTimestampValue(NamedTuple):
    """SleepGetTimestampValue."""

    timestamp: Arrow
    value: int


@yamlAdd
class SleepGetSerie(NamedTuple):
    """SleepGetSerie."""

    enddate: Arrow
    startdate: Arrow
    state: SleepState
    hr: Tuple[SleepGetTimestampValue, ...]
    rr: Tuple[SleepGetTimestampValue, ...]
    snoring: Tuple[SleepGetTimestampValue, ...]


@yamlAdd
class SleepGetResponse(NamedTuple):
    """SleepGetResponse."""

    model: SleepModel
    series: Tuple[SleepGetSerie, ...]


@yamlAdd
class GetSleepSummaryData(NamedTuple):
    """GetSleepSummaryData."""

    breathing_disturbances_intensity: Optional[int]
    deepsleepduration: Optional[int]
    durationtosleep: Optional[int]
    durationtowakeup: Optional[int]
    hr_average: Optional[int]
    hr_max: Optional[int]
    hr_min: Optional[int]
    lightsleepduration: Optional[int]
    remsleepduration: Optional[int]
    rr_average: Optional[int]
    rr_max: Optional[int]
    rr_min: Optional[int]
    sleep_score: Optional[int]
    snoring: Optional[int]
    snoringepisodecount: Optional[int]
    wakeupcount: Optional[int]
    wakeupduration: Optional[int]


@yamlAdd
class GetSleepSummarySerie(NamedTuple):
    """GetSleepSummarySerie."""

    timezone: tzinfo
    model: SleepModel
    startdate: Arrow
    enddate: Arrow
    date: Arrow
    modified: Arrow
    data: GetSleepSummaryData


@yamlAdd
class SleepGetSummaryResponse(NamedTuple):
    """SleepGetSummaryResponse."""

    more: bool
    offset: int
    series: Tuple[GetSleepSummarySerie, ...]


@yamlAdd
class MeasureGetMeasMeasure(NamedTuple):
    """MeasureGetMeasMeasure."""

    type: MeasureType
    unit: int
    value: int


@yamlAdd
class MeasureGetMeasGroup(NamedTuple):
    """MeasureGetMeasGroup."""

    attrib: MeasureGetMeasGroupAttrib
    category: MeasureGetMeasGroupCategory
    created: Arrow
    date: Arrow
    deviceid: Optional[str]
    grpid: int
    measures: Tuple[MeasureGetMeasMeasure, ...]


@yamlAdd
class MeasureGetMeasResponse(NamedTuple):
    """MeasureGetMeasResponse."""

    measuregrps: Tuple[MeasureGetMeasGroup, ...]
    more: Optional[bool]
    offset: Optional[int]
    timezone: tzinfo
    updatetime: Arrow


#@yamlAdd
class MeasureGetActivityActivity(NamedTuple):
    """MeasureGetActivityActivity."""

    date: Arrow
    timezone: tzinfo
    deviceid: Optional[str]
    brand: int
    is_tracker: bool
    steps: Optional[int]
    distance: Optional[float]
    elevation: Optional[float]
    soft: Optional[int]
    moderate: Optional[int]
    intense: Optional[int]
    active: Optional[int]
    calories: Optional[float]
    totalcalories: float
    hr_average: Optional[int]
    hr_min: Optional[int]
    hr_max: Optional[int]
    hr_zone_0: Optional[int]
    hr_zone_1: Optional[int]
    hr_zone_2: Optional[int]
    hr_zone_3: Optional[int]


@yamlAdd
class MeasureGetActivityResponse(NamedTuple):
    """MeasureGetActivityResponse."""

    activities: Tuple[MeasureGetActivityActivity, ...]
    more: bool
    offset: int


class HeartModel(IntEnum):
    """Heart model."""

    BPM_CORE = 44
    MOVE_ECG = 91
    SCAN_WATCH = 93


def new_heart_model(value: Optional[int]) -> HeartModel:
    """Create enum based on primitive."""
    return cast(HeartModel, enum_or_raise(value, HeartModel))


class AfibClassification(IntEnum):
    """Atrial fibrillation classification"""

    NEGATIVE = 0
    POSITIVE = 1
    INCONCLUSIVE = 2


def new_afib_classification(value: Optional[int]) -> AfibClassification:
    """Create enum based on primitive."""
    return cast(AfibClassification, enum_or_raise(value, AfibClassification))


class HeartWearPosition(IntEnum):
    """Wear position of heart model."""

    RIGHT_WRIST = 0
    LEFT_WRIST = 1
    RIGHT_ARM = 2
    LEFT_ARM = 3
    RIGHT_FOOT = 4
    LEFT_FOOT = 5


def new_heart_wear_position(value: Optional[int]) -> HeartWearPosition:
    """Create enum based on primitive."""
    return cast(HeartWearPosition, enum_or_raise(value, HeartWearPosition))


@yamlAdd
class HeartGetResponse(NamedTuple):
    """HeartGetResponse."""

    signal: Tuple[int, ...]
    sampling_frequency: int
    wearposition: HeartWearPosition


@yamlAdd
class HeartListECG(NamedTuple):
    """HeartListECG."""

    signalid: int
    afib: AfibClassification


@yamlAdd
class HeartBloodPressure(NamedTuple):
    """HeartBloodPressure."""

    diastole: int
    systole: int


@yamlAdd
class HeartListSerie(RecordClass):
    """HeartListSerie"""

    ecg: Optional[HeartListECG]
    ecgvalues: Optional[HeartGetResponse]

    # blood pressure is optional as not all devices (e.g. Move ECG) collect it
    bloodpressure: Optional[HeartBloodPressure]

    heart_rate: int
    timestamp: Arrow
    model: HeartModel


@yamlAdd
class HeartListResponse(NamedTuple):
    """HeartListResponse."""

    more: bool
    offset: int
    series: Tuple[HeartListSerie, ...]


@yamlAdd
class Credentials(NamedTuple):
    """Credentials."""

    access_token: str
    token_expiry: int
    token_type: str
    refresh_token: str
    userid: int
    client_id: str
    consumer_secret: str


@yamlAdd
class NotifyListProfile(NamedTuple):
    """NotifyListProfile."""

    appli: NotifyAppli
    callbackurl: str
    expires: Optional[Arrow]
    comment: Optional[str]


@yamlAdd
class NotifyListResponse(NamedTuple):
    """NotifyListResponse."""

    profiles: Tuple[NotifyListProfile, ...]


@yamlAdd
class NotifyGetResponse(NamedTuple):
    """NotifyGetResponse."""

    appli: NotifyAppli
    callbackurl: str
    comment: Optional[str]


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
    """Return Arrow or None."""
    if value is None:
        return None

    return arrow.get(value)


def timezone_or_none(value: Any) -> Optional[tzinfo]:
    """Return tzinfo or None."""
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
        devices=_flexible_tuple_of(data.get("devices", ()), new_user_get_device_device)
    )


def new_notify_list_profile(data: dict) -> NotifyListProfile:
    """Create ListSubscriptionProfile from json."""
    return NotifyListProfile(
        appli=new_notify_appli(data.get("appli")),
        callbackurl=str_or_raise(data.get("callbackurl")),
        expires=arrow_or_none(data.get("expires")),
        comment=str_or_none(data.get("comment")),
    )


def new_notify_list_response(data: dict) -> NotifyListResponse:
    """Create NotifyListResponse from json."""
    return NotifyListResponse(
        profiles=_flexible_tuple_of(data.get("profiles", ()), new_notify_list_profile)
    )


def new_notify_get_response(data: dict) -> NotifyGetResponse:
    """Create NotifyGetResponse from json."""
    return NotifyGetResponse(
        appli=new_notify_appli(data.get("appli")),
        callbackurl=str_or_raise(data.get("callbackurl")),
        comment=str_or_none(data.get("comment")),
    )


def new_sleep_timestamps(
    data: Optional[Dict[Any, Any]]
) -> Tuple[SleepGetTimestampValue, ...]:
    """Create SleepTimestamp from json."""
    if data is None:
        return ()

    return tuple(
        SleepGetTimestampValue(arrow_or_raise(int(timestamp)), value)
        for timestamp, value in data.items()
    )


def new_sleep_get_serie(data: dict) -> SleepGetSerie:
    """Create GetSleepSerie from json."""
    return SleepGetSerie(
        enddate=arrow_or_raise(data.get("enddate")),
        startdate=arrow_or_raise(data.get("startdate")),
        state=new_sleep_state(data.get("state")),
        hr=new_sleep_timestamps(dict_or_none(data.get(GetSleepField.HR.value))),
        rr=new_sleep_timestamps(dict_or_none(data.get(GetSleepField.RR.value))),
        snoring=new_sleep_timestamps(
            dict_or_none(data.get(GetSleepField.SNORING.value))
        ),
    )


def new_sleep_get_response(data: dict) -> SleepGetResponse:
    """Create GetSleepResponse from json."""
    return SleepGetResponse(
        model=new_sleep_model(data.get("model")),
        series=_flexible_tuple_of(data.get("series", ()), new_sleep_get_serie),
    )


def new_get_sleep_summary_data(data: dict) -> GetSleepSummaryData:
    """Create GetSleepSummarySerie from json."""
    return GetSleepSummaryData(
        breathing_disturbances_intensity=int_or_none(
            data.get(GetSleepSummaryField.BREATHING_DISTURBANCES_INTENSITY.value)
        ),
        deepsleepduration=int_or_none(
            data.get(GetSleepSummaryField.DEEP_SLEEP_DURATION.value)
        ),
        durationtosleep=int_or_none(
            data.get(GetSleepSummaryField.DURATION_TO_SLEEP.value)
        ),
        durationtowakeup=int_or_none(
            data.get(GetSleepSummaryField.DURATION_TO_WAKEUP.value)
        ),
        hr_average=int_or_none(data.get(GetSleepSummaryField.HR_AVERAGE.value)),
        hr_max=int_or_none(data.get(GetSleepSummaryField.HR_MAX.value)),
        hr_min=int_or_none(data.get(GetSleepSummaryField.HR_MIN.value)),
        lightsleepduration=int_or_none(
            data.get(GetSleepSummaryField.LIGHT_SLEEP_DURATION.value)
        ),
        remsleepduration=int_or_none(
            data.get(GetSleepSummaryField.REM_SLEEP_DURATION.value)
        ),
        rr_average=int_or_none(data.get(GetSleepSummaryField.RR_AVERAGE.value)),
        rr_max=int_or_none(data.get(GetSleepSummaryField.RR_MAX.value)),
        rr_min=int_or_none(data.get(GetSleepSummaryField.RR_MIN.value)),
        sleep_score=int_or_none(data.get(GetSleepSummaryField.SLEEP_SCORE.value)),
        snoring=int_or_none(data.get(GetSleepSummaryField.SNORING.value)),
        snoringepisodecount=int_or_none(
            data.get(GetSleepSummaryField.SNORING_EPISODE_COUNT.value)
        ),
        wakeupcount=int_or_none(data.get(GetSleepSummaryField.WAKEUP_COUNT.value)),
        wakeupduration=int_or_none(
            data.get(GetSleepSummaryField.WAKEUP_DURATION.value)
        ),
    )


def new_get_sleep_summary_serie(data: dict) -> GetSleepSummarySerie:
    """Create GetSleepSummarySerie from json."""
    timezone: Final = timezone_or_raise(data.get("timezone"))

    return GetSleepSummarySerie(
        date=arrow_or_raise(data.get("date")).to(timezone),
        enddate=arrow_or_raise(data.get("enddate")).to(timezone),
        model=new_sleep_model(data.get("model")),
        modified=arrow_or_raise(data.get("modified")).to(timezone),
        startdate=arrow_or_raise(data.get("startdate")).to(timezone),
        timezone=timezone,
        data=new_get_sleep_summary_data(dict_or_raise(data.get("data"))),
    )


def new_sleep_get_summary_response(data: dict) -> SleepGetSummaryResponse:
    """Create GetSleepSummaryResponse from json."""
    return SleepGetSummaryResponse(
        more=bool_or_raise(data.get("more")),
        offset=int_or_raise(data.get("offset")),
        series=_flexible_tuple_of(data.get("series", ()), new_get_sleep_summary_serie),
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
        date=arrow_or_raise(data.get("date")).to(timezone),
        created=arrow_or_raise(data.get("created")).to(timezone),
        category=new_measure_category(data.get("category")),
        deviceid=data.get("deviceid"),
        measures=_flexible_tuple_of(
            data.get("measures", ()), new_measure_get_meas_measure
        ),
    )


def _flexible_tuple_of(
    items: Iterable[Any], fun: Callable[[Any], GenericType]
) -> Tuple[GenericType, ...]:
    """Create a tuple of objects resolved through lambda.

    If the lambda throws an exception, the resulting item will be ignored.
    """
    new_items: Final[List[GenericType]] = []
    for item in items:
        try:
            new_items.append(fun(item))
        except Exception:  # pylint:disable=broad-except
            print(
                "Warning: Failed to convert object. See exception for details.",
                traceback.format_exc(),
            )

    return tuple(new_items)


def new_measure_get_meas_response(data: dict) -> MeasureGetMeasResponse:
    """Create GetMeasResponse from json."""
    timezone: Final = timezone_or_raise(data.get("timezone"))

    return MeasureGetMeasResponse(
        measuregrps=_flexible_tuple_of(
            data.get("measuregrps", ()),
            lambda group: new_measure_get_meas_group(group, timezone),
        ),
        more=data.get("more"),
        offset=data.get("offset"),
        timezone=timezone,
        updatetime=arrow_or_raise(data.get("updatetime")).to(timezone),
    )


def new_measure_get_activity_activity(data: dict) -> MeasureGetActivityActivity:
    """Create GetActivityActivity from json."""
    timezone: Final = timezone_or_raise(data.get("timezone"))

    return MeasureGetActivityActivity(
        date=arrow_or_raise(data.get("date")).to(timezone),
        timezone=timezone,
        deviceid=str_or_none(data.get("deviceid")),
        brand=int_or_raise(data.get("brand")),
        is_tracker=bool_or_raise(data.get("is_tracker")),
        steps=int_or_none(data.get(GetActivityField.STEPS.value)),
        distance=float_or_raise(data.get(GetActivityField.DISTANCE.value)),
        elevation=float_or_raise(data.get(GetActivityField.ELEVATION.value)),
        soft=int_or_none(data.get(GetActivityField.SOFT.value)),
        moderate=int_or_none(data.get(GetActivityField.MODERATE.value)),
        intense=int_or_none(data.get(GetActivityField.INTENSE.value)),
        active=int_or_none(data.get(GetActivityField.ACTIVE.value)),
        calories=float_or_raise(data.get(GetActivityField.CALORIES.value)),
        totalcalories=float_or_raise(data.get(GetActivityField.TOTAL_CALORIES.value)),
        hr_average=int_or_none(data.get(GetActivityField.HR_AVERAGE.value)),
        hr_min=int_or_none(data.get(GetActivityField.HR_MIN.value)),
        hr_max=int_or_none(data.get(GetActivityField.HR_MAX.value)),
        hr_zone_0=int_or_none(data.get(GetActivityField.HR_ZONE_0.value)),
        hr_zone_1=int_or_none(data.get(GetActivityField.HR_ZONE_1.value)),
        hr_zone_2=int_or_none(data.get(GetActivityField.HR_ZONE_2.value)),
        hr_zone_3=int_or_none(data.get(GetActivityField.HR_ZONE_3.value)),
    )


def new_measure_get_activity_response(data: dict) -> MeasureGetActivityResponse:
    """Create GetActivityResponse from json."""
    return MeasureGetActivityResponse(
        activities=_flexible_tuple_of(
            data.get("activities", ()), new_measure_get_activity_activity
        ),
        more=bool_or_raise(data.get("more")),
        offset=int_or_raise(data.get("offset")),
    )


AMBIGUOUS_GROUP_ATTRIBS: Final = (
    MeasureGetMeasGroupAttrib.DEVICE_ENTRY_FOR_USER_AMBIGUOUS,
    MeasureGetMeasGroupAttrib.MANUAL_USER_DURING_ACCOUNT_CREATION,
)


class MeasureGroupAttribs:
    """Groups of MeasureGetMeasGroupAttrib."""

    ANY: Final = tuple(enum_val for enum_val in MeasureGetMeasGroupAttrib)
    AMBIGUOUS: Final = AMBIGUOUS_GROUP_ATTRIBS
    UNAMBIGUOUS: Final = tuple(
        enum_val
        for enum_val in MeasureGetMeasGroupAttrib
        if enum_val not in AMBIGUOUS_GROUP_ATTRIBS
    )


class MeasureTypes:
    """Groups of MeasureType."""

    ANY: Final = tuple(enum_val for enum_val in MeasureType)


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

    return tuple(
        MeasureGetMeasGroup(
            attrib=group.attrib,
            category=group.category,
            created=group.created,
            date=group.date,
            deviceid=group.deviceid,
            grpid=group.grpid,
            measures=tuple(
                measure
                for measure in group.measures
                if measure.type in iter_measure_type
            ),
        )
        for group in iter_groups
        if group.attrib in iter_group_attrib
    )


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
    groups: Final = query_measure_groups(
        from_source, with_measure_type, with_group_attrib
    )

    return next(
        iter(
            tuple(
                float(measure.value * pow(10, measure.unit))
                for group in groups
                for measure in group.measures
            )
        ),
        None,
    )


def new_heart_get_response(data: dict) -> HeartGetResponse:
    """Create GetSleepResponse from json."""
    return HeartGetResponse(
        signal=tuple(sample for sample in data.get("signal", ())),
        sampling_frequency=int_or_raise(data.get("sampling_frequency")),
        wearposition=new_heart_wear_position(data.get("wearposition")),
    )


def new_heart_list_ecg(data: dict) -> HeartListECG:
    """Create HeartListECG from json."""
    if data and 'signalid' in data:
      return HeartListECG(
          signalid=int_or_none(data.get("signalid")),
          afib=new_afib_classification(data.get("afib")),
      )
    else:
      return None


def new_heart_blood_pressure(
    data: Optional[Dict[Any, Any]]
) -> Optional[HeartBloodPressure]:
    """Create HeartBloodPressure from json."""
    if data is None:
        return data

    return HeartBloodPressure(
        diastole=int_or_raise(data.get("diastole")),
        systole=int_or_raise(data.get("systole")),
    )


def new_heart_list_serie(data: dict) -> HeartListSerie:
    """Create HeartListSerie from json."""
    return HeartListSerie(
        model=new_heart_model(int_or_raise(data.get("model"))),
        ecg=new_heart_list_ecg(dict_or_none(data.get("ecg"))),
        ecgvalues=None,
        bloodpressure=new_heart_blood_pressure(dict_or_none(data.get("bloodpressure"))),
        heart_rate=int_or_none(data.get("heart_rate")),
        timestamp=arrow_or_raise((int_or_raise(data.get("timestamp")))),
    )


def new_heart_list_response(data: dict) -> HeartListResponse:
    """Create HeartListResponse from json."""
    series = data['series']
    series = [s for s in series if 'ecg' in s]
    return HeartListResponse(
        more=bool_or_raise(data.get("more")),
        offset=int_or_raise(data.get("offset")),
        series=_flexible_tuple_of(data.get("series", ()), new_heart_list_serie),
    )


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
    parsed_response: Final = dict_or_raise(data)
    status_any: Final = parsed_response.get("status")
    status: Final = int_or_none(status_any)

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
