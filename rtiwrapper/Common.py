import ctypes
import enum
import time
import xml.etree.ElementTree as ET
# from collections import deque
import queue

# Queues:
detectionQueue = queue.Queue(maxsize=3000)  # deque([], maxlen=3000)
detectionLocationQueue = queue.Queue(maxsize=3000)  # deque([], maxlen=3000)
detectionElectronicWarfareQueue = queue.Queue(maxsize=3000)  # deque([], maxlen=3000)
detectionOptronicsQueue = queue.Queue(maxsize=3000)  # deque([], maxlen=3000)
detectionRadarQueue = queue.Queue(maxsize=3000)  # deque([], maxlen=3000)
PositionQueue = queue.Queue(maxsize=3000)  # deque([], maxlen=3000)
DetectionApsQueue = queue.Queue(maxsize=3000)  # deque([], maxlen=3000)
RotMountQueue = queue.Queue(maxsize=3000)  # deque([], maxlen=3000)
RotMountStartScanQueue = queue.Queue(maxsize=3000)  # deque([], maxlen=3000)
RotMountStopScanQueue = queue.Queue(maxsize=3000)  # deque([], maxlen=3000)
tacticalSensitivityQueue = queue.Queue(maxsize=3000)  # deque([], maxlen=3000)

functionsHandleSubList = []  # list to hold all functions handle of subscribes


# Constants

class configDefsKeysEnum():  # keys in configDefs.json
    FUSION_ALGO_PRAMS_FILE_PATH = "fusionAlgoPramsFilePath"
    BARAK_DATASET = "barakDataSet"
    BARAK_QOS_FILE_PATH = "barakQosFilePath"
    COMM_DEFS_DE = "commDefsDE"
    IDENTIFIERS_FILE_PATH = "identifiersFilePath"
    SOURCE_ID_TYPE_NAME = "sourceIDTypeName"
    RECIPIENT_IDS_TYPENAMES = "recipientIDsTypeNames"
    AGING = "aging"
    PLATFORM_ID = "platformId"
    NOGA_CAM_DAY = "nogaCamDay"
    NOGA_CAM_NIGHT = "nogaCamNight"
    NOGA_CAM_SWIR = "nogaCamSwir"


# -----------------------------------
# creating enumerations using class
class Configuration(enum.IntEnum):  # argv arguments
    FusionExePath = 0
    ConfigDefsPath = 1
    PathRtiConnectorLib = 2
    # FusionAlgoParamsPath = 1
    # FusionDdsSchemaPath = 2
    # FusionDdsQosPath = 3
    # FusionMonitorDefs = 4
    # rtiConnectorDLL = 5
    # BarakIdentifiers = 6
    # NogaFusionSourceID = 7


class ClientParams(enum.IntEnum):
    RemoteIP = 0
    RemotePort = 1
    LocalIP = 2
    LocalPort = 3


class IdentifierFieldsEnum(enum.IntEnum):
    PLATFORM_ID = 0
    SYSTEM_ID = 1
    MODULE_ID = 2
    TYPE_NAME = 3


class MiscellaneousEnum(enum.IntEnum):
    VERY_SHORT_STRING = 10
    SHORT_STRING = 20
    MEDIUM_STRING = 100
    LONG_STRING_256 = 256
    LONG_STRING = 500
    DDS_SAMPLE_INFO = 36
    METHODS_COUNT = 15
    DETECTION_METHODS = 32


class ResourceStruct:
    def __init__(self, data=None):
        self.strSystemDescriptor = None
        self.strModuleDescriptor = None
        # self.nSystemID = None
        # self.nModuleID = None
        self.A_systemId = None
        self.A_moduleId = None
        self.strTypeName = None
        self.strClassification = None


