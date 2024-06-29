"""
this file is for constant params for developer use only.
any constants in code that should be changeable by user via the API should be in the Jason params file.
any constant/param within this file is for developer use only and will not be changeable by users.
"""
from enum import Enum

DETECTOR_TYPES = {
    'APS_SYSTEM': "Windcoat",  # "22.1"
    'BMS_SYSTEM': "MAANAK",  # "MANUAL" "21.1"
    'TAMAR_DISPLAY': "User_deleted",  # "2.1"
    'LOADER_DISPLAY': "LOADER_DISPLAY",  # 1.11.1
    'GUNNER_DISPLAY': "GUNNER_DISPLAY"  # 1.10.1
}


class RangeMethod(Enum):
    UNKNOWN = 0
    CALCULATED = 1
    MEASURED = 2
    REPORTED = 3


class DetectionStatus(Enum):
    NONE = 0
    VALID_RECOGNIZED = 1
    VALID_NOT_RECOGNIZED = 2
    DELETED = 3
    CANCELED = 4
    MERGED = 5
    SPLIT = 6


class NogaScanState(Enum):
    OFF = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    FAILED = 3


class DetectionSpec(Enum):
    NOGA_STARE_NO_RANGE = 'NogaStareNoRange'
    MARKER = 'Marker'
    NOGA_STARE_CALC = 'NogaStareCalc'
    NOGA_SCAN_MEASURED = 'NogaScanMeasured'
    NOGA_SCAN_NO_RANGE = 'NogaScanNoRange'
    NOGA_SCAN_CALC = 'NogaScanCalc'
    DELETED = 'DELETED'
    APS_SYSTEM_DETECTION = 'APS_SYSTEM_DETECTION'
    APS_SYSTEM_THREAT = 'APS_SYSTEM_THREAT'
    APS_SYSTEM_TARGET = 'APS_SYSTEM_TARGET'


class DetectionType(Enum):
    DETECTION = 0
    THREAT = 1
    TARGET = 2


class SensorsName(Enum):
    MAANAK_ID = "BMS_SYSTEM"
    APS_ID = 'APS_SYSTEM'


WOW_CLASS_SCORE = 1
DEFAULT_HERTZ_WHEN_NO_ELAPSED_TIME = 9999999
