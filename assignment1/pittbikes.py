import argparse
import collections
import csv
import json
import glob
import math
import os
import pandas
import re
import requests
import string
import sys
import time
import xml

class Bike(object):
    def __init__(self, baseURL, station_info, station_status):
        # initialize the instance
        self.baseURL = baseURL
        self.station_info = station_info
        self.station_status = station_status
        pass

    """
    The method total_bikes will compute and return 
    how many bikes are currently available over all stations
    in the entire City Bike Share network.
    """

    def total_bikes(self):
        # return the total number of bikes available

        print(f"[total_bikes] trying to get response from {self.baseURL + self.station_status}")
        response = requests.get(self.baseURL + self.station_status)
        # print(f"{response}")
        data = response.json()
        total_bikes_num = sum(station['num_bikes_available'] for station in data['data']['stations'])
        print(f"{total_bikes_num = }")
        return total_bikes_num


    def total_docks(self):
        response = requests.get(self.baseURL + self.station_status)
        data = response.json()
        total_docks = sum(station['num_docks_available'] for station in data['data']['stations'])
        return total_docks
        # return the total number of docks available


    def percent_avail(self, station_id):
        # return the percentage of available docks
        response = requests.get(self.baseURL + self.station_status)
        data = response.json()
        for station in data['data']['stations']:
            if int(station['station_id']) == station_id:
                total = station['num_bikes_available'] + station['num_docks_available']
                if total > 0:
                    percent = (station['num_docks_available'] / total) * 100
                    return f"{int(percent)}%"
        return ""

    def closest_stations(self, latitude, longitude):
        # return the stations closest to the given coordinates
        response = requests.get(self.baseURL + self.station_info)
        data = response.json()
        distances = {}
        for station in data['data']['stations']:
            dist = self.distance(latitude, longitude, station['lat'], station['lon'])
            distances[station['station_id']] = dist
        closest_stations = sorted(distances, key=distances.get)[:3]
        result = {station_id: next(
            station['name'] for station in data['data']['stations'] if station['station_id'] == station_id) for
                  station_id in closest_stations}
        return result


    def closest_bike(self, latitude, longitude):
        # return the station with available bikes closest to the given coordinates
        response = requests.get(self.baseURL + self.station_info)
        station_data = response.json()
        response = requests.get(self.baseURL + self.station_status)
        status_data = response.json()
        distances = {}
        for station in station_data['data']['stations']:
            for status in status_data['data']['stations']:
                if station['station_id'] == status['station_id'] and status['num_bikes_available'] > 0:
                    dist = self.distance(latitude, longitude, station['lat'], station['lon'])
                    distances[station['station_id']] = dist
        closest_station_id = min(distances, key=distances.get)
        closest_station_name = next(station['name'] for station in station_data['data']['stations'] if
                                    station['station_id'] == closest_station_id)
        return {closest_station_id: closest_station_name}


    def station_bike_avail(self, latitude, longitude):
        # return the station id and available bikes that correspond to the station with the given coordinates
        # 載入車站信息
        response = requests.get(self.baseURL + self.station_info)
        station_data = response.json()
        # 載入車站狀態
        response = requests.get(self.baseURL + self.station_status)
        status_data = response.json()
        # 查找最接近的車站
        result = {int(station_data['station_id']): status_data['bikes_available']}
        closest_station = None
        min_distance = float('inf')
        for station in station_data['data']['stations']:
            dist = self.distance(latitude, longitude, station['lat'], station['lon'])
            if dist < min_distance:
                min_distance = dist
                closest_station = station['station_id']
                # for status in status_data['data']['stations']:
                # if station['station_id'] == closest_station:
                return result
        return result



        # if closest_station is None:
        #     return "this station does not exist."
        #     # 查找並返回最接近車站的自行車數量
        # for status in status_data['data']['stations']:
        #     if status['station_id'] == closest_station:
        #         return {closest_station: status['num_bikes_available']}

        # for station in station_data['data']['stations']:
        #     # check if station has corresponding latitude and longitude
        #     if station['lat']
        #     # print(station['lat'])
        #     # print(latitude)
        #     if station['lat'] == latitude:
        #         # and station['lon'] == longitude:# datatype
        #         station_id = int(station['station_id'])  # change the datatype to int
        #         bikes_available = next(status['num_bikes_available'] for status in status_data['data']['stations'] if
        #                                int(status['station_id']) == station_id)
        #         return {station_id: bikes_available}
        # # return {}
        

    def distance(self, lat1, lon1, lat2, lon2):
        p = 0.017453292519943295
        a = 0.5 - math.cos((lat2-lat1)*p)/2 + math.cos(lat1*p)*math.cos(lat2*p) * (1-math.cos((lon2-lon1)*p)) / 2
        return 12742 * math.asin(math.sqrt(a))


# testing and debugging the Bike class

if __name__ == '__main__':
    instance = Bike('https://db.cs.pitt.edu/courses/cs1656/data', '/station_information.json', '/station_status.json')
    print('------------------total_bikes()-------------------')
    t_bikes = instance.total_bikes()
    print(type(t_bikes))
    print(t_bikes)
    print()

    print('------------------total_docks()-------------------')
    t_docks = instance.total_docks()
    print(type(t_docks))
    print(t_docks)
    print()

    print('-----------------percent_avail()------------------')
    p_avail = instance.percent_avail(342875) # replace with station ID
    print(type(p_avail))
    print(p_avail)
    print()

    print('----------------closest_stations()----------------')
    c_stations = instance.closest_stations(40.444618, -79.954707) # replace with latitude and longitude
    print(type(c_stations))
    print(c_stations)
    print()

    print('-----------------closest_bike()-------------------')
    c_bike = instance.closest_bike(40.478145372014666, -79.95573878288269) # replace with latitude and longitude
    print(type(c_bike))
    print(c_bike)
    print()

    print('---------------station_bike_avail()---------------')
    s_bike_avail = instance.station_bike_avail(4, 7) # replace with exact latitude and longitude of station
    print(type(s_bike_avail))
    print(s_bike_avail)