def ExtractIdentifiers(identifiersPath):
    dictIdentifiers = {}
    root = ET.parse(identifiersPath, parser=ET.XMLParser(encoding='iso-8859-5'))
    for ResourceStructChild in root.findall('ResourceStruct'):
        id = ResourceStruct()
        id.strSystemDescriptor = ResourceStructChild.find("SystemDescriptor").text
        id.strModuleDescriptor = ResourceStructChild.find("ModuleDescriptor").text
        id.A_systemId = ResourceStructChild.find("SystemID").text
        id.A_moduleId = ResourceStructChild.find("ModuleID").text
        id.strTypeName = ResourceStructChild.find("TypeName").text
        id.strClassification = ResourceStructChild.find("Classification").text
        dictIdentifiers[id.strTypeName] = id
    return dictIdentifiers


# -------------------------------------
class DataTimeType:
    def __init__(self, data=None):
        if data is not None:
            self.A_second = data['A_second']
            self.A_nanoseconds = ['A_nanoseconds']
        else:
            dt = time.time()
            self.A_second = int((dt))
            self.A_nanoseconds = int((dt - int(dt)) * 1000000000)


# ----------------------------
# Structs:
class Ctypes_DDSDuration(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("seconds", ctypes.c_int32),
                ("nanoseconds", ctypes.c_uint32)
                ]


class Ctypes_T_Identifier(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("A_platformId", ctypes.c_int32),
                ("A_systemId", ctypes.c_int16),
                ("A_moduleId", ctypes.c_int16)
                ]


class Ctypes_T_RotationalPosition(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("A_azimuth", ctypes.c_double),
                ("A_azimuthAccuracy", ctypes.c_double),
                ("A_elevation", ctypes.c_double),
                ("A_elevationAccuracy", ctypes.c_double)
                ]


class Ctypes_T_Coordinate3D(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("A_altitude", ctypes.c_double),
                ("A_latitude", ctypes.c_double),
                ("A_longitude", ctypes.c_double)
                ]


class Ctypes_T_Detection_Unique_Id(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("A_platformId_A_sourceID", ctypes.c_int32),
                ("A_systemId_A_sourceID", ctypes.c_int16),
                ("A_moduleId_A_sourceID", ctypes.c_int16),
                ("A_msb_A_detectionUniqueID", ctypes.c_ulonglong),
                ("A_lsb_A_detectionUniqueID", ctypes.c_ulonglong),
                ]


class Ctypes_T_DateTime(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("A_seconds", ctypes.c_longlong),
                ("A_nanoseconds", ctypes.c_int32)
                ]


class Ctypes_T_ThreatData(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("A_threatID", Ctypes_T_DateTime),
                ("A_threatType", ctypes.c_char * MiscellaneousEnum.SHORT_STRING),
                ("A_isDetectedByEOS", ctypes.c_bool),
                ("A_isDetectedBySR", ctypes.c_bool),
                ("A_isDetectedByPearl", ctypes.c_bool)
                ]


class Ctypes_T_AronlodThreat(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("A_orientation", ctypes.c_double),
                ("A_distance", ctypes.c_double),
                ("A_pencils", ctypes.c_uint8),
                ("A_threatPencils", Ctypes_T_ThreatData * 32),
                ("A_threatPencils_ItemsCount", ctypes.c_uint),
                ]


class C_Focus(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("A_platformId", ctypes.c_int32),
                ("A_systemId", ctypes.c_int16),
                ("A_moduleId", ctypes.c_int16),
                ("A_seconds", ctypes.c_longlong),
                ("A_nanoseconds", ctypes.c_int32),
                ("A_focusState", ctypes.c_int32),
                ("A_focusAutoState", ctypes.c_int32),
                ("A_upperBound", ctypes.c_bool),
                ("A_lowerBound", ctypes.c_bool),
                ("DDS_sampleInfo", ctypes.c_char * MiscellaneousEnum.DDS_SAMPLE_INFO)
                ]


