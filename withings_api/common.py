"""Common classes and functions."""
from dataclasses import dataclass
from datetime import tzinfo
from enum import Enum, IntEnum
import logging
from typing import Any, Dict, Optional, Tuple, Type, TypeVar, Union, cast

import arrow
from arrow import Arrow
from dateutil import tz
from dateutil.tz import tzlocal
from pydantic import BaseModel, Field, validator
from typing_extensions import Final

from .const import (
    LOG_NAMESPACE,
    STATUS_AUTH_FAILED,
    STATUS_BAD_STATE,
    STATUS_ERROR_OCCURRED,
    STATUS_INVALID_PARAMS,
    STATUS_SUCCESS,
    STATUS_TIMEOUT,
    STATUS_TOO_MANY_REQUESTS,
    STATUS_UNAUTHORIZED,
)

_LOGGER = logging.getLogger(LOG_NAMESPACE)
_GenericType = TypeVar("_GenericType")


def to_enum(
    enum_class: Type[_GenericType], value: Any, default_value: _GenericType
) -> _GenericType:
    """Attempt to convert a value to an enum."""
    try:
        return enum_class(value)  # type: ignore
    except ValueError:
        _LOGGER.warning(
            "Unsupported %s value %s. Replacing with UNKNOWN value %s. Please report this warning to the developer to ensure proper support.",
            str(enum_class),
            value,
            str(default_value),
        )
        return default_value


class ConfiguredBaseModel(BaseModel):
    """An already configured pydantic model."""

    class Config:
        """Config for pydantic model."""

        ignore_extra: Final = True
        allow_extra: Final = False
        allow_mutation: Final = False


class TimeZone(tzlocal):
    """Subclass of tzinfo for parsing timezones."""

    @classmethod
    def __get_validators__(cls) -> Any:
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> tzinfo:
        """Convert input to the desired object."""
        if isinstance(value, tzinfo):
            return value
        if isinstance(value, str):
            timezone: Final = tz.gettz(value)
            if timezone:
                return timezone
            raise ValueError(f"Invalid timezone provided {value}")

        raise TypeError("string or tzinfo required")


class ArrowType(Arrow):  # type: ignore
    """Subclass of Arrow for parsing dates."""

    @classmethod
    def __get_validators__(cls) -> Any:
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> Arrow:
        """Convert input to the desired object."""
        if isinstance(value, str):
            if value.isdigit():
                return arrow.get(int(value))
            return arrow.get(value)
        if isinstance(value, int):
            return arrow.get(value)
        if isinstance(value, (Arrow, ArrowType)):
            return value

        raise TypeError("string or int required")


class SleepModel(IntEnum):
    """Sleep model."""

    UNKNOWN = -999999
    TRACKER = 16
    SLEEP_MONITOR = 32


class SleepState(IntEnum):
    """Sleep states."""

    UNKNOWN = -999999
    AWAKE = 0
    LIGHT = 1
    DEEP = 2
    REM = 3


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


class MeasureGetMeasGroupCategory(IntEnum):
    """Measure categories."""

    UNKNOWN = -999999
    REAL = 1
    USER_OBJECTIVES = 2


class MeasureType(IntEnum):
    """Measure types."""

    UNKNOWN = -999999
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


class NotifyAppli(IntEnum):
    """Data to notify_subscribe to."""

    UNKNOWN = -999999
    WEIGHT = 1
    CIRCULATORY = 4
    ACTIVITY = 16
    SLEEP = 44
    USER = 46
    BED_IN = 50
    BED_OUT = 51


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


class UserGetDeviceDevice(ConfiguredBaseModel):
    """UserGetDeviceDevice."""

    type: str
    model: str
    battery: str
    deviceid: str
    timezone: TimeZone


class UserGetDeviceResponse(ConfiguredBaseModel):
    """UserGetDeviceResponse."""

    devices: Tuple[UserGetDeviceDevice, ...]


class SleepGetTimestampValue(ConfiguredBaseModel):
    """SleepGetTimestampValue."""

    timestamp: ArrowType
    value: int


class SleepGetSerie(ConfiguredBaseModel):
    """SleepGetSerie."""

    enddate: ArrowType
    startdate: ArrowType
    state: SleepState
    hr: Tuple[SleepGetTimestampValue, ...] = ()  # pylint: disable=invalid-name
    rr: Tuple[SleepGetTimestampValue, ...] = ()  # pylint: disable=invalid-name
    snoring: Tuple[SleepGetTimestampValue, ...] = ()

    @validator("hr", pre=True)
    @classmethod
    def _hr_to_tuple(cls, value: Dict[str, int]) -> Tuple:
        return SleepGetSerie._timestamp_value_to_object(value)

    @validator("rr", pre=True)
    @classmethod
    def _rr_to_tuple(cls, value: Dict[str, int]) -> Tuple:
        return SleepGetSerie._timestamp_value_to_object(value)

    @validator("snoring", pre=True)
    @classmethod
    def _snoring_to_tuple(cls, value: Dict[str, int]) -> Tuple:
        return SleepGetSerie._timestamp_value_to_object(value)

    @classmethod
    def _timestamp_value_to_object(
        cls, value: Any
    ) -> Tuple[SleepGetTimestampValue, ...]:
        if not value:
            return ()
        if isinstance(value, dict):
            return tuple(
                [
                    SleepGetTimestampValue(timestamp=item_key, value=item_value)
                    for item_key, item_value in value.items()
                ]
            )

        return cast(Tuple[SleepGetTimestampValue, ...], value)

    @validator("state", pre=True)
    @classmethod
    def _state_to_enum(cls, value: Any) -> SleepState:
        return to_enum(SleepState, value, SleepState.UNKNOWN)


