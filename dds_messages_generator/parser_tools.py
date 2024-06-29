import csv
import datetime
from rtiwrapper.Common import *
import os

E_IFFCategory = {
    'P_Tactical_Sensor_PSM::L_IFFCategory_UNKNOWN': 0,
    'P_Tactical_Sensor_PSM::L_IFFCategory_FRIEND': 1,
    'P_Tactical_Sensor_PSM::L_IFFCategory_FOE': 2,
    'P_Tactical_Sensor_PSM::L_IFFCategory_UNINVOLVED': 3
}
E_EngagementStatus = {
    'P_Tactical_Sensor_PSM::L_EngagementStatus_UNKNOWN': 0,
    'P_Tactical_Sensor_PSM::L_EngagementStatus_NONE': 1,
    'P_Tactical_Sensor_PSM::L_EngagementStatus_HANDLED': 2,
    'P_Tactical_Sensor_PSM::L_EngagementStatus_DROPPED': 3,
    'P_Tactical_Sensor_PSM::L_EngagementStatus_THRETENING': 4
}
E_Interception = {
    'P_Tactical_Sensor_PSM::L_Interception_UNKNOWN': 0,
    'P_Tactical_Sensor_PSM::L_Interception_ON': 1,
    'P_Tactical_Sensor_PSM::L_Interceptions_MISSING_OUT': 2
}

E_DetectionState = {
    'P_Tactical_Sensor_PSM::L_DetectionState_NONE': 0,
    'P_Tactical_Sensor_PSM::L_DetectionState_VALID_RECOGNIZED': 1,
    'P_Tactical_Sensor_PSM::L_DetectionState_VALID_NOT_RECOGNIZED': 2,
    'P_Tactical_Sensor_PSM::L_DetectionState_DELETED': 3,
    'P_Tactical_Sensor_PSM::L_DetectionState_CANCELED': 4,
    'P_Tactical_Sensor_PSM::L_DetectionState_MERGED': 5,
    'P_Tactical_Sensor_PSM::L_DetectionState_SPLIT': 6
}

E_DetectionType = {
    'P_Tactical_Sensor_PSM::L_DetectionType_DETECTION': 0,
    'P_Tactical_Sensor_PSM::L_DetectionType_THREAT': 1,
    'P_Tactical_Sensor_PSM::L_DetectionType_TARGET': 2
}

E_Trajectory = {
    'P_Tactical_Sensor_PSM::L_Trajectory_UNKNOWN': 0,
    'P_Tactical_Sensor_PSM::L_Trajectory_SURFACE': 1,
    'P_Tactical_Sensor_PSM::L_Trajectory_HORIZON': 2,
    'P_Tactical_Sensor_PSM::L_Trajectory_BALISTIC': 3,
    'P_Tactical_Sensor_PSM::L_Trajectory_STEEP': 4,
    'P_Tactical_Sensor_PSM::L_Trajectory_UNDERNEATH': 5
}

E_Sensing_Method = {
    'P_Tactical_Sensor_PSM::L_Sensing_Method_UNKNOWN': 0,
    'P_Tactical_Sensor_PSM::L_Sensing_Method_RF': 1,
    'P_Tactical_Sensor_PSM::L_Sensing_Method_OPTIC': 2,
    'P_Tactical_Sensor_PSM::L_Sensing_Method_ACOUSTIC': 3,
    'P_Tactical_Sensor_PSM::L_Sensing_Method_C4I': 4,
    'P_Tactical_Sensor_PSM::L_Sensing_Method_OPERATOR': 5
}

E_Value_Source = {
    'P_LDM_Common::L_Value_Source_UNKNOWN': 0,
    'P_LDM_Common::L_Value_Source_CALCULATED': 1,
    'P_LDM_Common::L_Value_Source_MEASURED': 2,
    'P_LDM_Common::L_Value_Source_REPORTED': 3
}