class Ctypes_T_Physical_Parameters(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("A_elevation_A_relativeLocationsBase", ctypes.c_double),
        ("A_azimuth_A_relativeLocationsBase", ctypes.c_double),
        ("A_range_A_relativeLocationsBase", ctypes.c_double),
        ("A_sensorInertialLocationAvailable", ctypes.c_bool),
        ("A_altitude_A_sensorInertialLocation", ctypes.c_double),
        ("A_latitude_A_sensorInertialLocation", ctypes.c_double),
        ("A_longitude_A_sensorInertialLocation", ctypes.c_double),
        ("A_relativeLocationAvailable", ctypes.c_bool),
        ("A_rangeAvailable", ctypes.c_bool),
        ("A_elevation_A_relativeLocation", ctypes.c_double),
        ("A_azimuth_A_relativeLocation", ctypes.c_double),
        ("A_range_A_relativeLocation", ctypes.c_double),
        ("A_elevation_A_relativeLocationAccuracy", ctypes.c_double),
        ("A_azimuth_A_relativeLocationAccuracy", ctypes.c_double),
        ("A_range_A_relativeLocationAccuracy", ctypes.c_double),
        ("A_inertialLocationAvailable", ctypes.c_bool),
        ("A_elevation_A_inertialLocation", ctypes.c_double),
        ("A_azimuth_A_inertialLocation", ctypes.c_double),
        ("A_range_A_inertialLocation", ctypes.c_double),
        ("A_elevation_A_inertialLocationAccuracy", ctypes.c_double),
        ("A_azimuth_A_inertialLocationAccuracy", ctypes.c_double),
        ("A_range_A_inertialLocationAccuracy", ctypes.c_double),
        ("A_absoluteLocationAvailable", ctypes.c_bool),
        ("A_altitude_A_absoluteLocation", ctypes.c_double),
        ("A_latitude_A_absoluteLocation", ctypes.c_double),
        ("A_longitude_A_absoluteLocation", ctypes.c_double),
        ("A_altitude_A_absoluteLocationAccuracy", ctypes.c_double),
        ("A_latitude_A_absoluteLocationAccuracy", ctypes.c_double),
        ("A_longitude_A_absoluteLocationAccuracy", ctypes.c_double),
        ("A_angularVelocityAvailable", ctypes.c_bool),
        ("A_elevation_A_angularVelocity", ctypes.c_double),
        ("A_azimuth_A_angularVelocity", ctypes.c_double),
        ("A_magnitude_A_angularVelocity", ctypes.c_double),
        ("A_elevation_A_angularVelocityAccuracy", ctypes.c_double),
        ("A_azimuth_A_angularVelocityAccuracy", ctypes.c_double),
        ("A_magnitude_A_angularVelocityAccuracy", ctypes.c_double),
        ("A_linearSpeedAvailable", ctypes.c_bool),
        ("A_linearSpeed", ctypes.c_double),
        ("A_elevation_A_speedOrientation", ctypes.c_double),
        ("A_azimuth_A_speedOrientation", ctypes.c_double),
        ("A_range_A_speedOrientation", ctypes.c_double),
        ("A_linearSpeedAccuracy", ctypes.c_double),
        ("A_radialVelocityAvailable", ctypes.c_bool),
        ("A_radialVelocity", ctypes.c_double),
        ("A_radialVelocityAccuracy", ctypes.c_double),
        ("A_tangentialVelocityAvailable", ctypes.c_bool),
        ("A_horizontalTangentialVelocity", ctypes.c_double),
        ("A_horizontalTangentialVelocityError", ctypes.c_double),
        ("A_verticalTangentialVelocity", ctypes.c_double),
        ("A_verticalTangentialVelocityError", ctypes.c_double),
        ("A_fieldOfViewAvailable", ctypes.c_bool),
        ("A_hfov_A_fieldOfView", ctypes.c_double),
        ("A_vfov_A_fieldOfView", ctypes.c_double),
        ("A_elevation_A_fovCenter_A_fieldOfView", ctypes.c_double),
        ("A_azimuth_A_fovCenter_A_fieldOfView", ctypes.c_double),
        ("A_range_A_fovCenter_A_fieldOfView", ctypes.c_double)
    ]