class SleepGetResponse(ConfiguredBaseModel):
    """SleepGetResponse."""

    model: SleepModel
    series: Tuple[SleepGetSerie, ...]

    @validator("model", pre=True)
    @classmethod
    def _model_to_enum(cls, value: Any) -> SleepModel:
        return to_enum(SleepModel, value, SleepModel.UNKNOWN)


class GetSleepSummaryData(
    ConfiguredBaseModel
):  # pylint: disable=too-many-instance-attributes
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


class GetSleepSummarySerie(ConfiguredBaseModel):
    """GetSleepSummarySerie."""

    timezone: TimeZone
    model: SleepModel
    startdate: ArrowType
    enddate: ArrowType
    date: ArrowType
    modified: ArrowType
    data: GetSleepSummaryData
    id: Optional[int] = None

    @validator("startdate")
    @classmethod
    def _set_timezone_on_startdate(
        cls, value: ArrowType, values: Dict[str, Any]
    ) -> Arrow:
        return cast(Arrow, value.to(values["timezone"]))

    @validator("enddate")
    @classmethod
    def _set_timezone_on_enddate(
        cls, value: ArrowType, values: Dict[str, Any]
    ) -> Arrow:
        return cast(Arrow, value.to(values["timezone"]))

    @validator("date")
    @classmethod
    def _set_timezone_on_date(cls, value: ArrowType, values: Dict[str, Any]) -> Arrow:
        return cast(Arrow, value.to(values["timezone"]))

    @validator("modified")
    @classmethod
    def _set_timezone_on_modified(
        cls, value: ArrowType, values: Dict[str, Any]
    ) -> Arrow:
        return cast(Arrow, value.to(values["timezone"]))

    @validator("model", pre=True)
    @classmethod
    def _model_to_enum(cls, value: Any) -> SleepModel:
        return to_enum(SleepModel, value, SleepModel.UNKNOWN)


class SleepGetSummaryResponse(ConfiguredBaseModel):
    """SleepGetSummaryResponse."""

    more: bool
    offset: int
    series: Tuple[GetSleepSummarySerie, ...]


class MeasureGetMeasMeasure(ConfiguredBaseModel):
    """MeasureGetMeasMeasure."""

    type: MeasureType
    unit: int
    value: int

    @validator("type", pre=True)
    @classmethod
    def _type_to_enum(cls, value: Any) -> MeasureType:
        return to_enum(MeasureType, value, MeasureType.UNKNOWN)


class MeasureGetMeasGroup(ConfiguredBaseModel):
    """MeasureGetMeasGroup."""

    attrib: MeasureGetMeasGroupAttrib
    category: MeasureGetMeasGroupCategory
    created: ArrowType
    date: ArrowType
    deviceid: Optional[str]
    grpid: int
    measures: Tuple[MeasureGetMeasMeasure, ...]

    @validator("attrib", pre=True)
    @classmethod
    def _attrib_to_enum(cls, value: Any) -> MeasureGetMeasGroupAttrib:
        return to_enum(
            MeasureGetMeasGroupAttrib, value, MeasureGetMeasGroupAttrib.UNKNOWN
        )

    @validator("category", pre=True)
    @classmethod
    def _category_to_enum(cls, value: Any) -> MeasureGetMeasGroupCategory:
        return to_enum(
            MeasureGetMeasGroupCategory, value, MeasureGetMeasGroupCategory.UNKNOWN
        )


class MeasureGetMeasResponse(ConfiguredBaseModel):
    """MeasureGetMeasResponse."""

    measuregrps: Tuple[MeasureGetMeasGroup, ...]
    more: Optional[bool]
    offset: Optional[int]
    timezone: TimeZone
    updatetime: ArrowType

    @validator("updatetime")
    @classmethod
    def _set_timezone_on_updatetime(
        cls, value: ArrowType, values: Dict[str, Any]
    ) -> Arrow:
        return cast(Arrow, value.to(values["timezone"]))


class MeasureGetActivityActivity(
    BaseModel
):  # pylint: disable=too-many-instance-attributes
    """MeasureGetActivityActivity."""

    date: ArrowType
    timezone: TimeZone
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


class MeasureGetActivityResponse(ConfiguredBaseModel):
    """MeasureGetActivityResponse."""

    activities: Tuple[MeasureGetActivityActivity, ...]
    more: bool
    offset: int


