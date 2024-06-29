import struct
import uuid
from geopy import distance
import numpy as np


def gps_to_polar(sensor, target, transfer):
    lat1, lon1, h1 = sensor
    lat2, lon2, h2 = target

    x1, y1 = transfer.transform(lat1, lon1, radians=True)  # x is easting, y is northing
    x2, y2 = transfer.transform(lat2, lon2, radians=True)
    dx = x2 - x1
    dy = y2 - y1
    dh = h2 - h1

    az = np.arctan2(dx, dy)
    r = np.sqrt(dx ** 2 + dy ** 2 + dh ** 2)
    el = np.arctan2(dh, np.hypot(dx, dy))
    return az, el, r


def polar_to_gps(target, sensor):
    sensor_latitude, sensor_longitude, sensor_altitude = sensor
    target_azimuth, target_elevation, target_range = target
    target_azimuth = np.rad2deg(target_azimuth)
    reference_point = (np.rad2deg(sensor_latitude), np.rad2deg(sensor_longitude), sensor_altitude)
    destination_point = distance.distance(kilometers=target_range / 1000).destination(point=reference_point,
                                                                                      bearing=target_azimuth)
    target_latitude = destination_point.latitude
    target_longitude = destination_point.longitude
    target_altitude = sensor_altitude + (target_range * np.sin(target_elevation))
    return np.deg2rad(target_latitude), np.deg2rad(target_longitude), target_altitude


def new_id():
    return uuid.uuid4()


def uuid_to_int(ID):
    b_uuid = ID.int.to_bytes(16, byteorder='big', signed=False)
    msb, lsb = struct.unpack('>2q', b_uuid)
    return msb, lsb