class Ctypes_T_Descriptive_Parameters(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("A_recognizingDetectorTypes", ctypes.c_char * MiscellaneousEnum.SHORT_STRING * 10),
        ("A_recognizingDetectorTypes_ItemsCount", ctypes.c_uint32),
        ("A_classificationAvailable", ctypes.c_bool),
        ("A_objectClassification", ctypes.c_char * MiscellaneousEnum.SHORT_STRING),
        ("A_classificationConfidence", ctypes.c_double),
        ("A_elevation_A_detectionSampleSize", ctypes.c_double),
        ("A_azimuth_A_detectionSampleSize", ctypes.c_double),
        ("A_range_A_detectionSampleSize", ctypes.c_double),
        ("A_height_A_absoluteSize", ctypes.c_double),
        ("A_length_A_absoluteSize", ctypes.c_double),
        ("A_width_A_absoluteSize", ctypes.c_double),
        ("A_seconds_A_exposureDuration", ctypes.c_uint32),
        ("A_nanoseconds_A_exposureDuration", ctypes.c_uint32),
        ("A_rangeMethod", ctypes.c_int32),
        ("A_altitude_A_sourceLocationAccuracy", ctypes.c_double),
        ("A_latitude_A_sourceLocationAccuracy", ctypes.c_double),
        ("A_longitude_A_sourceLocationAccuracy", ctypes.c_double),
        ("A_altitude_A_sourceLocation", ctypes.c_double),
        ("A_latitude_A_sourceLocation", ctypes.c_double),
        ("A_longitude_A_sourceLocation", ctypes.c_double)

    ]


class Ctypes_T_Spatial_Info(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("A_physicalInfo", Ctypes_T_Physical_Parameters),
                ("A_descriptiveInfo", Ctypes_T_Descriptive_Parameters),
                ]


class T_DetectingMethod(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("A_detectorType", ctypes.c_char * MiscellaneousEnum.SHORT_STRING),
        ("A_algorithm", ctypes.c_char * MiscellaneousEnum.SHORT_STRING)
    ]


class C_Detection(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("A_platformId_A_sourceID", ctypes.c_int32),
                ("A_systemId_A_sourceID", ctypes.c_int16),
                ("A_moduleId_A_sourceID", ctypes.c_int16),
                ("A_seconds_A_timeOfDataGeneration", ctypes.c_longlong),
                ("A_nanoseconds_A_timeOfDataGeneration", ctypes.c_int32),
                ("A_msb_A_detectionUniqueID", ctypes.c_ulonglong),
                ("A_lsb_A_detectionUniqueID", ctypes.c_ulonglong),
                ("A_confidence", ctypes.c_double),
                ("A_detectionClassification", ctypes.c_char * MiscellaneousEnum.SHORT_STRING),
                ("A_detectionClassScore", ctypes.c_double),
                ("A_detectionForceType", ctypes.c_int32),
                ("A_detectionThreatStatus", ctypes.c_int32),
                ("A_interception", ctypes.c_int32),
                ("A_detectionStatus", ctypes.c_int32),
                ("A_type", ctypes.c_int32),
                ("A_seconds_A_lifeSpan", ctypes.c_uint32),
                ("A_nanoseconds_A_lifeSpan", ctypes.c_uint32),
                ("A_priority", ctypes.c_int16),
                ("A_trajectoryType", ctypes.c_int32),
                ("A_method", ctypes.c_int32 * MiscellaneousEnum.METHODS_COUNT),
                ("A_method_ItemsCount", ctypes.c_uint32),
                ("A_spatialParametersAvailable", ctypes.c_bool),
                ("A_spatialInfo", Ctypes_T_Spatial_Info),
                ("A_suspensionCause", ctypes.c_int32),
                ("A_designatedInfo", ctypes.c_char * MiscellaneousEnum.SHORT_STRING),
                ("A_designatedInfo_IsSet", ctypes.c_bool),
                ("A_numberOfDetectionMethods", ctypes.c_uint8),
                ("A_numberOfDetectionMethods_IsSet", ctypes.c_bool),
                ("A_detectionMethods", T_DetectingMethod * MiscellaneousEnum.DETECTION_METHODS),
                ("A_detectionMethods_IsSet", ctypes.c_bool),
                ("A_detectionMethods_ItemsCount", ctypes.c_uint32),
                ("A_snapshotAvailable", ctypes.c_bool)
                ]

    def get_fields(self):
        return [field[0] for field in self._fields_]


