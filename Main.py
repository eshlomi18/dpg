import math
import tkinter as tk
import numpy as np
import pyproj
from PIL import Image, ImageTk
import os
import dds_messages_generator.topic_publisher
from utils.draggable_widget import DraggableWidget
from utils.constants import DEFAULT_HERTZ_WHEN_NO_ELAPSED_TIME
from utils.conversions import polar_to_gps, gps_to_polar, new_id, uuid_to_int
import dds_messages_generator.parser_tools
import sys
from rtiwrapper.RtiConnectorWrapper import RtiConnectorWrapper
import json
from tkinter import filedialog
import threading
from rtiwrapper.Common import *
from utils.general_functions import is_this_a_log_file

transformer = pyproj.Transformer.from_proj(4326, pyproj.Proj(proj='utm', zone=36, ellps='WGS84'))


class App:
    # NOTE TO MYSELF: every time you add widget you need to do save and rerun the gui, and then you will see it in the 
    # left corner. after you will do save again you will see his name and position in the widget_positions.txt file.
    # Pay attention not to leave empty lines in the widget_positions.txt, not even at the end of the file
    # every time I create a new attribute I need to pay attention that his name
    # is in the list of the not_in_the_name list in the save method
    # There are parameters that are sent to functions that appear to be of no use, but during the run they are used
    def __init__(self):
        self.is_mount_thread_needs_to_stop = False
        self.is_position_thread_needs_to_stop = False
        self.position_output = None
        self.file_name = None
        self.scenario_running = None
        self.scenario_thread = None
        self.analyzed_data = None
        self.value = None
        self.rtiConnectorWrapperObject = None
        self.root = tk.Tk()
        self.root.title("GUI")
        self.root.geometry("670x500")

        # placing the root window
        self.root.geometry('+{}+{}'.format((self.root.winfo_screenwidth() // 2) - (self.root.winfo_reqwidth() // 2),
                                           (self.root.winfo_screenheight() // 4) - (self.root.winfo_reqheight() // 4)))
        # widgets creation
        self.label_widgets_creation()
        self.menu_widgets_creation()
        self.entry_widgets_creation()
        self.button_widgets_creation()

        # disable on the start because the default value is deg
        # we want to use these buttons just when the units of measure are radians
        self.polar2geo_button.configure(state='disabled')
        self.geo2polar_button.configure(state='disabled')

        self.start_sending_noga_status_button.configure(state='disabled')
        self.stop_sending_noga_status_button.configure(state='disabled')
        self.stop_sending_location_button.configure(state=tk.DISABLED)

        self.save_button = tk.Button(self.root, text="Save", command=self.save_widgets)
        # self.save_button.place(x=50, y=460)

        self.move_button = tk.Button(self.root, text="Move", command=self.enable_dragging)
        # self.move_button.place(x=100, y=460)

        # Makes sure that the same conversion value is not selected twice
        # (in the first case, makes sure that it is not a degree again)
        self.flag = True
        self.rti_connection()
        self.position_default_values()

    def label_widgets_creation(self):
        labels_widgets = {
            "source_id": {"text": "source_id"},
            "classification": {"text": "classification"},
            "classscore": {"text": "classscore"},
            "tank_location_available": {"text": "tank_location_available", "font": "bold"},
            "tank_altitude": {"text": "tank_altitude"},
            "tank_altitude_measurement_units": {"text": "M"},
            "tank_latitude": {"text": "tank_latitude"},
            "tank_longitude": {"text": "tank_longitude"},
            "target_polar_available": {"text": "target_polar_available", "font": "bold"},
            "elevation": {"text": "elevation"},
            "azimuth": {"text": "azimuth"},
            "range": {"text": "range"},
            "range_measurement_units": {"text": "M"},
            "target_geo_available": {"text": "target_geo_available", "font": "bold"},
            "target_altitude": {"text": "target_altitude"},
            "target_altitude_measurement_units": {"text": "M"},
            "target_latitude": {"text": "target_latitude"},
            "target_longitude": {"text": "target_longitude"},
            "uniq_id": {"text": "uniq_id"},
            "msb": {"text": "msb"},
            "lsb": {"text": "lsb"},
            "type": {"text": "type"},
            "range_method": {"text": "range_method"},
            "noga_status": {"text": "noga_status"},

            # add more labels here if needed
        }
        for name, props in labels_widgets.items():
            label = tk.Label(self.root, text=props["text"], font=props.get("font"))  # label text and font
            draggable_widget = DraggableWidget(label)
            setattr(self, f"{name}", label)  # create an attribute on the instance that references the Label object
            setattr(self, f"draggable_{name}", draggable_widget)

    def menu_widgets_creation(self):
        # create a dictionary of options for each menu
        menu_widgets = {
            "source_id": {"default": "commander",
                          "values": ["noga", "maanak", "commander", "windcoat", "gunner", "loader", "DELETED",
                                     "DH_TACT_SENSOR"], "command": self.influenced_by_the_source_id},
            "classification": {"default": "General Enemy",
                               "values": ["Person", "Car", "General Enemy", "Infantry", "AT", "AFV", "Motorcycle",
                                          "Windcoat", "Marker"]},
            "tank_location_available": {"default": "True", "values": ["True", "False"], "command": self.menu_clicked},
            "tank_latitude": {"default": "deg", "values": ["deg", "rad"], "command": self.deg_rad},
            "tank_longitude": {"default": "deg", "values": ["deg", "rad"], "command": self.deg_rad},
            "target_polar_available": {"default": "True", "values": ["True", "False"], "command": self.menu_clicked},
            "elevation": {"default": "deg", "values": ["deg", "rad"], "command": self.deg_rad},
            "azimuth": {"default": "deg", "values": ["deg", "rad"], "command": self.deg_rad},
            "target_geo_available": {"default": "True", "values": ["True", "False"], "command": self.menu_clicked},
            "target_latitude": {"default": "deg", "values": ["deg", "rad"], "command": self.deg_rad},
            "target_longitude": {"default": "deg", "values": ["deg", "rad"], "command": self.deg_rad},
            "type": {"default": "DETECTION", "values": ["DETECTION"]},
            "range_method": {"default": "no range", "values": ["no range", "calc", "measured", "manual"]},
            "noga_status": {"default": "stare", "values": ["stare", "scan"]},
            # add more menus here if needed
        }
        # create an option menu for each option in the dictionary
        for name, props in menu_widgets.items():
            default = props["default"]
            values = props["values"]
            command = props.get("command")  # optional, use None if not specified

            # create a StringVar to keep track of the selected value
            var = tk.StringVar(self.root)
            var.set(default)

            # create the OptionMenu widget
            menu = tk.OptionMenu(self.root, var, *values, command=command)

            # add the draggable widget functionality
            draggable_menu = DraggableWidget(menu)

            # save the menu and its associated StringVar as instance attributes
            setattr(self, f"{name}_menu", menu)
            setattr(self, f"{name}_value_inside", var)
            setattr(self, f"draggable_{name}_menu", draggable_menu)

            # if classification menu, update the default value based on the selected source_id
            if name == "classification":
                var.trace_add("write", lambda *_: self.classifications_based_on_selected_sensor)
            if name == "type":  # default value for the first run
                self.value = 0

    def entry_widgets_creation(self):
        entry_widgets = {
            "classscore": {"default_value": "0.7"},
            "tank_altitude": {"default_value": "73.0"},
            "tank_latitude": {"default_value": "32.66735998048158"},
            "tank_longitude": {"default_value": "35.103842456107564"},
            "elevation": {"default_value": "-0.0353396946160196"},
            "azimuth": {"default_value": "-155.96792315810453"},
            "range": {"default_value": "250.73443455288"},
            "target_altitude": {"default_value": "72.84534850803514"},
            "target_latitude": {"default_value": "32.66531384562824"},
            "target_longitude": {"default_value": "35.10270581260785"},
            "msb": {"default_value": "-7232807926196496584"},
            "lsb": {"default_value": "2647935891334119835"},
            # add more entry here if needed
        }
        for name, props in entry_widgets.items():
            entry = tk.Entry(self.root)
            entry.insert(0, str(props["default_value"]))
            draggable_widget = DraggableWidget(entry)
            setattr(self, f"{name}_entry", entry)
            setattr(self, f"draggable_{name}_entry", draggable_widget)

        # creating canvas with a selected image and adding it to the gui window
        image_widgets = {
            "tank": {"file": "merkava4.jpg", "width": 70, "height": 50},
            "mantak": {"file": "mantak.png", "width": 70, "height": 50},
            "ministry_of_defence": {"file": "ministry_of_defence.png", "width": 70, "height": 60},
        }
        for name, props in image_widgets.items():
            canvas = tk.Canvas(self.root, width=props["width"], height=props["height"] + 10)  # canvas size
            image = Image.open(os.path.join(os.getcwd(), "pictures", props["file"]))  # image path
            image.thumbnail((props["width"], props["height"]), Image.LANCZOS)  # Image size keep aspect ratio
            image_tk = ImageTk.PhotoImage(image)  # Necessary to work with an image in tkinter
            canvas.create_image(5, 4, image=image_tk, anchor=tk.NW)  # creates an image item on the Canvas
            draggable_widget = DraggableWidget(canvas)
            # The purpose of these setattr() calls is to create new attributes on the instance that reference
            # the Canvas, PhotoImage, and DraggableWidget objects that were created in the constructor
            setattr(self, f"{name}_canvas", canvas)
            setattr(self, f"{name}_image_tk", image_tk)
            setattr(self, f"draggable_{name}_image_canvas", draggable_widget)

    def button_widgets_creation(self):
        button_widgets = {
            "publish_button": {"text": "publish", "command": self.publish},
            "polar2geo_button": {"text": "polar2geo", "command": self.polar2geo},
            "geo2polar_button": {"text": "geo2polar", "command": self.geo2polar},
            "csv_loader_button": {"text": "csv loader", "command": self.csv_file_loader},
            "run_button": {"text": "run", "command": self.start_scenario},
            "stop_button": {"text": "stop", "command": self.stop_scenario},
            "benchmark_button": {"text": "engine_benchmark", "command": self.engine_benchmark},
            "update_location_button": {"text": "update_location", "command": self.update_tank_location},
            "start_sending_location_button": {"text": "start_sending_location", "command": self.start_position_thread},
            "start_sending_noga_status_button": {"text": "start_sending_noga_status",
                                                 "command": self.start_mount_thread},
            "stop_sending_location_button": {"text": "stop_sending_location", "command": self.stop_position_thread},
            "stop_sending_noga_status_button": {"text": "stop_sending_noga_status", "command": self.stop_mount_thread}
            # add more buttons here if needed
        }

        for name, props in button_widgets.items():
            button = tk.Button(self.root, text=props["text"], command=props["command"])
            draggable_widget = DraggableWidget(button)
            setattr(self, name, button)
            setattr(self, f"draggable_{name}", draggable_widget)

        # Disable the run and stop buttons initially
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.benchmark_button.config(state=tk.DISABLED)

    def position_default_values(self):
        topic = "P_Navigation_PSM::C_Position"
        structType = DictTopicData[topic][DictTopicDataEnum.StructType]
        self.position_output = structType()
        self.position_output.A_altitude_A_currentPosition = 73.0
        self.position_output.A_latitude_A_currentPosition = 0.570152989593634
        self.position_output.A_longitude_A_currentPosition = 0.61267763096045

    def rti_connection(self):
        # connection to rti
        configDefsPath = 'dds_messages_generator/configDefs.json'
        with open(configDefsPath) as f:
            dictConfigDefs = json.load(f)
        sys.argv.append("dds_messages_generator/configDefs.json")
        sys.argv.append("dependencies/RtiConnectorModule.dll")
        self.rtiConnectorWrapperObject = RtiConnectorWrapper(dictConfigDefs)
        self.rtiConnectorWrapperObject.Create()

    def engine_benchmark(self):
        average_hertz = 0
        hertz_sum = 0
        for value in self.analyzed_data:
            # this is for lines that have default value for "last_detection_processing_time_in_hertz"
            if value['last_detection_processing_time_in_hertz'] != DEFAULT_HERTZ_WHEN_NO_ELAPSED_TIME:
                hertz_sum += value['last_detection_processing_time_in_hertz']
        first_log_time = self.analyzed_data[0]["time"]
        last_log_time = self.analyzed_data[-1]["time"]
        passed_time = last_log_time - first_log_time
        average_hertz = hertz_sum / len(self.analyzed_data)
        print(f"average_hertz: {average_hertz} \nhertz_sum: {hertz_sum} \n"
              f"passed_time_between_first_and_last_log: {passed_time}")

    def csv_file_loader(self):
        # initial dir: This argument sets the initial directory that will be displayed when the file dialog opens
        # title: is for the dialog name
        # filetypes: specifies the file types that will be displayed in the file dialog
        file_path = filedialog.askopenfilename(initialdir=os.path.join(os.getcwd(), "dds_messages_generator/records"),
                                               title="Select CSV file",
                                               filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
        self.file_name = os.path.basename(file_path)
        if file_path:
            output_list = dds_messages_generator.parser_tools.load_scenario(file_path)

            if "benchmark" in self.file_name:
                self.analyzed_data = dds_messages_generator.parser_tools.benchmark_log_parser(output_list)
                self.benchmark_button.config(state=tk.NORMAL)
                self.run_button.config(state=tk.DISABLED)
            elif is_this_a_log_file(output_list):
                self.analyzed_data = dds_messages_generator.parser_tools.optronics_log_parser(output_list)
                self.benchmark_button.config(state=tk.DISABLED)
                self.run_button['state'] = 'normal'
            else:
                self.analyzed_data = dds_messages_generator.parser_tools.optronics_data_parser(output_list)
                self.benchmark_button.config(state=tk.DISABLED)
                self.run_button['state'] = 'normal'

    def update_tank_location(self):
        self.position_output.A_altitude_A_currentPosition = float(self.tank_altitude_entry.get())
        if self.tank_latitude_value_inside.get() == "deg":
            self.position_output.A_latitude_A_currentPosition = np.deg2rad(float(self.tank_latitude_entry.get()))
            self.position_output.A_longitude_A_currentPosition = np.deg2rad(float(self.tank_longitude_entry.get()))
        else:
            self.position_output.A_latitude_A_currentPosition = float(self.tank_latitude_entry.get())
            self.position_output.A_longitude_A_currentPosition = float(self.tank_longitude_entry.get())

    # runs the CSV in a way that simulates the times the messages were sent according to the difference between them
    def run_csv_file(self):
        # when the running is active you cannot load another file
        self.csv_loader_button['state'] = 'disabled'
        self.publish_button['state'] = 'disabled'

        for i, output in enumerate(self.analyzed_data):
            if output['data'].A_moduleId_A_sourceID != 1 or b'TDBOX' in output['data'].A_detectionClassification:
                # filter out mission layer messages
                continue
            if output['data'].A_systemId_A_sourceID == 22:
                self.publish_to_aps(output)
            else:
                self.publish_to_optronics(output)
                self.publish_to_position(output)

            # Check if the scenario should stop
            if not self.scenario_running:
                print('Scenario stopped')
                break  # Exit the loop if scenario should stop
            # Waiting the time until the next detection arrived
            if i < len(self.analyzed_data) - 1:
                time_diff = self.analyzed_data[i + 1]['time'] - output['time']
                time_to_sleep = max(time_diff.total_seconds(), 0)
                time.sleep(time_to_sleep)

        if self.scenario_running:
            print('Finished the scenario')
        self.csv_loader_button['state'] = 'normal'
        self.publish_button['state'] = 'normal'
        self.run_button['state'] = 'normal'
        self.stop_button['state'] = 'disabled'

    def publish_to_aps(self, output):
        topic = "P_Tactical_Sensor_PSM::C_Detection_Aps"
        self.rtiConnectorWrapperObject.Publish(topic, output['data'])

    def publish_to_optronics(self, output):
        topicOptronics = "P_Tactical_Sensor_PSM::C_Detection_Optronics"
        output['data'].A_detectionMethods_IsSet = True
        output['data'].A_numberOfDetectionMethods_IsSet = True
        self.rtiConnectorWrapperObject.Publish(topicOptronics, output['data'])

    def publish_to_position(self, log_output):
        topic = "P_Navigation_PSM::C_Position"
        structType = DictTopicData[topic][DictTopicDataEnum.StructType]
        output = structType()

        output.A_seconds_A_timeOfDataGeneration = log_output['data'].A_seconds_A_timeOfDataGeneration
        output.A_nanoseconds_A_timeOfDataGeneration = log_output['data'].A_nanoseconds_A_timeOfDataGeneration
        output.A_altitude_A_currentPosition = log_output[
            'data'].A_spatialInfo.A_physicalInfo.A_altitude_A_sensorInertialLocation
        output.A_latitude_A_currentPosition = log_output[
            'data'].A_spatialInfo.A_physicalInfo.A_latitude_A_sensorInertialLocation
        output.A_longitude_A_currentPosition = log_output[
            'data'].A_spatialInfo.A_physicalInfo.A_longitude_A_sensorInertialLocation

        self.rtiConnectorWrapperObject.Publish(topic, output)

    def stop_scenario(self):
        self.stop_button['state'] = 'disabled'
        self.run_button['state'] = 'normal'
        self.publish_button['state'] = 'normal'
        self.scenario_running = False  # Set the flag to stop the scenario

    def start_scenario(self):
        if self.scenario_thread is None or not self.scenario_thread.is_alive():
            self.scenario_running = True
            self.scenario_thread = threading.Thread(target=self.run_csv_file)
            print("Scenario started")
            self.scenario_thread.start()
            self.run_button['state'] = 'disable'
            self.stop_button['state'] = 'normal'
        else:
            print("Scenario is already running.")

    def random_number(self):
        msb, lsb = uuid_to_int(new_id())
        self.msb_entry.delete(0, "end")
        self.msb_entry.insert(0, str(msb))
        self.lsb_entry.delete(0, "end")
        self.lsb_entry.insert(0, str(lsb))

    def polar2geo(self):
        if self.elevation_value_inside.get() != "deg":
            platform = (float(self.tank_latitude_entry.get()), float(self.tank_longitude_entry.get()),
                        float(self.tank_altitude_entry.get()))
            target_polar = (float(self.azimuth_entry.get()),
                            float(self.elevation_entry.get()), float(self.range_entry.get()))
            lat, lon, alt = polar_to_gps(platform, target_polar)
            polar_values = [lat, lon, alt]
            entrys = [self.target_latitude_entry, self.target_longitude_entry, self.target_altitude_entry]
            for entry, polar_value in zip(entrys, polar_values):
                entry.delete(0, "end")
                entry.insert(0, str(polar_value))

    def geo2polar(self):
        platform = (float(self.tank_latitude_entry.get()), float(self.tank_longitude_entry.get()),
                    float(self.tank_altitude_entry.get()))
        target_geo = (float(self.target_latitude_entry.get()), float(self.target_longitude_entry.get()),
                      float(self.target_altitude_entry.get()))
        az, el, r = gps_to_polar(platform, target_geo, transformer)
        geo_values = [az, el, r]
        entrys = [self.azimuth_entry, self.elevation_entry, self.range_entry]
        for entry, geo_value in zip(entrys, geo_values):
            entry.delete(0, "end")
            entry.insert(0, str(geo_value))

    def conversion_button_state(self):
        buttons = [self.geo2polar_button, self.polar2geo_button]

        # make sure that the conversion buttons will be available
        if (self.tank_location_available_value_inside.get() == "True" and self.source_id_value_inside.get() != "maanak"
                and self.target_geo_available_value_inside.get() == "True"
                and self.target_polar_available_value_inside.get() == "True"
                and self.azimuth_value_inside.get() == "rad"):

            buttons[0].configure(state="normal")
            buttons[1].configure(state="normal")
        else:
            buttons[0].configure(state="disabled")
            buttons[1].configure(state="disabled")

    # Checks that the same conversion type is not selected twice
    def deg_rad(self, option):
        if (option == "rad" and self.flag) or (option == "deg" and not self.flag):
            self.deg_rad_convert(option)
            self.flag = not self.flag
        # when you select deg the conversion_buttons need to be disabled and normal when you select rad
        self.conversion_button_state()

    # Converts from angle to radian and vice versa
    def deg_rad_convert(self, option):
        convert_func = {"rad": math.radians, "deg": math.degrees}[option]
        # Each entry you convert its value
        entries = [self.tank_latitude_entry, self.tank_longitude_entry, self.elevation_entry,
                   self.azimuth_entry, self.target_latitude_entry, self.target_longitude_entry]
        selected_values = [self.tank_latitude_value_inside, self.tank_longitude_value_inside,
                           self.elevation_value_inside, self.azimuth_value_inside, self.target_latitude_value_inside,
                           self.target_longitude_value_inside]
        disabled_entrys = []
        for entry, selected_value in zip(entries, selected_values):  # zip - allow me to  read from 2 lists
            # changing the disabled entrys state to normal in order to make the conversion
            if entry['state'] == tk.DISABLED:
                disabled_entrys.append(entry)
                entry.configure(state="normal")

            selected_value.set(option)
            value = float(entry.get())
            converted_value = convert_func(value)
            entry.delete(0, "end")  # delete the value inside the entry, so it could set another one instead
            entry.insert(0, str(converted_value))

            # Checks whether there are disabled entrys that changed to normal for the conversion
            if len(disabled_entrys) > 0:
                disabled_entrys.pop(0).configure(state="disable")

    def type_selected(self, type_value):
        type_value_mapping = {
            "DETECTION": 0,
            "THREAT": 1,
            "TARGET": 2
        }
        self.value = type_value_mapping.get(type_value)

    def influenced_by_the_source_id(self, source_id_value):
        self.classifications_based_on_selected_sensor(source_id_value)
        self.range_methods_based_on_selected_sensor(source_id_value)
        self.noga_selected(source_id_value)
        self.types_based_on_selected_sensor(source_id_value)
        self.type_selected(self.type_value_inside.get())
        self.available_fields_when_maanak_is_selected()

    def available_fields_when_maanak_is_selected(self):
        # Define lists of widgets to update
        tank_widgets = [self.tank_location_available_menu, self.tank_altitude_entry, self.tank_latitude_entry,
                        self.tank_longitude_entry, self.tank_latitude_menu, self.tank_longitude_menu]
        target_polar_widgets = [self.target_polar_available_menu, self.elevation_entry, self.azimuth_entry,
                                self.range_entry, self.elevation_menu,
                                self.azimuth_menu]
        target_geo_widgets = [self.target_altitude_entry, self.target_latitude_entry, self.target_longitude_entry,
                              self.target_latitude_menu, self.target_longitude_menu]

        if self.source_id_value_inside.get() in ["maanak", "DH_TACT_SENSOR"]:
            for widget in tank_widgets:
                widget.configure(state=tk.DISABLED)

            for widget in target_polar_widgets:
                widget.configure(state=tk.DISABLED)

            for widget in target_geo_widgets:
                widget.configure(state=tk.NORMAL)
            self.target_geo_available_menu.configure(state=tk.DISABLED)
        else:
            # Enable widgets for other source_id_value
            for widget in tank_widgets + target_polar_widgets + [self.target_geo_available_menu]:
                widget.configure(state=tk.NORMAL)

    def types_based_on_selected_sensor(self, source_id_value):
        type_map = {
            "noga": {"DETECTION": ["DETECTION"]},
            "windcoat": {"DETECTION": ["DETECTION", "THREAT", "TARGET"]},
            "maanak": {"DETECTION": ["DETECTION", "THREAT", "TARGET"]},
            "commander": {"DETECTION": ["DETECTION"]},
            "gunner": {"DETECTION": ["DETECTION"]},
            "loader": {"DETECTION": ["DETECTION"]},
            "DELETED": {"DETECTION": ["DETECTION", "THREAT", "TARGET"]},
            "DH_TACT_SENSOR": {"DETECTION": ["DETECTION"]}
        }

        if source_id_value in type_map:
            types = type_map[source_id_value]  # take the dict base on the id
            # Clear the existing menu items
            self.type_menu['menu'].delete(0, 'end')

            # Populate the menu with new items and update the value
            for key, values in types.items():
                self.type_value_inside.set(key)
                self.value = 0  # Reset the value to 0
                for idx, type_value in enumerate(values):
                    self.type_menu['menu'].add_command(
                        label=type_value,
                        command=lambda value=type_value, idx=idx: self.set_type_value(value, idx))
            return

    def set_type_value(self, type_value, value):
        self.type_value_inside.set(type_value)
        self.value = value

    def classifications_based_on_selected_sensor(self, source_id_value):
        classification_map = {
            "noga": {"Person": ["Person", "Car", "Motorcycle", "Marker"]},
            "windcoat": {"Windcoat": ["Windcoat"]},
            "maanak": {
                "General Enemy": ["General Enemy", "Infantry", "AT", "AFV", "SA", "IFV", "Animal", "Rocket Launcher",
                                  "C2", "ELINT", "Movement"]},
            "commander": {"General Enemy": ["General Enemy", "Infantry", "AT", "AFV", "SA", "IFV", "Target"]},
            "gunner": {"General Enemy": ["General Enemy", "Infantry", "AT", "AFV", "SA", "IFV"]},
            "loader": {"General Enemy": ["General Enemy", "Infantry", "AT", "AFV", "SA", "IFV"]},
            "DELETED": {
                "Person": ["Person", "Car", "Motorcycle", "Marker", "General Enemy", "Infantry", "AT", "AFV", "SA",
                           "IFV", "Windcoat"]},
            "DH_TACT_SENSOR": {"Marker": ["Marker"]},
        }

        if source_id_value in classification_map:
            classifications = classification_map[source_id_value]  # take the dict base on the id
            for key, values in classifications.items():  # key - default value, values - values you want for this id
                self.classification_value_inside.set(key)
                self.classification_menu['menu'].delete(0, 'end')  # deletes the existing menu items
                # populates it with new menu items
                for classification_value in values:
                    self.classification_menu['menu'].add_command(
                        label=classification_value,
                        command=lambda value=classification_value: self.classification_value_inside.set(value))
                break

    def range_methods_based_on_selected_sensor(self, source_id_value):
        range_method_map = {
            "noga": {"no range": ["no range", "calc", "measured"]},
            "windcoat": {"measured": ["measured"]},
            "maanak": {"no range": ["no range"]},
            "commander": {"manual": ["manual"]},
            "gunner": {"manual": ["manual"]},
            "loader": {"manual": ["manual"]},
            "DELETED": {"no range": ["no range", "calc", "measured"]},
            "DH_TACT_SENSOR": {"measured": ["measured"]},
        }

        if source_id_value in range_method_map:
            range_method = range_method_map[source_id_value]  # take the dict based on the id
            for key, values in range_method.items():  # key - default value, values - values you want for this id
                self.range_method_value_inside.set(key)
                self.range_method_menu['menu'].delete(0, 'end')  # deletes the existing menu items
                # populates it with new menu items
                for range_method_value in values:
                    self.range_method_menu['menu'].add_command(
                        label=range_method_value,
                        command=lambda value=range_method_value: self.range_method_value_inside.set(value))
                break

    def noga_selected(self, source_id_value):
        widget_states = {
            "noga": "normal",
            "commander": "disabled",
            "maanak": "disabled",
            "windcoat": "disabled",
            "gunner": "disabled",
            "loader": "disabled",
            "DELETED": "disabled",
            "DH_TACT_SENSOR": "disabled"
        }
        self.noga_status_menu.configure(state=widget_states[source_id_value])
        self.start_sending_noga_status_button.configure(state=widget_states[source_id_value])

    def menu_clicked(self, selected_option):
        # Define a dictionary that maps checkbutton values to entry states
        widgets_states = {
            "True": "normal",
            "False": "disabled",
        }

        # Define lists of widgets to update
        tank_widgets = [self.tank_altitude_entry, self.tank_latitude_entry, self.tank_longitude_entry]
        target_polar_widgets = [self.elevation_entry, self.azimuth_entry, self.range_entry, self.elevation_menu,
                                self.azimuth_menu, self.target_geo_available_menu]
        target_geo_widgets = [self.target_altitude_entry, self.target_latitude_entry, self.target_longitude_entry,
                              self.target_latitude_menu, self.target_longitude_menu, self.target_polar_available_menu]

        # Get the selected values from the check buttons
        tank_location_available = self.tank_location_available_value_inside.get()
        target_polar_available = self.target_polar_available_value_inside.get()
        target_geo_available = self.target_geo_available_value_inside.get()

        # Update the state of the widgets based on the selected values
        for widget in tank_widgets:
            widget.configure(state=widgets_states[tank_location_available])

        for widget in target_polar_widgets:
            widget.configure(state=widgets_states[target_polar_available])

        for widget in target_geo_widgets:
            widget.configure(state=widgets_states[target_geo_available])

        # every time you choose "True" or "False" I want it to also affect the conversion_button_state
        self.conversion_button_state()

    def publish(self):
        if self.source_id_value_inside.get() == "noga":
            dds_messages_generator.topic_publisher.optronics_or_aps(self,
                                                                    "dds_messages_generator/records/for_publish/noga.csv")
        elif self.source_id_value_inside.get() == "maanak":
            dds_messages_generator.topic_publisher.optronics_or_aps(self,
                                                                    "dds_messages_generator/records/for_publish/maanak.csv")
        elif self.source_id_value_inside.get() == "commander":
            dds_messages_generator.topic_publisher.optronics_or_aps(self,
                                                                    "dds_messages_generator/records/for_publish/commander.csv")
        elif self.source_id_value_inside.get() == "gunner":
            dds_messages_generator.topic_publisher.optronics_or_aps(self,
                                                                    "dds_messages_generator/records/for_publish/gunner.csv")
        elif self.source_id_value_inside.get() == "loader":
            dds_messages_generator.topic_publisher.optronics_or_aps(self,
                                                                    "dds_messages_generator/records/for_publish/loader.csv")
        elif self.source_id_value_inside.get() == "windcoat":
            dds_messages_generator.topic_publisher.optronics_or_aps(self,
                                                                    'dds_messages_generator/records/for_publish/windcoat.csv',
                                                                    "P_Tactical_Sensor_PSM::C_Detection_Aps")
        elif self.source_id_value_inside.get() == "DELETED":
            dds_messages_generator.topic_publisher.optronics_or_aps(self,
                                                                    "dds_messages_generator/records/for_publish/deleted.csv")

        elif self.source_id_value_inside.get() == "DH_TACT_SENSOR":
            dds_messages_generator.topic_publisher.optronics_or_aps(self,
                                                                    "dds_messages_generator/records/for_publish/noga.csv")

        # self.random_number()

    # saving the locations of each widget in a file
    def save_widgets(self):
        self.disable_dragging()
        with open("widget_positions.txt", "w") as f:
            count = 0
            not_in_the_name = ['draggable', 'save', 'move', 'root', 'value', 'flag', 'image', 'rti', 'analyzed_data',
                               'scenario', 'file_name', 'position_output', 'thread_needs_to_stop']
            for attribute_name, value in vars(self).items():
                #  checks if any of the items in the not_in_the_name list are present in the attribute_name string.
                #  If none of them are present, the not any() function returns True
                if not any(item in attribute_name for item in not_in_the_name):
                    x = getattr(self, attribute_name).winfo_x()
                    y = getattr(self, attribute_name).winfo_y()
                    f.write(f"{attribute_name}: {x},{y}\n")
                    count += 1

    # for every attribute in the class that start with "draggable", change her dragging attribute value to True
    def enable_dragging(self):
        for attr_name in dir(self):
            if attr_name.startswith("draggable"):
                attr = getattr(self, attr_name)
                attr.dragging = True

    # for every attribute in the class that start with "draggable", change her dragging attribute value to False
    def disable_dragging(self):
        for attr_name in dir(self):
            if attr_name.startswith("draggable"):
                attr = getattr(self, attr_name)
                attr.dragging = False

    def load_widget_positions(self):
        if os.path.isfile("widget_positions.txt"):
            with open("widget_positions.txt", "r") as f:
                for line in f:
                    try:
                        # Separates each line for name and position
                        key, value = line.strip().split(" ")
                        x, y = map(int, value.split(","))
                        # get the widget by key and set its position
                        widget_name = key.split(":")[0]
                        # retrieves the widget object based on the widget name in the key
                        widget = getattr(self, widget_name)
                        widget.place(x=x, y=y)

                    except Exception as e:
                        print(f"Error parsing widget position: {e}")

    def start_position_thread(self):
        self.stop_sending_location_button.configure(state=tk.NORMAL)
        self.start_sending_location_button.configure(state=tk.DISABLED)
        self.is_position_thread_needs_to_stop = False
        thread = threading.Thread(target=dds_messages_generator.topic_publisher.position, args=(self,))
        thread.start()
        if self.is_position_thread_needs_to_stop:
            thread.join()

    def stop_position_thread(self):
        self.start_sending_location_button.configure(state=tk.NORMAL)
        self.stop_sending_location_button.configure(state=tk.DISABLED)
        self.is_position_thread_needs_to_stop = True

    def start_mount_thread(self):
        self.stop_sending_noga_status_button.configure(state=tk.NORMAL)
        self.start_sending_noga_status_button.configure(state=tk.DISABLED)
        self.is_mount_thread_needs_to_stop = False
        thread = threading.Thread(target=dds_messages_generator.topic_publisher.mount, args=(self,))
        thread.start()
        if self.is_mount_thread_needs_to_stop:
            thread.join()

    def stop_mount_thread(self):
        self.start_sending_noga_status_button.configure(state=tk.NORMAL)
        self.stop_sending_noga_status_button.configure(state=tk.DISABLED)
        self.is_mount_thread_needs_to_stop = True

    # stopping the script when you press "q" or "Q" in the keyboard
    def stop_mainloop(self, event):
        if event.char.lower() == "q":
            self.root.quit()

    def run(self):
        self.load_widget_positions()
        self.disable_dragging()
        self.classifications_based_on_selected_sensor("commander")
        self.range_methods_based_on_selected_sensor("commander")
        self.noga_selected("commander")
        self.root.bind("<Key>", self.stop_mainloop)
        self.root.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()