E_SuspensionCause = {
    'P_Tactical_Sensor_PSM::L_SuspensionCause_NOT_SUSPENDED': 0,
    'P_Tactical_Sensor_PSM::L_SuspensionCause_UNKNOWN': 1,
    'P_Tactical_Sensor_PSM::L_SuspensionCause_FALSE_DETECTION': 2,
    'P_Tactical_Sensor_PSM::L_SuspensionCause_LATE_DETECTION': 3,
    'P_Tactical_Sensor_PSM::L_SuspensionCause_IRRELEVANT': 4,
    'P_Tactical_Sensor_PSM::L_SuspensionCause_BUSY': 5,
    'P_Tactical_Sensor_PSM::L_SuspensionCause_VANISHED': 6,
    'P_Tactical_Sensor_PSM::L_SuspensionCause_OPERATOR_DECISION': 7
}

E_ProcessState = {
    'P_Mount_PSM::L_ProcessState_OFF': 0,
    'P_Mount_PSM::L_ProcessState_IN_PROGRESS': 1,
    'P_Mount_PSM::L_ProcessState_COMPLETED': 2,
    'P_Mount_PSM::L_ProcessState_FAILED': 3,
}

E_EnslavementMode = {
    'P_Mount_PSM::L_EnslavementMode_INDEPENDENT': 0,
    'P_Mount_PSM::L_EnslavementMode_ENSLAVED': 1,
    'P_Mount_PSM::L_EnslavementMode_MECHANICAL': 2,
}

E_MountWorkMode = {
    'P_Mount_PSM::L_MountWorkMode_INIT': 0,
    'P_Mount_PSM::L_MountWorkMode_OPER': 1,
    'P_Mount_PSM::L_MountWorkMode_MAINT': 2,
}

E_OnOff = {
    'P_LDM_Common::L_OnOff_ON': 0,
    'P_LDM_Common::L_OnOff_OFF': 1,
}

E_StabilizationMode = {
    'P_Mount_PSM::L_StabilizationMode_MANUAL': 0,
    'P_Mount_PSM::L_StabilizationMode_POWER': 1,
    'P_Mount_PSM::L_StabilizationMode_STABILIZATION': 2,
}


def is_this_a_log_file(output_list):
    # Key to check
    return 'A_platformId_A_sourceID' in output_list