class C_Detection_Merged(C_Detection):
    _pack_ = 1
    _fields_ = [
        ("A_sourceDetectionsID", Ctypes_T_Detection_Unique_Id * 100),
        ("A_sourceDetectionsID_ItemsCount", ctypes.c_uint32),
        ("DDS_sampleInfo", ctypes.c_char * MiscellaneousEnum.DDS_SAMPLE_INFO)
    ]


class C_Detection_Radar(C_Detection):
    _pack_ = 1
    _fields_ = [
        ("A_detectionMode", ctypes.c_char * MiscellaneousEnum.SHORT_STRING),
        ("A_frequency", ctypes.c_double),
        ("A_bw", ctypes.c_double),
        ("DDS_sampleInfo", ctypes.c_char * MiscellaneousEnum.DDS_SAMPLE_INFO)
    ]


class T_VideoPosition(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("A_verticalPosition", ctypes.c_double),
        ("A_horizontalPosition", ctypes.c_double)
    ]


class C_Detection_Optronics(C_Detection):
    _pack_ = 1
    _fields_ = [
        ("A_opticalErrorRadius", ctypes.c_double),
        ("A_absoluteDirectionAvailable", ctypes.c_bool),
        ("A_elevation_A_sensorLOS", ctypes.c_double),
        ("A_azimuth_A_sensorLOS", ctypes.c_double),
        ("A_range_A_sensorLOS", ctypes.c_double),
        ("A_elevation_A_sensorLOSAccuracy", ctypes.c_double),
        ("A_azimuth_A_sensorLOSAccuracy", ctypes.c_double),
        ("A_range_A_sensorLOSAccuracy", ctypes.c_double),
        ("A_videoDataAvailable", ctypes.c_bool),
        ("A_platformId_A_videoStreamSourceID", ctypes.c_int32),
        ("A_systemId_A_videoStreamSourceID", ctypes.c_int16),
        ("A_moduleId_A_videoStreamSourceID", ctypes.c_int16),

        ("A_detectionCenterVideoLocation", T_VideoPosition),
        ("A_detectionSizeOnVideo", T_VideoPosition),
        ("A_detectionVideoAccuracy", T_VideoPosition),

        ("DDS_sampleInfo", ctypes.c_char * MiscellaneousEnum.DDS_SAMPLE_INFO)
    ]


class C_Detection_Aps(C_Detection):
    _pack_ = 1
    _fields_ = [
        ("A_seconds_A_timeToGo", ctypes.c_uint32),
        ("A_nanoseconds_A_timeToGo", ctypes.c_uint32),
        ("A_affecting", ctypes.c_bool),
        ("A_threatFamily", ctypes.c_int32),
        ("A_threatAronlod", Ctypes_T_AronlodThreat),
        ("A_threatAronlod_IsSet", ctypes.c_bool),
        ("A_actionStatus", ctypes.c_char * MiscellaneousEnum.SHORT_STRING),
        ("A_altitude_A_threatHitPoint", ctypes.c_double),
        ("A_latitude_A_threatHitPoint", ctypes.c_double),
        ("A_longitude_A_threatHitPoint", ctypes.c_double),
        ("A_threatRefinementInfo", ctypes.c_char * MiscellaneousEnum.SHORT_STRING),
        ("DDS_sampleInfo", ctypes.c_char * MiscellaneousEnum.DDS_SAMPLE_INFO)
    ]


class C_Detection_ElectronicWarfare(C_Detection):
    _pack_ = 1
    _fields_ = [
        ("A_tbdField", ctypes.c_int16),

        ("DDS_sampleInfo", ctypes.c_char * MiscellaneousEnum.DDS_SAMPLE_INFO)
    ]


