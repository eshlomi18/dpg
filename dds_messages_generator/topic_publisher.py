import numpy as np
import json
import dds_messages_generator.parser_tools
import time
from utils.constants import DetectionType, NogaScanState, RangeMethod
from rtiwrapper.Common import DictTopicData, DictTopicDataEnum
from utils.general_functions import is_this_a_log_file, time_of_data_generation, validate_entry


def open_params_file():
    with open('dds_messages_generator/params.json', 'r') as file:
        json_data = file.read()
    params_file = json.loads(json_data)
    return params_file


def optronics_or_aps(app, scene_name='dds_messages_generator/records/for_publish/noga.csv',
                     topic="P_Tactical_Sensor_PSM::C_Detection_Optronics"):
    output_list = dds_messages_generator.parser_tools.load_scenario(scene_name)
    if is_this_a_log_file(output_list):
        if topic == "P_Tactical_Sensor_PSM::C_Detection_Optronics":
            parsed_output = dds_messages_generator.parser_tools.optronics_log_parser(output_list)
        else:
            parsed_output = dds_messages_generator.parser_tools.aps_log_parser(output_list)
    else:
        parsed_output = dds_messages_generator.parser_tools.optronics_data_parser(output_list)
    first_detection = parsed_output[0]
    params = open_params_file()
    topic = topic
    source_id_parts = None

    empty_entry = True
    # taking all the entrys
    for attribute_name, value in vars(app).items():
        if "entry" in attribute_name and "draggable" not in attribute_name:
            entry = getattr(app, attribute_name)
            if attribute_name in ['tank_altitude_entry', 'tank_latitude_entry', 'tank_longitude_entry']:
                condition = app.tank_location_available_value_inside.get() == "True"
                error_message = f"{attribute_name.replace('_entry', '')} must receive a value"
            elif attribute_name in ['elevation_entry', 'azimuth_entry', 'range_entry']:
                condition = app.target_polar_available_value_inside.get() == "True"
                error_message = f"{attribute_name.replace('_entry', '')} must receive a value"
            elif attribute_name in ['target_altitude_entry', 'target_latitude_entry', 'target_longitude_entry']:
                condition = app.target_geo_available_value_inside.get() == "True"
                error_message = f"{attribute_name.replace('_entry', '')} must receive a value"
            # for the rest of the entrys
            else:
                condition = True
                error_message = f"{attribute_name.replace('_entry', '')} must receive a value"
            # checking if the entry is empty
            if not validate_entry(entry, condition, error_message):
                empty_entry = False

    # if even one entry is empty ,immediately exit from the method without performing the rest of the code.
    # ensure that the function terminates early when an empty entry is encountered,
    # saving unnecessary processing time and preventing any undesired behavior that could occur
    # due to missing or invalid input
    if empty_entry is False:
        return

    source_ids = {"commander": ["1.2.1", "MANUAL"], "noga": ["1.14.1", "ATR"],
                  "maanak": ["1.21.1", "MAANAK"],
                  "windcoat": ["1.22.1", "Windcoat"], "gunner": ["1.10.1", "MANUAL"],
                  "loader": ["1.11.1", "MANUAL"], "DELETED": ["1.2.1", "MANUAL"], "DH_TACT_SENSOR": ["1.24.3", "ATR"]}

    selected_value = app.source_id_value_inside.get()
    if selected_value in source_ids:
        source_id = source_ids[selected_value][params["FULL_SOURCE_ID_NUMBER"]]
        source_id_parts = str(source_id).split(".")
    if selected_value == "DELETED":
        first_detection['data'].A_detectionStatus = 3

    first_detection['data'].A_platformId_A_sourceID = int(source_id_parts[params["PLATFORM_ID"]])
    first_detection['data'].A_systemId_A_sourceID = int(source_id_parts[params["SYSTEM_ID"]])
    first_detection['data'].A_moduleId_A_sourceID = int(source_id_parts[params["MODULE_ID"]])

    first_detection['data'].A_detectionClassification = bytes(app.classification_value_inside.get(), 'utf-8')
    first_detection['data'].A_detectionClassScore = float(app.classscore_entry.get())
    first_detection['data'].A_type = app.value

    if app.tank_altitude_entry.cget("state") != "disabled":
        first_detection['data'].A_spatialInfo.A_physicalInfo.A_sensorInertialLocationAvailable = True
        first_detection['data'].A_spatialInfo.A_physicalInfo.A_altitude_A_sensorInertialLocation = \
            float(app.tank_altitude_entry.get())
        if app.tank_latitude_value_inside.get() == "deg":
            first_detection['data'].A_spatialInfo.A_physicalInfo.A_latitude_A_sensorInertialLocation = np.deg2rad(
                float(app.tank_latitude_entry.get()))
            first_detection['data'].A_spatialInfo.A_physicalInfo.A_longitude_A_sensorInertialLocation = np.deg2rad(
                float(app.tank_longitude_entry.get()))
        else:
            first_detection['data'].A_spatialInfo.A_physicalInfo.A_latitude_A_sensorInertialLocation = float(
                app.tank_latitude_entry.get())
            first_detection['data'].A_spatialInfo.A_physicalInfo.A_longitude_A_sensorInertialLocation = float(
                app.tank_longitude_entry.get())

    else:
        first_detection['data'].A_spatialInfo.A_physicalInfo.A_sensorInertialLocationAvailable = False
        first_detection['data'].A_spatialInfo.A_physicalInfo.A_altitude_A_sensorInertialLocation = 0
        first_detection['data'].A_spatialInfo.A_physicalInfo.A_latitude_A_sensorInertialLocation = 0
        first_detection['data'].A_spatialInfo.A_physicalInfo.A_longitude_A_sensorInertialLocation = 0

    if app.elevation_entry.cget("state") != "disabled":
        first_detection['data'].A_spatialInfo.A_physicalInfo.A_inertialLocationAvailable = True
        first_detection['data'].A_spatialInfo.A_physicalInfo.A_range_A_inertialLocation = float(app.range_entry.get())
        if app.azimuth_value_inside.get() == "deg":
            first_detection['data'].A_spatialInfo.A_physicalInfo.A_elevation_A_inertialLocation = np.deg2rad(
                float(app.elevation_entry.get()))
            first_detection['data'].A_spatialInfo.A_physicalInfo.A_azimuth_A_inertialLocation = np.deg2rad(
                float(app.azimuth_entry.get()))
        else:
            first_detection['data'].A_spatialInfo.A_physicalInfo.A_elevation_A_inertialLocation = float(
                app.elevation_entry.get())
            first_detection['data'].A_spatialInfo.A_physicalInfo.A_azimuth_A_inertialLocation = float(
                app.azimuth_entry.get())
    else:
        first_detection['data'].A_spatialInfo.A_physicalInfo.A_inertialLocationAvailable = False
        first_detection['data'].A_spatialInfo.A_physicalInfo.A_elevation_A_inertialLocation = 0
        first_detection['data'].A_spatialInfo.A_physicalInfo.A_azimuth_A_inertialLocation = 0
        first_detection['data'].A_spatialInfo.A_physicalInfo.A_range_A_inertialLocation = 0

    if app.target_altitude_entry.cget("state") != "disabled":
        first_detection['data'].A_spatialInfo.A_physicalInfo.A_absoluteLocationAvailable = True
        first_detection['data'].A_spatialInfo.A_physicalInfo.A_altitude_A_absoluteLocation = float(
            app.target_altitude_entry.get())
        if app.tank_latitude_value_inside.get() == "deg":
            first_detection['data'].A_spatialInfo.A_physicalInfo.A_latitude_A_absoluteLocation = np.deg2rad(
                float(app.target_latitude_entry.get()))
            first_detection['data'].A_spatialInfo.A_physicalInfo.A_longitude_A_absoluteLocation = np.deg2rad(
                float(app.target_longitude_entry.get()))
        else:
            first_detection['data'].A_spatialInfo.A_physicalInfo.A_latitude_A_absoluteLocation = float(
                app.target_latitude_entry.get())
            first_detection['data'].A_spatialInfo.A_physicalInfo.A_longitude_A_absoluteLocation = float(
                app.target_longitude_entry.get())
    else:
        first_detection['data'].A_spatialInfo.A_physicalInfo.A_absoluteLocationAvailable = False
        first_detection['data'].A_spatialInfo.A_physicalInfo.A_altitude_A_absoluteLocation = 0
        first_detection['data'].A_spatialInfo.A_physicalInfo.A_latitude_A_absoluteLocation = 0
        first_detection['data'].A_spatialInfo.A_physicalInfo.A_longitude_A_absoluteLocation = 0

    first_detection['data'].A_msb_A_detectionUniqueID = int(app.msb_entry.get())
    first_detection['data'].A_lsb_A_detectionUniqueID = int(app.lsb_entry.get())
    first_detection['data'].A_seconds_A_timeOfDataGeneration = int(time.time())
    first_detection['data'].A_nanoseconds_A_timeOfDataGeneration = time.time_ns() % 1000000000

    name_to_value = {
        "no range": RangeMethod.UNKNOWN.value,
        "calc": RangeMethod.CALCULATED.value,
        "measured": RangeMethod.MEASURED.value,
        "manual": RangeMethod.REPORTED.value,
    }

    first_detection['data'].A_spatialInfo.A_descriptiveInfo.A_rangeMethod = name_to_value[
        app.range_method_value_inside.get()]
    first_detection['data'].A_spatialInfo.A_descriptiveInfo.A_recognizingDetectorTypes[0].value = \
        source_ids[selected_value][params["RECOGNIZING_DETECTOR_TYPE"]].encode('utf-8')

    first_detection['data'].A_detectionMethods_IsSet = True
    first_detection['data'].A_numberOfDetectionMethods_IsSet = True
    first_detection['data'].A_threatFamily = 0  # A default value without it, the topic APS collapses

    if selected_value == 'DH_TACT_SENSOR':
        first_detection['data'].A_spatialInfo.A_descriptiveInfo.A_recognizingDetectorTypes[0].value = b"ADV"
        first_detection['data'].A_detectionMethods_ItemsCount = 3
        first_detection['data'].A_numberOfDetectionMethods = 3
        first_detection['data'].A_detectionMethods[0].A_detectorType = b"rangeType"
        first_detection['data'].A_detectionMethods[0].A_algorithm = b"E_DH_RangeType"
        first_detection['data'].A_detectionMethods[1].A_detectorType = b"targetType"
        first_detection['data'].A_detectionMethods[1].A_algorithm = b"E_DH_TargetType"
        first_detection['data'].A_detectionMethods[2].A_detectorType = b"detectChan"
        first_detection['data'].A_detectionMethods[2].A_algorithm = b"detectChan"
        first_detection['data'].A_detectionMethods[3].A_detectorType = b"activity"
        first_detection['data'].A_detectionMethods[3].A_algorithm = b"E_DH_Activity"
    # first_detection['data'].A_designatedInfo
    # first_detection['data'].A_detectionStatus = 4
    app.rtiConnectorWrapperObject.Publish(topic, first_detection['data'])
    print("published")