def load_scenario(filename: str):
    output_lst = []
    file_name = os.path.basename(filename)
    with open(filename, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convert "FALSE" to "False" and "TRUE" to "True"
            for key, value in row.items():
                if value.upper() == "FALSE":
                    row[key] = "False"
                elif value.upper() == "TRUE":
                    row[key] = "True"

            if "benchmark" in file_name:
                output_lst.append(row)
            elif is_this_a_log_file(row):
                # Assuming 'row' is a dictionary containing the data from a CSV row
                seconds = float(row['A_seconds_A_timeOfDataGeneration'])
                nanoseconds = float(row['A_nanoseconds_A_timeOfDataGeneration'])
                # Convert to datetime
                datetime_time = datetime.datetime.utcfromtimestamp(seconds + nanoseconds * 1e-9)
                output = {'time': datetime_time, 'data': row}
                output_lst.append(dict(output))
            else:
                datetime_time = datetime.datetime.strptime(row['LocalTime'], '%H:%M:%S.%f')
                if row['Info'].find('General Enemy') != -1:
                    row['Info'] = row['Info'].replace('General Enemy', 'General_Enemy')
                data = row['Info'].split(sep=' ')
                if data[8] == 'General_Enemy':
                    data[8] = 'General Enemy'
                output = {'time': datetime_time, 'data': data}
                output_lst.append(output)
    return output_lst


def mount_data_parser(lst: list):
    output_lst = []
    topicOptronics = "P_Mount_PSM::C_Rot_Mount"
    structType = DictTopicData[topicOptronics][DictTopicDataEnum.StructType]
    for item in lst:
        ctypeStruct = structType()
        ctypeStruct.A_platformId_A_sourceID = int(item['data'][0])
        ctypeStruct.A_systemId_A_sourceID = int(item['data'][1])
        ctypeStruct.A_moduleId_A_sourceID = int(item['data'][2])
        ctypeStruct.A_seconds_A_timeOfDataGeneration = int(item['data'][3])
        ctypeStruct.A_nanoseconds_A_timeOfDataGeneration = int(item['data'][4])
        ctypeStruct.A_azimuth_mountPosition = float(item['data'][5])
        ctypeStruct.A_azimuthAccuracy_mountPosition = float(item['data'][6])
        ctypeStruct.A_elevation_mountPosition = float(item['data'][7])
        ctypeStruct.A_elevationAccuracy_mountPosition = float(item['data'][8])
        ctypeStruct.A_altitude_absolutePosition = float(item['data'][9])
        ctypeStruct.A_latitude_absolutePosition = float(item['data'][10])
        ctypeStruct.A_longitude_absolutePosition = float(item['data'][11])
        ctypeStruct.A_attitudeToNorthPosition = float(item['data'][12])
        ctypeStruct.A_scanState = E_ProcessState[item['data'][13]]
        ctypeStruct.A_bringToState = E_ProcessState[item['data'][14]]
        ctypeStruct.A_azimuth_bringToPreset = float(item['data'][15])
        ctypeStruct.A_azimuthAccuracy_bringToPreset = float(item['data'][16])
        ctypeStruct.A_elevation_bringToPreset = float(item['data'][17])
        ctypeStruct.A_elevationAccuracy_bringToPreset = float(item['data'][18])
        ctypeStruct.A_enslavementMode = E_EnslavementMode[item['data'][19]]
        ctypeStruct.A_platformId_enslavedTo = int(item['data'][20])
        ctypeStruct.A_systemId_enslavedTo = int(item['data'][21])
        ctypeStruct.A_moduleId_enslavedTo = int(item['data'][22])
        ctypeStruct.A_workMode = E_MountWorkMode[item['data'][23]]
        ctypeStruct.A_lmcState = E_OnOff[item['data'][24]]
        ctypeStruct.A_stabilizationState = E_StabilizationMode[item['data'][25]]
        ctypeStruct.A_inMovementInhibitZone = int(item['data'][26])

        output_lst.append({"time": item['time'], "data": ctypeStruct})
    return output_lst.copy()


def optronics_data_parser(lst: list):
    output_lst = []
    topicOptronics = "P_Tactical_Sensor_PSM::C_Detection"
    structType = DictTopicData[topicOptronics][DictTopicDataEnum.StructType]
    for item in lst:
        ctypeStruct = structType()
        ctypeStruct.A_platformId_A_sourceID = int(item['data'][0])
        ctypeStruct.A_systemId_A_sourceID = int(item['data'][1])
        ctypeStruct.A_moduleId_A_sourceID = int(item['data'][2])
        ctypeStruct.A_seconds_A_timeOfDataGeneration = int(item['data'][3])
        ctypeStruct.A_nanoseconds_A_timeOfDataGeneration = int(item['data'][4])
        ctypeStruct.A_msb_A_detectionUniqueID = int(item['data'][5])
        ctypeStruct.A_lsb_A_detectionUniqueID = int(item['data'][6])
        ctypeStruct.A_confidence = float(item['data'][7])
        ctypeStruct.A_detectionClassification = item['data'][8].encode()
        ctypeStruct.A_detectionClassScore = float(item['data'][9])
        ctypeStruct.A_detectionForceType = E_IFFCategory[item['data'][10]]
        ctypeStruct.A_detectionThreatStatus = E_EngagementStatus[item['data'][11]]
        ctypeStruct.A_interception = E_Interception[item['data'][12]]
        ctypeStruct.A_detectionStatus = E_DetectionState[item['data'][13]]
        ctypeStruct.A_type = E_DetectionType[item['data'][14]]
        ctypeStruct.A_seconds_A_lifeSpan = int(item['data'][15])
        ctypeStruct.A_nanoseconds_A_lifeSpan = int(item['data'][16])
        ctypeStruct.A_priority = int(item['data'][17])
        ctypeStruct.A_trajectoryType = E_Trajectory[item['data'][18]]
        for i in range(15):
            ctypeStruct.A_method[i] = E_Sensing_Method[item['data'][19 + i]]
        ctypeStruct.A_method_ItemsCount = int(item['data'][34])
        ctypeStruct.A_spatialParametersAvailable = int(item['data'][35])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_elevation_A_relativeLocationsBase = float(item['data'][36])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_azimuth_A_relativeLocationsBase = float(item['data'][37])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_range_A_relativeLocationsBase = float(item['data'][38])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_sensorInertialLocationAvailable = int(item['data'][39])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_altitude_A_sensorInertialLocation = float(item['data'][40])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_latitude_A_sensorInertialLocation = float(item['data'][41])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_longitude_A_sensorInertialLocation = float(item['data'][42])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_relativeLocationAvailable = int(item['data'][43])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_rangeAvailable = int(item['data'][44])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_elevation_A_relativeLocation = float(item['data'][45])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_azimuth_A_relativeLocation = float(item['data'][46])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_range_A_relativeLocation = float(item['data'][47])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_elevation_A_relativeLocationAccuracy = float(item['data'][48])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_azimuth_A_relativeLocationAccuracy = float(item['data'][49])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_range_A_relativeLocationAccuracy = float(item['data'][50])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_inertialLocationAvailable = int(item['data'][51])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_elevation_A_inertialLocation = float(item['data'][52])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_azimuth_A_inertialLocation = float(item['data'][53])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_range_A_inertialLocation = float(item['data'][54])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_elevation_A_inertialLocationAccuracy = float(item['data'][55])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_azimuth_A_inertialLocationAccuracy = float(item['data'][56])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_range_A_inertialLocationAccuracy = float(item['data'][57])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_absoluteLocationAvailable = int(item['data'][58])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_altitude_A_absoluteLocation = float(item['data'][59])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_latitude_A_absoluteLocation = float(item['data'][60])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_longitude_A_absoluteLocation = float(item['data'][61])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_altitude_A_absoluteLocationAccuracy = float(item['data'][62])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_latitude_A_absoluteLocationAccuracy = float(item['data'][63])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_longitude_A_absoluteLocationAccuracy = float(item['data'][64])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_angularVelocityAvailable = int(item['data'][65])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_elevation_A_angularVelocity = float(item['data'][66])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_azimuth_A_angularVelocity = float(item['data'][67])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_magnitude_A_angularVelocity = float(item['data'][68])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_elevation_A_angularVelocityAccuracy = float(item['data'][69])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_azimuth_A_angularVelocityAccuracy = float(item['data'][70])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_magnitude_A_angularVelocityAccuracy = float(item['data'][71])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_linearSpeedAvailable = int(item['data'][72])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_linearSpeed = float(item['data'][73])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_elevation_A_speedOrientation = float(item['data'][74])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_azimuth_A_speedOrientation = float(item['data'][75])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_range_A_speedOrientation = float(item['data'][76])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_linearSpeedAccuracy = float(item['data'][77])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_radialVelocityAvailable = int(item['data'][78])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_radialVelocity = float(item['data'][79])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_radialVelocityAccuracy = float(item['data'][80])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_tangentialVelocityAvailable = int(item['data'][81])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_horizontalTangentialVelocity = float(item['data'][82])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_horizontalTangentialVelocityError = float(item['data'][83])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_verticalTangentialVelocity = float(item['data'][84])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_verticalTangentialVelocityError = float(item['data'][85])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_fieldOfViewAvailable = int(item['data'][86])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_hfov_A_fieldOfView = float(item['data'][87])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_vfov_A_fieldOfView = float(item['data'][88])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_elevation_A_fovCenter_A_fieldOfView = float(item['data'][89])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_azimuth_A_fovCenter_A_fieldOfView = float(item['data'][90])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_range_A_fovCenter_A_fieldOfView = float(item['data'][91])
        for i in range(10):
            ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_recognizingDetectorTypes[i].value = item['data'][
                92 + i].encode()
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_recognizingDetectorTypes_ItemsCount = int(item['data'][102])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_classificationAvailable = int(item['data'][103])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_objectClassification = item['data'][104].encode()
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_classificationConfidence = float(item['data'][105])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_elevation_A_detectionSampleSize = float(item['data'][106])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_azimuth_A_detectionSampleSize = float(item['data'][107])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_range_A_detectionSampleSize = float(item['data'][108])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_height_A_absoluteSize = float(item['data'][109])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_length_A_absoluteSize = float(item['data'][110])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_width_A_absoluteSize = float(item['data'][111])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_seconds_A_exposureDuration = int(item['data'][112])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_nanoseconds_A_exposureDuration = int(item['data'][113])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_rangeMethod = E_Value_Source[item['data'][114]]
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_altitude_A_sourceLocationAccuracy = float(item['data'][115])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_latitude_A_sourceLocationAccuracy = float(item['data'][116])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_longitude_A_sourceLocationAccuracy = float(item['data'][117])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_altitude_A_sourceLocation = float(item['data'][118])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_latitude_A_sourceLocation = float(item['data'][119])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_longitude_A_sourceLocation = float(item['data'][120])
        ctypeStruct.A_suspensionCause = E_SuspensionCause[item['data'][121]]
        ctypeStruct.A_designatedInfo = item['data'][122].encode()
        ctypeStruct.A_designatedInfo_IsSet = int(item['data'][123])
        ctypeStruct.A_numberOfDetectionMethods = int(item['data'][124])
        ctypeStruct.A_numberOfDetectionMethods_IsSet = int(item['data'][125])
        for j, i in enumerate(range(0, 64, 2)):
            ctypeStruct.A_detectionMethods[j].A_detectorType = item['data'][126 + i].encode()
            ctypeStruct.A_detectionMethods[j].A_algorithm = item['data'][126 + i].encode()
        ctypeStruct.A_detectionMethods_ItemsCount_IsSet = int(item['data'][190])
        ctypeStruct.A_detectionMethods_ItemsCount = int(item['data'][191])
        ctypeStruct.A_snapshotAvailable = int(item['data'][192])
        output_lst.append({"time": item['time'], "data": ctypeStruct})
    return output_lst.copy()


def detection_log_parser(lst: list):
    output_list = []
    topicOptronics = "P_Tactical_Sensor_PSM::C_Detection"
    structType = DictTopicData[topicOptronics][DictTopicDataEnum.StructType]
    for item in lst:
        ctypeStruct = structType()
        ctypeStruct.A_platformId_A_sourceID = int(item['data']['A_platformId_A_sourceID'])
        ctypeStruct.A_systemId_A_sourceID = int(item['data']['A_systemId_A_sourceID'])
        ctypeStruct.A_moduleId_A_sourceID = int(item['data']['A_moduleId_A_sourceID'])
        ctypeStruct.A_seconds_A_timeOfDataGeneration = int(item['data']['A_seconds_A_timeOfDataGeneration'])
        ctypeStruct.A_nanoseconds_A_timeOfDataGeneration = int(item['data']['A_nanoseconds_A_timeOfDataGeneration'])
        ctypeStruct.A_msb_A_detectionUniqueID = int(item['data']['A_msb_A_detectionUniqueID'])
        ctypeStruct.A_lsb_A_detectionUniqueID = int(item['data']['A_lsb_A_detectionUniqueID'])
        ctypeStruct.A_confidence = float(item['data']['A_confidence'])
        ctypeStruct.A_detectionClassification = item['data']['A_detectionClassification'].encode()
        ctypeStruct.A_detectionClassScore = float(item['data']['A_detectionClassScore'])
        ctypeStruct.A_detectionForceType = int(item['data']['A_detectionForceType'])
        ctypeStruct.A_detectionThreatStatus = int(item['data']['A_detectionThreatStatus'])
        ctypeStruct.A_interception = int(item['data']['A_interception'])
        ctypeStruct.A_detectionStatus = int(item['data']['A_detectionStatus'])
        ctypeStruct.A_type = int(item['data']['A_type'])
        ctypeStruct.A_seconds_A_lifeSpan = int(item['data']['A_seconds_A_lifeSpan'])
        ctypeStruct.A_nanoseconds_A_lifeSpan = int(item['data']['A_nanoseconds_A_lifeSpan'])
        ctypeStruct.A_priority = int(item['data']['A_priority'])
        ctypeStruct.A_trajectoryType = int(item['data']['A_trajectoryType'])
        for i in range(15):
            ctypeStruct.A_method[i] = int(item['data'][f'A_method_{i}'])
        ctypeStruct.A_method_ItemsCount = int(item['data']['A_method_ItemsCount'])
        ctypeStruct.A_spatialParametersAvailable = eval(item['data']['A_spatialParametersAvailable'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_elevation_A_relativeLocationsBase = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_elevation_A_relativeLocationsBase'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_azimuth_A_relativeLocationsBase = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_azimuth_A_relativeLocationsBase'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_range_A_relativeLocationsBase = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_range_A_relativeLocationsBase'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_sensorInertialLocationAvailable = eval(
            item['data']['A_spatialInfo_A_physicalInfo_A_sensorInertialLocationAvailable'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_altitude_A_sensorInertialLocation = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_altitude_A_sensorInertialLocation'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_latitude_A_sensorInertialLocation = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_latitude_A_sensorInertialLocation'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_longitude_A_sensorInertialLocation = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_longitude_A_sensorInertialLocation'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_relativeLocationAvailable = eval(
            item['data']['A_spatialInfo_A_physicalInfo_A_relativeLocationAvailable'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_rangeAvailable = eval(
            item['data']['A_spatialInfo_A_physicalInfo_A_rangeAvailable'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_elevation_A_relativeLocation = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_elevation_A_relativeLocation'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_azimuth_A_relativeLocation = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_azimuth_A_relativeLocation'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_range_A_relativeLocation = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_range_A_relativeLocation'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_elevation_A_relativeLocationAccuracy = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_elevation_A_relativeLocationAccuracy'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_azimuth_A_relativeLocationAccuracy = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_azimuth_A_relativeLocationAccuracy'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_range_A_relativeLocationAccuracy = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_range_A_relativeLocationAccuracy'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_inertialLocationAvailable = eval(
            item['data']['A_spatialInfo_A_physicalInfo_A_inertialLocationAvailable'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_elevation_A_inertialLocation = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_elevation_A_inertialLocation'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_azimuth_A_inertialLocation = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_azimuth_A_inertialLocation'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_range_A_inertialLocation = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_range_A_inertialLocation'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_elevation_A_inertialLocationAccuracy = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_elevation_A_inertialLocationAccuracy'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_azimuth_A_inertialLocationAccuracy = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_azimuth_A_inertialLocationAccuracy'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_range_A_inertialLocationAccuracy = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_range_A_inertialLocationAccuracy'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_absoluteLocationAvailable = eval(
            item['data']['A_spatialInfo_A_physicalInfo_A_absoluteLocationAvailable'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_altitude_A_absoluteLocation = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_altitude_A_absoluteLocation'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_latitude_A_absoluteLocation = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_latitude_A_absoluteLocation'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_longitude_A_absoluteLocation = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_longitude_A_absoluteLocation'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_altitude_A_absoluteLocationAccuracy = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_altitude_A_absoluteLocationAccuracy'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_latitude_A_absoluteLocationAccuracy = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_latitude_A_absoluteLocationAccuracy'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_longitude_A_absoluteLocationAccuracy = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_longitude_A_absoluteLocationAccuracy'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_angularVelocityAvailable = eval(
            item['data']['A_spatialInfo_A_physicalInfo_A_angularVelocityAvailable'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_elevation_A_angularVelocity = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_elevation_A_angularVelocity'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_azimuth_A_angularVelocity = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_azimuth_A_angularVelocity'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_magnitude_A_angularVelocity = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_magnitude_A_angularVelocity'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_elevation_A_angularVelocityAccuracy = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_elevation_A_angularVelocityAccuracy'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_azimuth_A_angularVelocityAccuracy = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_azimuth_A_angularVelocityAccuracy'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_magnitude_A_angularVelocityAccuracy = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_magnitude_A_angularVelocityAccuracy'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_linearSpeedAvailable = eval(
            item['data']['A_spatialInfo_A_physicalInfo_A_linearSpeedAvailable'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_linearSpeed = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_linearSpeed'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_elevation_A_speedOrientation = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_elevation_A_speedOrientation'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_azimuth_A_speedOrientation = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_azimuth_A_speedOrientation'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_range_A_speedOrientation = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_range_A_speedOrientation'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_linearSpeedAccuracy = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_linearSpeedAccuracy'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_radialVelocityAvailable = eval(
            item['data']['A_spatialInfo_A_physicalInfo_A_radialVelocityAvailable'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_radialVelocity = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_radialVelocity'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_radialVelocityAccuracy = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_radialVelocityAccuracy'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_tangentialVelocityAvailable = eval(
            item['data']['A_spatialInfo_A_physicalInfo_A_tangentialVelocityAvailable'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_horizontalTangentialVelocity = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_horizontalTangentialVelocity'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_horizontalTangentialVelocityError = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_horizontalTangentialVelocityError'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_verticalTangentialVelocity = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_verticalTangentialVelocity'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_verticalTangentialVelocityError = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_verticalTangentialVelocityError'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_fieldOfViewAvailable = eval(
            item['data']['A_spatialInfo_A_physicalInfo_A_fieldOfViewAvailable'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_hfov_A_fieldOfView = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_hfov_A_fieldOfView'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_vfov_A_fieldOfView = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_vfov_A_fieldOfView'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_elevation_A_fovCenter_A_fieldOfView = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_elevation_A_fovCenter_A_fieldOfView'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_azimuth_A_fovCenter_A_fieldOfView = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_azimuth_A_fovCenter_A_fieldOfView'])
        ctypeStruct.A_spatialInfo.A_physicalInfo.A_range_A_fovCenter_A_fieldOfView = float(
            item['data']['A_spatialInfo_A_physicalInfo_A_range_A_fovCenter_A_fieldOfView'])
        for i in range(10):
            ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_recognizingDetectorTypes[i].value = item['data'][
                f'A_spatialInfo_A_descriptiveInfo_A_recognizingDetectorTypes_{i}'].encode()
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_recognizingDetectorTypes_ItemsCount = int(
            item['data']['A_spatialInfo_A_descriptiveInfo_A_recognizingDetectorTypes_ItemsCount'])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_classificationAvailable = eval(
            item['data']['A_spatialInfo_A_descriptiveInfo_A_classificationAvailable'])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_objectClassification = item['data'][
            'A_spatialInfo_A_descriptiveInfo_A_objectClassification'].encode()
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_classificationConfidence = float(
            item['data']['A_spatialInfo_A_descriptiveInfo_A_classificationConfidence'])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_elevation_A_detectionSampleSize = float(
            item['data']['A_spatialInfo_A_descriptiveInfo_A_elevation_A_detectionSampleSize'])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_azimuth_A_detectionSampleSize = float(
            item['data']['A_spatialInfo_A_descriptiveInfo_A_azimuth_A_detectionSampleSize'])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_range_A_detectionSampleSize = float(
            item['data']['A_spatialInfo_A_descriptiveInfo_A_range_A_detectionSampleSize'])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_height_A_absoluteSize = float(
            item['data']['A_spatialInfo_A_descriptiveInfo_A_height_A_absoluteSize'])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_length_A_absoluteSize = float(
            item['data']['A_spatialInfo_A_descriptiveInfo_A_length_A_absoluteSize'])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_width_A_absoluteSize = float(
            item['data']['A_spatialInfo_A_descriptiveInfo_A_width_A_absoluteSize'])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_seconds_A_exposureDuration = int(
            item['data']['A_spatialInfo_A_descriptiveInfo_A_seconds_A_exposureDuration'])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_nanoseconds_A_exposureDuration = int(
            item['data']['A_spatialInfo_A_descriptiveInfo_A_nanoseconds_A_exposureDuration'])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_rangeMethod = int(
            item['data']['A_spatialInfo_A_descriptiveInfo_A_rangeMethod'])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_altitude_A_sourceLocationAccuracy = float(
            item['data']['A_spatialInfo_A_descriptiveInfo_A_altitude_A_sourceLocationAccuracy'])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_latitude_A_sourceLocationAccuracy = float(
            item['data']['A_spatialInfo_A_descriptiveInfo_A_latitude_A_sourceLocationAccuracy'])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_longitude_A_sourceLocationAccuracy = float(
            item['data']['A_spatialInfo_A_descriptiveInfo_A_longitude_A_sourceLocationAccuracy'])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_altitude_A_sourceLocation = float(
            item['data']['A_spatialInfo_A_descriptiveInfo_A_altitude_A_sourceLocation'])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_latitude_A_sourceLocation = float(
            item['data']['A_spatialInfo_A_descriptiveInfo_A_latitude_A_sourceLocation'])
        ctypeStruct.A_spatialInfo.A_descriptiveInfo.A_longitude_A_sourceLocation = float(
            item['data']['A_spatialInfo_A_descriptiveInfo_A_longitude_A_sourceLocation'])
        ctypeStruct.A_suspensionCause = int(item['data']['A_suspensionCause'])
        ctypeStruct.A_designatedInfo = item['data']['A_designatedInfo'].encode()
        ctypeStruct.A_designatedInfo_IsSet = eval(item['data']['A_designatedInfo_IsSet'])
        ctypeStruct.A_numberOfDetectionMethods = int(item['data']['A_numberOfDetectionMethods'])
        ctypeStruct.A_numberOfDetectionMethods_IsSet = eval(item['data']['A_numberOfDetectionMethods_IsSet'])
        for j, i in enumerate(range(0, 64, 2)):
            ctypeStruct.A_detectionMethods[j].A_detectorType = item['data'][
                f'A_detectionMethods_{j}_A_detectorType'].encode()
            ctypeStruct.A_detectionMethods[j].A_algorithm = item['data'][f'A_detectionMethods_{j}_A_algorithm'].encode()
        ctypeStruct.A_detectionMethods_IsSet = eval(item['data']['A_detectionMethods_IsSet'])
        ctypeStruct.A_detectionMethods_ItemsCount = int(item['data']['A_detectionMethods_ItemsCount'])
        ctypeStruct.A_snapshotAvailable = eval(item['data']['A_snapshotAvailable'])

        output_list.append({"time": item['time'], "data": ctypeStruct})
    return output_list.copy()


def optronics_log_parser(lst: list):
    parsed_detections_list = detection_log_parser(lst)
    output_list = []
    topicOptronics = "P_Tactical_Sensor_PSM::C_Detection_Optronics"
    structType = DictTopicData[topicOptronics][DictTopicDataEnum.StructType]
    for item in parsed_detections_list:
        ctypeStruct = item["data"]
        ctypeStruct.__class__ = structType
        output_list.append({"time": item['time'], "data": ctypeStruct})
    return output_list.copy()


def aps_log_parser(lst: list):
    parsed_detections_list = detection_log_parser(lst)
    output_list = []
    topicOptronics = "P_Tactical_Sensor_PSM::C_Detection_Aps"
    structType = DictTopicData[topicOptronics][DictTopicDataEnum.StructType]
    for item in parsed_detections_list:
        ctypeStruct = item["data"]
        ctypeStruct.__class__ = structType
        output_list.append({"time": item['time'], "data": ctypeStruct})
    return output_list.copy()


def benchmark_log_parser(lst: list):
    output_list = []
    for item in lst:
        output = {"time": float(item["time"]), "unprocessed_detection": float(item["unprocessed_detection"]),
                  "tracks_amount": float(item["tracks_amount"]),
                  "last_detection_processing_time_in_seconds": float(item["last_detection_processing_time_in_seconds"]),
                  "last_detection_processing_time_in_hertz": float(item["last_detection_processing_time_in_hertz"])}

        output_list.append(output)
    return output_list