class C_Snapshot(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("A_platformId_A_sourceID", ctypes.c_int32),
        ("A_systemId_A_sourceID", ctypes.c_int16),
        ("A_moduleId_A_sourceID", ctypes.c_int16),
        ("A_seconds_A_timeOfDataGeneration", ctypes.c_longlong),
        ("A_nanoseconds_A_timeOfDataGeneration", ctypes.c_int32),
        ("A_msb_A_detectionUniqueID", ctypes.c_ulonglong),
        ("A_lsb_A_detectionUniqueID", ctypes.c_ulonglong),
        ("A_snapshotID", ctypes.c_ulonglong),
        ("A_format", ctypes.c_char * 10),
        ("A_format_ItemsCount", ctypes.c_uint32),
        ("A_snapshot", ctypes.c_uint8 * 4096),
        ("A_snapshot_ItemsCount", ctypes.c_uint32),
        ("DDS_sampleInfo", ctypes.c_char * MiscellaneousEnum.DDS_SAMPLE_INFO)
    ]


class C_Tactical_Sensor_Specification(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("A_sourceID", Ctypes_T_Identifier),
        ("A_seconds", ctypes.c_longlong),
        ("A_nanoseconds", ctypes.c_int32),
        ("A_detectorTypesSupport", ctypes.c_char * MiscellaneousEnum.SHORT_STRING * 10),
        ("A_detectorTypesSupport_IsSet", ctypes.c_bool),
        ("A_detectorTypesSupport_ItemsCount", ctypes.c_uint32),
        ("A_detectingClassSupport", ctypes.c_char * MiscellaneousEnum.SHORT_STRING * 50),
        ("A_detectingClassSupport_IsSet", ctypes.c_bool),
        ("A_detectingClassSupport_ItemsCount", ctypes.c_uint32),
        ("A_rangeSupport", ctypes.c_bool),
        ("A_detectionSizeSupport", ctypes.c_bool),
        ("A_accuracySupport", ctypes.c_bool),
        ("A_detectionThreatLevelSupport", ctypes.c_bool),
        ("A_setDetectorStateSupport", ctypes.c_bool),
        ("A_videoDetectorSupport", ctypes.c_bool),
        ("A_snapshotSupport", ctypes.c_bool),
        ("A_rfSupport", ctypes.c_bool),

        ("A_maxNumberOfDetectionLocations", ctypes.c_int16),

        ("A_inertialLocationSupport", ctypes.c_bool),

        ("DDS_sampleInfo", ctypes.c_char * MiscellaneousEnum.DDS_SAMPLE_INFO)
    ]


class C_Resource_Specification(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("A_sourceID", Ctypes_T_Identifier),
                ("A_seconds", ctypes.c_longlong),
                ("A_nanoseconds", ctypes.c_int32),
                ("A_resourceTypeName", ctypes.c_char * MiscellaneousEnum.SHORT_STRING),
                ("A_descriptor", ctypes.c_char * MiscellaneousEnum.LONG_STRING),
                ("A_seconds_A_creationDate", ctypes.c_longlong),
                ("A_nanoseconds_A_creationDate", ctypes.c_int32),
                ("A_seconds_A_restorationDate", ctypes.c_longlong),
                ("A_nanoseconds_A_restorationDate", ctypes.c_int32),
                ("A_seconds_A_softwareUpdateDate", ctypes.c_longlong),
                ("A_nanoseconds_A_softwareUpdateDate", ctypes.c_int32),
                ("A_seconds_A_hardwareUpdateDate", ctypes.c_longlong),
                ("A_nanoseconds_A_hardwareUpdateDate", ctypes.c_int32),
                ("A_companyCode", ctypes.c_char * MiscellaneousEnum.SHORT_STRING),
                ("A_restorerCode", ctypes.c_char * MiscellaneousEnum.SHORT_STRING),
                ("A_projectCode", ctypes.c_char * MiscellaneousEnum.SHORT_STRING),
                ("A_seconds_A_totalOpTime", ctypes.c_uint32),
                ("A_nanoseconds_A_totalOpTime", ctypes.c_uint32),

                ("A_major_A_softwareVersion", ctypes.c_uint16),
                ("A_minor_A_softwareVersion", ctypes.c_uint16),
                ("A_revision_A_softwareVersion", ctypes.c_uint16),
                ("A_build_A_softwareVersion", ctypes.c_uint16),

                ("A_major_A_hardwareVersion", ctypes.c_uint16),
                ("A_minor_A_hardwareVersion", ctypes.c_uint16),
                ("A_revision_A_hardwareVersion", ctypes.c_uint16),
                ("A_build_A_hardwareVersion", ctypes.c_uint16),
                ("A_catalogCode", ctypes.c_char * 10),
                ("A_catalogCode_ItemsCount", ctypes.c_uint32),
                ("A_serialNumber", ctypes.c_char * 10),
                ("A_serialNumber_ItemsCount", ctypes.c_uint32),
                ("A_includedSoftwareSourceID", Ctypes_T_Identifier * 5),
                ("A_includedSoftwareSourceID_ItemsCount", ctypes.c_uint32),
                ("DDS_sampleInfo", ctypes.c_char * MiscellaneousEnum.DDS_SAMPLE_INFO)
                ]