class HeartModel(IntEnum):
    """Heart model."""

    UNKNOWN = -999999
    BPM_CORE = 44
    MOVE_ECG = 91


class AfibClassification(IntEnum):
    """Atrial fibrillation classification"""

    UNKNOWN = -999999
    NEGATIVE = 0
    POSITIVE = 1
    INCONCLUSIVE = 2


class HeartWearPosition(IntEnum):
    """Wear position of heart model."""

    UNKNOWN = -999999
    RIGHT_WRIST = 0
    LEFT_WRIST = 1
    RIGHT_ARM = 2
    LEFT_ARM = 3
    RIGHT_FOOT = 4
    LEFT_FOOT = 5


class HeartGetResponse(ConfiguredBaseModel):
    """HeartGetResponse."""

    signal: Tuple[int, ...]
    sampling_frequency: int
    wearposition: HeartWearPosition

    @validator("wearposition", pre=True)
    @classmethod
    def _wearposition_to_enum(cls, value: Any) -> HeartWearPosition:
        return to_enum(HeartWearPosition, value, HeartWearPosition.UNKNOWN)


class HeartListECG(ConfiguredBaseModel):
    """HeartListECG."""

    signalid: int
    afib: AfibClassification

    @validator("afib", pre=True)
    @classmethod
    def _afib_to_enum(cls, value: Any) -> AfibClassification:
        return to_enum(AfibClassification, value, AfibClassification.UNKNOWN)


class HeartBloodPressure(ConfiguredBaseModel):
    """HeartBloodPressure."""

    diastole: int
    systole: int


class HeartListSerie(ConfiguredBaseModel):
    """HeartListSerie"""

    ecg: HeartListECG

    heart_rate: int
    timestamp: ArrowType
    model: HeartModel

    # blood pressure is optional as not all devices (e.g. Move ECG) collect it
    bloodpressure: Optional[HeartBloodPressure] = None

    deviceid: Optional[str] = None

    @validator("model", pre=True)
    @classmethod
    def _model_to_enum(cls, value: Any) -> HeartModel:
        return to_enum(HeartModel, value, HeartModel.UNKNOWN)


class HeartListResponse(ConfiguredBaseModel):
    """HeartListResponse."""

    more: bool
    offset: int
    series: Tuple[HeartListSerie, ...]


@dataclass(frozen=True)
class Credentials:
    """Credentials."""

    access_token: str
    token_expiry: int
    token_type: str
    refresh_token: str
    userid: int
    client_id: str
    consumer_secret: str


class Credentials2(ConfiguredBaseModel):
    """Credentials."""

    access_token: str
    token_type: str
    refresh_token: str
    userid: int
    client_id: str
    consumer_secret: str
    expires_in: int
    created: ArrowType = Field(default_factory=arrow.utcnow)

    @property
    def token_expiry(self) -> int:
        """Get the token expiry."""
        return cast(int, self.created.shift(seconds=self.expires_in).timestamp)


CredentialsType = Union[Credentials, Credentials2]


def maybe_upgrade_credentials(value: CredentialsType) -> Credentials2:
    """Upgrade older versions of credentials to the newer signature."""
    if isinstance(value, Credentials2):
        return value

    creds = cast(Credentials, value)
    return Credentials2(
        access_token=creds.access_token,
        token_type=creds.token_type,
        refresh_token=creds.refresh_token,
        userid=creds.userid,
        client_id=creds.client_id,
        consumer_secret=creds.consumer_secret,
        expires_in=creds.token_expiry - arrow.utcnow().timestamp,
    )


class NotifyListProfile(ConfiguredBaseModel):
    """NotifyListProfile."""

    appli: NotifyAppli
    callbackurl: str
    expires: Optional[ArrowType]
    comment: Optional[str]

    @validator("appli", pre=True)
    @classmethod
    def _appli_to_enum(cls, value: Any) -> NotifyAppli:
        return to_enum(NotifyAppli, value, NotifyAppli.UNKNOWN)


class NotifyListResponse(ConfiguredBaseModel):
    """NotifyListResponse."""

    profiles: Tuple[NotifyListProfile, ...]


class NotifyGetResponse(ConfiguredBaseModel):
    """NotifyGetResponse."""

    appli: NotifyAppli
    callbackurl: str
    comment: Optional[str]

    @validator("appli", pre=True)
    @classmethod
    def _appli_to_enum(cls, value: Any) -> NotifyAppli:
        return to_enum(NotifyAppli, value, NotifyAppli.UNKNOWN)


class UnexpectedTypeException(Exception):
    """Thrown when encountering an unexpected type."""

    def __init__(self, value: Any, expected: Type[_GenericType]):
        """Initialize."""
        super().__init__(
            'Expected of "%s" to be "%s" but was "%s."' % (value, expected, type(value))
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
    if not isinstance(data, dict):
        raise UnexpectedTypeException(data, dict)

    parsed_response: Final = cast(dict, data)
    status: Final = parsed_response.get("status")

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
