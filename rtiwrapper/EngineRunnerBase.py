from rtiwrapper.Common import *
import os


class EngineRunnerBase:
    def __init__(self):
        pass

    def PublishEnginesVersion(self, resourceSpec):
        try:
            enginesVersionFile = 'EnginesVersion.txt'
            versionEnginesNum = ""
            if os.path.exists(enginesVersionFile):
                with open(enginesVersionFile, 'r') as f:
                    versionEnginesNum = f.readline()
            if not versionEnginesNum:
                print("EnginesVersion file is empty")
                return

            vectorSegmentsVersion = versionEnginesNum.split('.')
            resourceSpec.__setattr__("A_major_A_softwareVersion", int(vectorSegmentsVersion[0]))
            resourceSpec.__setattr__("A_minor_A_softwareVersion", int(vectorSegmentsVersion[1]))
            resourceSpec.__setattr__("A_revision_A_softwareVersion", int(vectorSegmentsVersion[2]))
            resourceSpec.__setattr__("A_build_A_softwareVersion", int(vectorSegmentsVersion[3]))
        except Exception as e:
            print("Engines Version number is not readable. Error: ", e)
            return

    def PublishResourceSpecification(self, rtiWrapper, sourceID, typeName):
        """
         publish P_Maintenance_PSM::C_Resource_Specification:
        :param rtiWrapper: API to DDS
        :param sourceID: Ctypes_T_Identifier
        :param typeName: string
        :return:
        """
        timeNow = DataTimeType()
        topicMaintResourceSpec = "P_Maintenance_PSM::C_Resource_Specification"
        resourceSpec = C_Resource_Specification(sourceID, timeNow.A_second,
                                                timeNow.A_nanoseconds, str.encode(typeName))
        self.PublishEnginesVersion(resourceSpec)
        rtiWrapper.Publish(topicMaintResourceSpec, resourceSpec)

    def PublishTacticalSensorSpec(self, rtiWrapper, sourceID):
        """
        publish tactical Sensor Specification:
        :param rtiWrapper:API to DDS
        :param sourceID: Ctypes_T_Identifier
        :return:
        """
        timeNow = DataTimeType()
        topic_Tactical_Sensor_Spec = "P_Tactical_Sensor_PSM::C_Tactical_Sensor_Specification"
        Tactical_Sensor_Spec = C_Tactical_Sensor_Specification(sourceID, timeNow.A_second, timeNow.A_nanoseconds)
        detectorTypesSupportArr = Tactical_Sensor_Spec.__getattribute__("A_detectorTypesSupport")
        AssignStringToBuffer("ATR", detectorTypesSupportArr[0])
        AssignStringToBuffer("VMD", detectorTypesSupportArr[1])

        Tactical_Sensor_Spec.A_detectorTypesSupport = detectorTypesSupportArr
        Tactical_Sensor_Spec.__setattr__("A_detectorTypesSupport_ItemsCount", 2)
        Tactical_Sensor_Spec.__setattr__("A_accuracySupport", True)
        Tactical_Sensor_Spec.__setattr__("A_videoDetector", True)
        Tactical_Sensor_Spec.__setattr__("A_maxNumberOfDetectionLocations", 100)
        rtiWrapper.Publish(topic_Tactical_Sensor_Spec, Tactical_Sensor_Spec)

    def PublishTacticalSensorStatus(self, rtiWrapper, sourceID):
        """
        publish C_Tactical_Sensor status
        :param rtiWrapper:API to DDS
        :param sourceID: Ctypes_T_Identifier
        :return:
        """
        timeNow = DataTimeType()
        topic_Tactical_Sensor = "P_Tactical_Sensor_PSM::C_Tactical_Sensor"
        tactical_Sensor = C_Tactical_Sensor(sourceID, timeNow.A_second, timeNow.A_nanoseconds, 0, 0, 0)
        rtiWrapper.Publish(topic_Tactical_Sensor, tactical_Sensor)