class C_Tactical_Sensor(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("A_sourceID", Ctypes_T_Identifier),
                ("A_seconds", ctypes.c_longlong),
                ("A_nanoseconds", ctypes.c_int32),
                ("A_sensorCurrentStatus", ctypes.c_int32),
                ("A_falseAlarmProbability", ctypes.c_double),
                ("A_detectionProbability", ctypes.c_double),
                ("A_sensitivityLevel", ctypes.c_uint8),
                ("A_sensitivityLevel_IsSet", ctypes.c_bool),
                ("DDS_sampleInfo", ctypes.c_char * MiscellaneousEnum.DDS_SAMPLE_INFO)
                ]


class C_Position(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("A_platformId_A_sourceID", ctypes.c_int32),
        ("A_systemId_A_sourceID", ctypes.c_int16),
        ("A_moduleId_A_sourceID", ctypes.c_int16),
        ("A_seconds_A_timeOfDataGeneration", ctypes.c_longlong),
        ("A_nanoseconds_A_timeOfDataGeneration", ctypes.c_int32),
        ("A_altitude_A_currentPosition", ctypes.c_double),
        ("A_latitude_A_currentPosition", ctypes.c_double),
        ("A_longitude_A_currentPosition", ctypes.c_double),
        ("DDS_sampleInfo", ctypes.c_char * MiscellaneousEnum.DDS_SAMPLE_INFO)
    ]


class C_Rot_Mount(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("A_platformId_A_sourceID", ctypes.c_int32),
                ("A_systemId_A_sourceID", ctypes.c_int16),
                ("A_moduleId_A_sourceID", ctypes.c_int16),
                ("A_seconds_A_timeOfDataGeneration", ctypes.c_longlong),
                ("A_nanoseconds_A_timeOfDataGeneration", ctypes.c_int32),
                ("A_mountPosition", Ctypes_T_RotationalPosition),
                ("A_absolutePosition", Ctypes_T_Coordinate3D),
                ("A_attitudeToNorthPosition", ctypes.c_double),
                ("A_scanState", ctypes.c_int),
                ("A_bringToState", ctypes.c_int),
                ("A_bringToPreset", Ctypes_T_RotationalPosition),
                ("A_enslavementMode", ctypes.c_int),
                ("A_enslavedTo", Ctypes_T_Identifier),
                ("A_workMode", ctypes.c_int),
                ("A_lmcState", ctypes.c_int),
                ("A_stabilizationState", ctypes.c_int),
                ("A_inMovementInhibitZone", ctypes.c_bool),
                ("A_traverseMode", ctypes.c_bool),
                ("DDS_sampleInfo", ctypes.c_char * MiscellaneousEnum.DDS_SAMPLE_INFO)
                ]


