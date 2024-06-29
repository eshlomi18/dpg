import sys
from rtiwrapper.Common import *
import os
import ctypes
import platform


class RtiConnectorWrapper:
    def __init__(self, dictConfigDefs):
        self.rti_connector = None
        self.dictConfigDefs = dictConfigDefs
        self.dll = None

    def Create(self):
        print("Create:")
        # Load the shared library into ctypes
        folder = os.path.dirname(os.path.abspath(__file__))
        rtiConnectorPath = sys.argv[int(Configuration.PathRtiConnectorLib)]
        os_name = platform.system()
        if os_name == "Windows":
            print("Create ::Windows ")
            dll_path = os.path.join(folder, rtiConnectorPath)  # "RtiConnectorModule.dll"
            abs_path_to_dlls = folder + "\\" + os.path.dirname(rtiConnectorPath)
            abs_path_to_dlls = abs_path_to_dlls.replace("\\", "/")
            os.environ['PATH'] = abs_path_to_dlls + os.pathsep + os.environ['PATH']
        else:
            print("Create :: linux ")
            dll_path = rtiConnectorPath
        dll_path = dll_path.replace("\\", "/")
        dll = ctypes.CDLL(dll_path)
        self.dll = dll

        dataSetParam = self.dictConfigDefs[configDefsKeysEnum.BARAK_DATASET]  # " path to RtiConnectorDataSet.xml"
        dataset_path = os.path.join(folder, dataSetParam)
        dataset_path = ctypes.create_string_buffer(bytes(dataset_path, encoding='ascii'))

        qosFileParam = self.dictConfigDefs[configDefsKeysEnum.BARAK_QOS_FILE_PATH]  # path to "BarakQosProfile.xml"
        qos_path = os.path.join(folder, qosFileParam)
        qos_path = ctypes.create_string_buffer(bytes(qos_path, encoding='ascii'))

        dataset_name = "Barak"
        dataset_name = ctypes.create_string_buffer(bytes(dataset_name, encoding='ascii'))

        monitorParams = self.dictConfigDefs[configDefsKeysEnum.COMM_DEFS_DE]
        remoteAddress = monitorParams.split(";")[int(ClientParams.RemoteIP)]  # "127.0.0.1"
        remoteAddress = ctypes.create_string_buffer(bytes(remoteAddress, encoding='ascii'))

        remotePort = monitorParams.split(";")[int(ClientParams.RemotePort)]
        c_remotePort = ctypes.create_string_buffer(bytes(remotePort, encoding='ascii'))  # 38001

        localAddress = monitorParams.split(";")[int(ClientParams.LocalIP)]
        localAddress = ctypes.create_string_buffer(bytes(localAddress, encoding='ascii'))

        localPort = monitorParams.split(";")[int(ClientParams.LocalPort)]
        c_localPort = ctypes.create_string_buffer(bytes(localPort, encoding='ascii'))  # 38002

        dll.create.restype = ctypes.c_void_p
        try:
            self.rti_connector = ctypes.c_void_p(
                dll.create(dataset_path, dataset_name, remoteAddress, ctypes.c_ushort(int(remotePort)), localAddress,
                           ctypes.c_ushort(int(localPort)), qos_path))
        except Exception as e:
            print("cannot create rtiConnector object  : ", e)
        self.dll.rti_connector_pub.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_int32]
        self.dll.rti_connector_pub.restype = ctypes.c_bool
        self.dll.rti_connector_sub.restype = ctypes.c_int

        dll.rti_connector_get.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_int32]
        dll.rti_connector_get.restype = ctypes.c_bool

    def Publish(self, topic, buffer, aging=None):
        structType = DictTopicData[topic][DictTopicDataEnum.StructType]
        bufferSize = ctypes.sizeof(structType)
        topic = ctypes.create_string_buffer(bytes(topic, encoding='ascii'))
        if aging != None:
            aging = ctypes.byref(aging)
        self.dll.rti_connector_pub(self.rti_connector, topic, ctypes.byref(buffer), ctypes.c_int32(bufferSize), aging)

    def Subscribe(self, topic, handle_sub_function, filterQuery):
        handle_event_type = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_size_t,
                                             ctypes.c_char_p)  # ,ctypes.c_void_p    result type and then args
        handle_event_func = handle_event_type(handle_sub_function)
        functionsHandleSubList.append(handle_event_func)
        topic = ctypes.create_string_buffer(bytes(topic, encoding='ascii'))
        if filterQuery != None:
            filterQuery = ctypes.create_string_buffer(bytes(filterQuery, encoding='ascii'))
        self.dll.rti_connector_sub(self.rti_connector, topic, handle_event_func, filterQuery)

    def Get(self, topic, buffer):
        structType = DictTopicData[topic][DictTopicDataEnum.StructType]
        bufferSize = ctypes.sizeof(structType)
        topic = ctypes.create_string_buffer(bytes(topic, encoding='ascii'))
        self.dll.rti_connector_get(self.rti_connector, topic, ctypes.byref(buffer), ctypes.c_int32(bufferSize))

    def GetFilterQuery(self, listOfIdentifiers, isRecipientID, platformId):
        """
        :param listOfIdentifiers: all identifiers we accept to get msgs from them . list of Ctypes_T_Identifier
        :param isRecipientID: bool - decide which field in the msg the filter is working on
        :return: Query
        """
        if type(listOfIdentifiers) != type([]):  # if it's one ID out of a list
            listOfIdentifiers = [listOfIdentifiers]

        filterQuery = ""
        if isRecipientID:
            filterID = "A_recipientID"
        else:
            filterID = "A_sourceID"
        filterQuery += filterID + ".A_platformId = " + platformId + " AND "
        filterQuery += "("
        try:
            listOfIdentifiers_lastIndex = len(listOfIdentifiers) - 1
            for i, identifier in enumerate(listOfIdentifiers):
                systemId = identifier.__getattribute__("A_systemId")
                moduleId = identifier.__getattribute__("A_moduleId")
                filterQuery += "(" + filterID + ".A_systemId = " + str(
                    systemId) + " AND " + filterID + ".A_moduleId = " + str(moduleId) + ")"
                if i != listOfIdentifiers_lastIndex:
                    filterQuery += " OR "
        except Exception as e:
            print("cannot parsing identifiers to create a filer  : ", e)
        filterQuery += ")"
        return filterQuery