def mount(app, scene_name='dds_messages_generator/records/for_publish/mount.csv'):
    loaded_scenario_data = dds_messages_generator.parser_tools.load_scenario(scene_name)
    parsed_data = dds_messages_generator.parser_tools.mount_data_parser(loaded_scenario_data)
    first_detection = parsed_data[0]
    topic_mount = "P_Mount_PSM::C_Rot_Mount"
    name_to_value = {"stare": NogaScanState.OFF.value, "scan": NogaScanState.IN_PROGRESS.value}

    while not app.is_mount_thread_needs_to_stop:
        seconds, nanoseconds = time_of_data_generation()
        first_detection['data'].A_seconds_A_timeOfDataGeneration = seconds
        first_detection['data'].A_nanoseconds_A_timeOfDataGeneration = nanoseconds
        first_detection['data'].A_scanState = name_to_value[app.noga_status_value_inside.get()]
        app.rtiConnectorWrapperObject.Publish(topic_mount, first_detection['data'])
        time.sleep(0.09)


def position(app):
    topic = "P_Navigation_PSM::C_Position"
    structType = DictTopicData[topic][DictTopicDataEnum.StructType]
    output = structType()
    while not app.is_position_thread_needs_to_stop:
        seconds, nanoseconds = time_of_data_generation()
        output.A_seconds_A_timeOfDataGeneration = seconds
        output.A_nanoseconds_A_timeOfDataGeneration = nanoseconds
        output.A_altitude_A_currentPosition = app.position_output.A_altitude_A_currentPosition
        output.A_latitude_A_currentPosition = app.position_output.A_latitude_A_currentPosition
        output.A_longitude_A_currentPosition = app.position_output.A_longitude_A_currentPosition
        app.rtiConnectorWrapperObject.Publish(topic, output)
        time.sleep(1)


def aps(app, scene_name='dds_messages_generator/records/for_publish/windcoat.csv'):
    output_list = dds_messages_generator.parser_tools.load_scenario(scene_name)
    if is_this_a_log_file(output_list):
        parsed_output = dds_messages_generator.parser_tools.aps_log_parser(output_list)

    else:
        parsed_output = dds_messages_generator.parser_tools.optronics_data_parser(output_list)
    first_detection = parsed_output[0]
    topic = "P_Tactical_Sensor_PSM::C_Detection_Aps"
    first_detection['data'].A_type = app.value
    app.rtiConnectorWrapperObject.Publish(topic, first_detection['data'])
    print("published")