class C_Rot_Mount_StartScanning_Cmd(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("A_sourceID", Ctypes_T_Identifier),
                ("A_recipientID", Ctypes_T_Identifier),
                ("A_referenceNum", ctypes.c_int32),
                ("A_seconds_A_timeOfDataGeneration", ctypes.c_longlong),
                ("A_nanoseconds_A_timeOfDataGeneration", ctypes.c_int32),
                ("A_boundaryPoints", Ctypes_T_RotationalPosition * 5),
                ("A_boundaryPoints_ItemsCount", ctypes.c_uint),
                ("DDS_sampleInfo", ctypes.c_char * MiscellaneousEnum.DDS_SAMPLE_INFO)
                ]


class C_Rot_Mount_StopScanning_Cmd(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("A_sourceID", Ctypes_T_Identifier),
                ("A_recipientID", Ctypes_T_Identifier),
                ("A_referenceNum", ctypes.c_int32),
                ("A_seconds_A_timeOfDataGeneration", ctypes.c_longlong),
                ("A_nanoseconds_A_timeOfDataGeneration", ctypes.c_int32),
                ("DDS_sampleInfo", ctypes.c_char * MiscellaneousEnum.DDS_SAMPLE_INFO)
                ]


class C_Tactical_Sensitivity_Cmd(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("A_sourceID", Ctypes_T_Identifier),
                ("A_recipientID", Ctypes_T_Identifier),
                ("A_referenceNum", ctypes.c_int32),
                ("A_seconds_A_timeOfDataGeneration", ctypes.c_longlong),
                ("A_nanoseconds_A_timeOfDataGeneration", ctypes.c_int32),
                ("A_level", ctypes.c_uint8),
                ("DDS_sampleInfo", ctypes.c_char * MiscellaneousEnum.DDS_SAMPLE_INFO)
                ]


class DictTopicDataEnum(enum.IntEnum):
    StructType = 0
    TopicQueue = 1


# Dictionary  <topic, [ type, queue];
global DictTopicData
DictTopicData = {
    "P_Tactical_Sensor_PSM::C_Detection": [C_Detection, detectionQueue],
    "P_Tactical_Sensor_PSM::C_Detection_ElectronicWarfare": [C_Detection_ElectronicWarfare,
                                                             detectionElectronicWarfareQueue],
    "P_Tactical_Sensor_PSM::C_Detection_Optronics": [C_Detection_Optronics, detectionOptronicsQueue],
    "P_Tactical_Sensor_PSM::C_Detection_Radar": [C_Detection_Radar, detectionRadarQueue],
    "P_Tactical_Sensor_PSM::C_Tactical_Sensitivity_Cmd": [C_Tactical_Sensitivity_Cmd, tacticalSensitivityQueue],
    "P_Navigation_PSM::C_Position": [C_Position, PositionQueue],
    "P_Tactical_Sensor_PSM::C_Detection_Aps": [C_Detection_Aps, DetectionApsQueue],
    "P_Mount_PSM::C_Rot_Mount": [C_Rot_Mount, RotMountQueue],
    "P_Mount_PSM::C_Rot_Mount_StartScanning_Cmd": [C_Rot_Mount_StartScanning_Cmd, RotMountStartScanQueue],
    "P_Mount_PSM::C_Rot_Mount_StopScanning_Cmd": [C_Rot_Mount_StopScanning_Cmd, RotMountStopScanQueue],
    # None in queue - cuz it's only for publishing
    "P_Maintenance_PSM::C_Resource_Specification": [C_Resource_Specification, None],
    "P_Tactical_Sensor_PSM::C_Detection_Merged": [C_Detection_Merged, None],
    "P_Tactical_Sensor_PSM::C_Tactical_Sensor_Specification": [C_Tactical_Sensor_Specification, None],
    "P_Tactical_Sensor_PSM::C_Tactical_Sensor": [C_Tactical_Sensor, None]

}


def AssignStringToBuffer(str1, arr):
    """
    assign string to ctypes.c_char buffer
    :param str1: string
    :param arr: ctypes.c_char  array
    """

    for i in range(len(str1)):
        arr[i] = str.encode(str1[i])
