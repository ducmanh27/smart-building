from urllib import request
from django.shortcuts import render,redirect
from django import http
from api import models
from api import serializers
from django.http import HttpResponse
from rest_framework import mixins
from rest_framework import generics
from rest_framework import status 
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.response import Response 
from django.http import JsonResponse
import numpy as np
from .SetPoint import SetPoint
from rest_framework import authentication, permissions
from rest_framework_simplejwt import authentication as jwtauthentication
import json
import psycopg2
import multiprocessing
import datetime
import calendar
from api.models import Room, Registration, RawSensorMonitor, RawActuatorMonitor
from api.serializers import RoomSerializer, RegistrationSerializer
from api.serializers import RawSensorMonitorSerializer ,RawActuatorMonitorSerializer, SetTimerHistorySerializer
import pandas as pd
import math
import time

print("Setting views.py")





###############################################################
# @brief: view for sending secondly data for chart on front-
# @paras: 
#        url:  "http://127.0.0.1:8000/api/v1.1/monitor/data?room_id=1&filter=1&node_id={node_id}"
# @return: The json-formatted data that is returned to front-end
#           will have a for like this:
#           {"green":[null,null,null,null,null,null,null,null,null,null,null,null,null,null,null],
#              "hum":[91.0,91.0,91.0,91.0,91.0,91.0,91.0,91.0,91.0,91.0,91.0,91.0,91.0,91.0,91.0],
#              "tvoc":[null,null,null,null,null,null,null,null,null,null,null,null,null,null,null],
#              "sound":[null,null,null,null,null,null,null,null,null,null,null,null,null,null,null],
#              "red":[null,null,null,null,null,null,null,null,null,null,null,null,null,null,null],
#              "light":[null,null,null,null,null,null,null,null,null,null,null,null,null,null,null],
#              "co2":[6666,6666,6666,6666,6666,6666,6666,6666,6666,6666,6666,6666,6666,6666,6666],
#              "blue":[null,null,null,null,null,null,null,null,null,null,null,null,null,null,null],
#              "motion":[null,null,null,null,null,null,null,null,null,null,null,null,null,null,null],
#              "time":[20,20,20,20,20,20,20,20,20,20,20,20,20,20,20],
#              "temp":[32.0,32.0,32.0,32.0,32.0,32.0,32.0,32.0,32.0,32.0,32.0,32.0,32.0,32.0,32.0],
#              "dust":[null,null,null,null,null,null,null,null,null,null,null,null,null,null,null]}
###############################################################
@api_view(["POST", "GET"])
@authentication_classes([jwtauthentication.JWTAuthentication])
@permission_classes([permissions.IsAuthenticated])
def getSensorSecondlyData(request , *args, **kwargs):
    try: 
        room_id = int(request.GET.get("room_id"))   #!< the query parameter is in string form
        filter = int(request.GET.get("filter"))
        node_id = int(request.GET.get("node_id"))
        # print(node_id)
        # print(filter)
        dict_filter = {"1D": 1, "1W": 2, "1M": 3, "6M": 4, "1Y": 5}
        #Notice that: the timestamp in database is the utc timestamp + 7hour
        #Our local time stamp is faster than than the utc timestamp 7 hour
        ctime = int((datetime.datetime.now()).timestamp()) + (7*60*60) #!< convert to our local timestamp
        # print(ctime)
        filter_time = 0 
        if filter == 1:
            filter_time = ctime - ctime%(24*60*60)
        elif filter == 2:
            filter_time = ctime - ctime%(24*60*60) - 24*60*60*7
        elif filter == 3:
            filter_time = ctime - ctime%(24*60*60) - 24*60*60*31
        elif filter == 4:
            filter_time = ctime - ctime%(24*60*60) - 24*60*60*31*6
        elif filter == 5:
            filter_time = ctime - ctime%(24*60*60) - 24*60*60*31*12
        else:
            filter_time = ctime - ctime%(24*60*60) - 24*60*60*31*12
        
        # print(filter_time)
            
        parameter_key_list = ["co2", "temp", "hum", "light", 
                                "dust", "sound", "red", "green", 
                                "blue", "tvoc", "motion", "time"]
        
        #Get all the node_id that is now presented in room
        sensor_node_id_list = [i["node_id"] for i in RegistrationSerializer(models.Registration.objects.filter(room_id=room_id, function="sensor"), many=True).data] #!< have to add many=True
        #Get all 100 record for each node_id and put all in an list
        total_list = []
        if node_id == 0:
            # print(filter_time)
            for each_node_id in sensor_node_id_list:
                if models.RawSensorMonitor.objects.filter(time__gt=filter_time, room_id=room_id, node_id=each_node_id).count() > 0:
                    data = RawSensorMonitorSerializer(models.RawSensorMonitor.objects.filter(time__gt=filter_time, room_id=room_id, node_id=each_node_id).order_by("-time"), many=True).data #!< have to add many=True
                    data.reverse()
                    total_list.append(data)
        else:
            if models.RawSensorMonitor.objects.filter(time__gt=filter_time, room_id=room_id, node_id=node_id).count() > 0:
                data = RawSensorMonitorSerializer(models.RawSensorMonitor.objects.filter(time__gt=filter_time, room_id=room_id, node_id=node_id).order_by("-time"), many=True).data #!< have to add many=True
                data.reverse()
                total_list.append(data) 
            


        if len(total_list) == 0:
            return_data = {}
            for i in parameter_key_list:
                return_data[i] = []
            return Response(return_data, status=status.HTTP_204_NO_CONTENT) 
        #!< Get an average data of each group of records id (ignore the 0 value) and the time of one record (latest) and add them to return data 

        # for i in total_list:
        #     print(len(i))
        # print("////....")
        min_len_of_array_in_total_list = min([len(i) for i in total_list])
        max_len_of_array_in_total_list = max([len(i) for i in total_list])
        # print(min_len_of_array_in_total_list)
        # print(max_len_of_array_in_total_list)
        # total_list = [i[-min_len_of_array_in_total_list:] for i in total_list]
        # for i in total_list:
        #     print(len(i))

        for i in total_list:
            if len(i) < max_len_of_array_in_total_list:
                for j in range(0, max_len_of_array_in_total_list - len(i)):
                    i.insert(0, {k: -1 for k in parameter_key_list})

        # for i in total_list:
        #     print(len(i))

        
        return_data = {}
        buffer = {}
        for i in parameter_key_list:
            return_data[i] = []
            if i != "time":
                buffer[i] = {"value": 0, "number": 0}
            else:
                buffer[i] = []    #!< is used to get the max value of time
        # print(len(total_list[0]))
        for i in range(len(total_list[0])):
            for each_element_in_total_list in total_list:
                for j in  parameter_key_list:
                    if j != "time" and each_element_in_total_list[i][j] >= 0:
                        buffer[j]["value"] = buffer[j]["value"] +  each_element_in_total_list[i][j]
                        buffer[j]["number"] = buffer[j]["number"] +  1
                    elif j == "time" and each_element_in_total_list[i][j] >= 0:
                        buffer[j].append(each_element_in_total_list[i][j])
                    else:
                        continue
            for j in parameter_key_list:
                if j == "time":
                    return_data[j].append(max(buffer[j])) 
                    buffer[j] = []  #!< reset value
                else:
                    if buffer[j]["number"] != 0:
                        return_data[j].append(round(buffer[j]["value"]/(buffer[j]["number"]),2 ))	
                    else:
                        return_data[j].append(0)
                    buffer[j]["value"] = 0
                    buffer[j]["number"] = 0
        return Response(return_data, status=status.HTTP_200_OK)
    except:
        return Response({"Response": "Error on server!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


	  

#___________________________________________________________________end__________________________________________________________________

			
from .djangoClient import insert_to_table_ControlSetpoint
from .djangoClient import send_setpoint_to_mqtt
from .djangoClient import client as setpoint_client            

###############################################################
# @brief: View for get set point value from Frontend, process
#         it, save it in database, and send it to gateway.
# @paras:
#       url: "http://${host}/api/v1.1/control/fans"
#       data:   
#           {
#               'method':'POST',
#                'headers': {
#                    'Content-Type':'application/json',
#                    },
#                "body": {
#                            "option": "manual",
#                            "speed": speed,
#                            "room_id": {room_id},
#                        },
#           }
# @return: 
#       {"Result": "Successful send setpoint"}
###############################################################
@api_view(["POST"])
@authentication_classes([jwtauthentication.JWTAuthentication])
@permission_classes([permissions.IsAuthenticated])
def send_setpoint(request, *arg, **kwargs):
    monitor_data = json.loads(request.body)
    # print(monitor_data)
    # print(request.data)
    try:
        insert_to_table_ControlSetpoint(monitor_data)
        send_setpoint_to_mqtt(setpoint_client, monitor_data)
        return Response({"Result": "Successfully send setpoint!"}, status=status.HTTP_200_OK)
    except:
        return Response({"Result": "Unsuccessfully send setpoint!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  


###############################################################
# @brief: View for set timer for actuator from Frontend, send it to gateway,
#           ,save the record to database.
# @paras:
#       url: "http://${host}/api/room/set_timer?room_id=${room_id}"
#       data:   
#           {
#               'method':'POST',
#                'headers': {
#                    'Content-Type':'application/json',
#                    },
#                "body": {
#                           "timer": [time],
#                        },
#           }
# @return: 
#       {"Result": "Successful set timer"}
###############################################################
from .djangoClient import send_timer_to_gateway, client
@api_view(["POST"])
@authentication_classes([jwtauthentication.JWTAuthentication])
@permission_classes([permissions.IsAuthenticated])
def setTimerActuator(request, *args, **kwargs):
    try:
        room_id = request.GET.get("room_id")
        timer = json.loads(request.body)
        # print(timer)
        result = send_timer_to_gateway(client, {"timer": timer["time"],"temperature": timer["temperature"] ,"room_id": room_id})
        #send data to gateway and wait for return
        new_data = {"room_id": room_id, 
                    "time": int((datetime.datetime.now()).timestamp()) + 7*60*60,
                    "timer": timer["time"],
                    "temperature": timer["temperature"],
                    "status": result,
                    }
        new_data_serializer = SetTimerHistorySerializer(data=new_data)
        if new_data_serializer.is_valid():
            new_data_serializer.save()
            if result == 1:
                return Response({"Response": "Successful"}, status=status.HTTP_200_OK)
            if result == 0:
                return Response({"Response": "Unsuccessfully set timer"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Response": "Can not save record to database"}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        #save to database 
    except:
        return Response({"Response": "Error on server!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    


###############################################################
# @brief: View for send heatmap data to frontend, using kriging 
#         algorithm.
#         the heatmap that is used in frontend has points arranged
#         in the x_axis from left to right and y_axis from top to bot
#         but the points we generate here is from bot to top and left to right
#         so we have to re-arrange them.
# @paras: 
#           url:    "http://127.0.0.1:8000/api/room/kriging?room_id={room_id}"
# @return: 
#       data in json format:
#           {"data":[-11.57,-0.29,9.6,18.04,24.99,30.41,34.37,37.12,39.01,40.45,-12.07,-0.88,8.92,17.25,23.94,
#                   28.85,31.98,33.61,34.21,34.28,-12.46,-1.32,8.5,16.89,23.57,28.14,30.44,30.86,30.1,28.78,-12.91,
#                   ...],
#           "resolutionX":10,
#           "resolutionY":10}
###############################################################







###############################################################
#@brief: This view is for send history chart data to frontend.
#@paras:
#           url: "http://backend_host/api/v1.1/monitor/data/history?room_id=1&time_start=${unixTimestampStart}&time_end=${unixTimestampEnd}&option=${optionChartData}"
#           times_start: unixtimestamp 
#           times_end: unixtimestamp 
#           for example: "http://127.0.0.1:8000/api/v1.1/monitor/data/history?room_id=1&node_id=0&time_start=1694451600&time_end=1694451600&option=day"
#
#@return:
#           data in json format:
#               {"co2":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,...],
#                "temp":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,...],
#                "hum":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,...],
#                "light":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,...],
#                "dust":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,...],
#                "sound":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,...],
#                "red":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,...],
#                "green":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,...],
#                "blue":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,...],
#                "tvoc":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,...],
#                "motion":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,...],
#                "time":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]}
###############################################################
from .processDataChart import getOptionDayData, getOptionMonthData, getOptionYearData
@api_view(["POST", "GET"])
@authentication_classes([jwtauthentication.JWTAuthentication])
@permission_classes([permissions.IsAuthenticated])
def historyChart(request, *args, **kwargs):
    try:
        if("option" in request.GET):
            option = request.GET.get("option")  #!< query parameter inside an URL is a string not a integer
            room_id = request.GET.get("room_id")   #!< query parameter inside an URL is a string not a integer
            node_id = request.GET.get("node_id")   #!< query parameter inside an URL is a string not a integer
            time_start = request.GET.get("time_start")   #!< query parameter inside an URL is a string not a integer
            time_end = request.GET.get("time_end") #!< query parameter inside an URL is a string not a integer
            # print(str(option), int(room_id), int(node_id), int(time_start), int(time_end))
            result_data = None
            if(option == "day"): 
                result_data = getOptionDayData(int(time_start), int(room_id), int(node_id))
                return Response(result_data, status=status.HTTP_200_OK)      
            elif(option == "month"):
                result_data = getOptionMonthData(int(time_start), int(time_end), int(room_id), int(node_id))
                return Response(result_data, status=status.HTTP_200_OK)       
            elif(option == "year"):
                result_data = getOptionYearData(int(time_start), int(time_end), int(room_id), int(node_id))
                return Response(result_data, status=status.HTTP_200_OK)       
            else:
                return Response({"Response": "Option provided is NOT valid"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Response": "Option is not provided"}, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({"Response": "Error on server!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






#######################################################################
#@brief: This view is for get room data for Landing page in
#        frontend.
#@paras:
#           url: "http://127.0.0.1:8000/api/room"
#@return: example:
		 # {
		 #    "farm": [
		 #       {
		 #             "id": 1,
		 #             "construction_name": "farm",
		 #             "x_length": 18,
		 #             "y_length": 8,
		 #             "node_array": [
		 #                {
		 #                   "id": 10,
		 #                   "mac_address": "ZX:CV:BN:MN",
		 #                   "function": "actuator",
		 #                   "room_id": 1
		 #                },
		 #                {
		 #                   "id": 1,
		 #                   "mac_address": "AB:CD:EF:GH",
		 #                   "function": "sensor",
		 #                   "room_id": 1
		 #                }
		 #             ]
		 #       },
		 #       {
		 #             "id": 2,
		 #             "construction_name": "farm",
		 #             "x_length": 18,
		 #             "y_length": 8,
		 #             "node_array": [
		 #                {
		 #                   "id": 100,
		 #                   "mac_address": "PO:IU:YT:RE",
		 #                   "function": "senor",
		 #                   "room_id": 2
		 #                }
		 #             ]
		 #       }
		 #    ],
		 #    "building": []
		 # }
#######################################################################
# @authentication_classes([jwtauthentication.JWTAuthentication])  #!< use JWTAuthentication
# @permission_classes([permissions.IsAuthenticated])              #!< permitted to use APi only if JWT is authenticated
@api_view(["GET"])
@authentication_classes([jwtauthentication.JWTAuthentication])
@permission_classes([permissions.IsAuthenticated])
def getRoomData(request, *args, **kwargs):
    try:
        Room_all_data = Room.objects.all()  #!< get all records in Room table
        RoomSerializer_instance = RoomSerializer(Room_all_data, many=True)   #!< HAVE TO ADD "many=True"
        # RegistrationSerializer_inst
        response_dict = {"farm": [], "building": []}
        for element in RoomSerializer_instance.data:
            if element["construction_name"] == "farm":
                #!v get all node data that is in this room
                node_data_in_room_element = Registration.objects.filter(room_id=element["room_id"], status="sync")
                #!v create one more field "node_array" in this element
                element["node_array"] = RegistrationSerializer(node_data_in_room_element, many=True).data #!< HAVE TO ADD "many=True"
                response_dict["farm"].append(element)
            elif element["construction_name"] == "building":
                #!v get all node data that is in this room
                node_data_in_room_element = Registration.objects.filter(room_id=element["room_id"], status="sync")
                #!v create one more field "node_array" int this element
                element["node_array"] = RegistrationSerializer(node_data_in_room_element, many=True).data #!< HAVE TO ADD "many=True"
                response_dict["building"].append(element)
        return Response(response_dict, status=status.HTTP_200_OK)
    except:
        return Response({"Response": "Error on server!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

   
#######################################################################
# @brief This view is for get data for InformationTag component in 
#        frontend.
#@paras
#           urls: "http://127.0.0.1:8000/api/room/information_tag?room_id=1"
# @return Example:
			   # {
			   #    "time": 1076,
			   #    "co2": [
			   #       12344
			   #    ],
			   #    "temp": [
			   #       34
			   #    ],
			   #    "hum": [
			    #       93
			    #    ],
                # "node_info": {
                #             "sensor": [...],
                #             "actuator": [...]},
                # "room_size": {"x_length": ..., "y_length": ...}
			   # }
#           
#######################################################################
# @authentication_classes([jwtauthentication.JWTAuthentication])  #!< use JWTAuthentication
# @permission_classes([permissions.IsAuthenticated])              #!< permitted to use APi only if JWT is authenticated
@api_view(["GET"])
# @authentication_classes([jwtauthentication.JWTAuthentication])
# @permission_classes([permissions.IsAuthenticated])
def getRoomInformationTag(request, *args, **kwargs):
    try:
        room_id = request.GET["room_id"]
        # print(room_id)
        if RawSensorMonitor.objects.count() != 0:
            # 1.Get all node_id s that belong to this room
            if Registration.objects.filter(room_id=room_id, function="sensor", status="sync", aim = "air_monitor").count() == 0:
                parameter_key_list = {"co2", "temp", "hum", "light", "dust", "sound", "red", "green", "blue", "tvoc", "motion"}
                average_data_to_return = {}
                for i in parameter_key_list:
                    average_data_to_return[i] = -1
                    average_data_to_return["time"] = 0
                return Response(average_data_to_return, status=status.HTTP_200_OK)
            all_node_id_of_this_room_id = Registration.objects.filter(room_id=room_id, function="sensor", status="sync", aim="air_monitor")
            RegistrationSerializer_instance = RegistrationSerializer(all_node_id_of_this_room_id, many=True)   #!< Have to add many=True
            
            all_node_id_of_this_room_id_list = [ i["node_id"] for i in RegistrationSerializer_instance.data]
            # print(all_node_id_of_this_room_id_list)
            # 2.get the latest data for each node_id
            latest_data_of_each_node_id_in_this_room = []
            for each_node_id in all_node_id_of_this_room_id_list:
                if RawSensorMonitor.objects.filter(room_id=room_id, node_id=each_node_id).exists():   #!< if records of this node_id exist ...
                    data_of_this_node_id = RawSensorMonitor.objects.filter(room_id=room_id, node_id=each_node_id).order_by('-time')[0]  #!< get the latest record of this node_id
                    latest_data_of_each_node_id_in_this_room.append(RawSensorMonitorSerializer(data_of_this_node_id).data)
                else:
                    continue
            # 3. get the average data of them
            parameter_key_list = {"co2", "temp", "hum", "light", "dust", "sound", "red", "green", "blue", "tvoc", "motion"}
            average_data_to_return = {}
            # for element in latest_data_of_each_node_id_in_this_room:
            df = pd.DataFrame(latest_data_of_each_node_id_in_this_room)
            df.sort_values(by="time", ascending=False, inplace=True, )
            average_data_to_return["time"] = df.iloc[0]["time"]   #!< get the time of the latest record
            df = df.replace(-1, np.nan)
            average_df = df.mean(numeric_only = True,)   #!< calculate average value of all column existing in dataframe
            for para in parameter_key_list:
                if para in average_df:
                    if para not in average_data_to_return:
                        average_data_to_return[para] = []
                        average_data_to_return[para].append(int(average_df[para]) if str(average_df[para]) != "nan" else -1)
                    else:
                        average_data_to_return[para].append(int(average_df[para]) if str(average_df[para]) != "nan" else -1)
                else:
                    continue
            # 5. Get nodes information
            sensor_node_information_in_this_room_list = RegistrationSerializer(
                            Registration.objects.filter(room_id=room_id, function="sensor", status="sync", aim = "air_monitor"), many=True).data #!< have to add many=True
            actuator_node_information_in_this_room_list = RegistrationSerializer(
                            Registration.objects.filter(room_id=room_id, status="sync"), many=True).data  #!< have to add many=True
            real_actuator_node_information_in_this_room_list = []
            for i in actuator_node_information_in_this_room_list:
                if i["function"] != "sensor":
                    real_actuator_node_information_in_this_room_list.append(i)
            
            average_data_to_return["node_info"] = {"sensor": sensor_node_information_in_this_room_list,
                                                    "actuator": real_actuator_node_information_in_this_room_list}
            # 6. Get room size 
            room_size_data = RoomSerializer(Room.objects.filter(room_id=room_id), many=True).data #!< have to include many=True
            average_data_to_return["room_size"] = {"x_length": room_size_data[0]["x_length"], "y_length": room_size_data[0]["y_length"]}
            # print(average_data_to_return)
            return Response(average_data_to_return, status=status.HTTP_200_OK)
            # data = RawSensorMonitor.objects.order_by('-time')[0]     #!< get the latest record in model according to timeline
            # RawSensorMonitorSerializer_instance = RawSensorMonitorSerializer(data)
            # return Response(RawSensorMonitorSerializer_instance.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No content!"}, status=status.HTTP_204_NO_CONTENT)
    except:
        return Response({"Response": "Error on server!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




##
# @brief: This view calculate the hourly and daily AQIdust pm2.5 base on airnowtech 
#       Goto "https://forum.airnowtech.org/t/the-aqi-equation/169" for more informations
# @params: 
#       urls: "room/AQIdustpm2_5?room_id={room_id}"
# @return:
#       data in json format: 
#       {
#           "hourly": ...,
#           "daily": ...,
#       }
@api_view(["GET"])
# @authentication_classes([jwtauthentication.JWTAuthentication])
# @permission_classes([permissions.IsAuthenticated])
def AQIdustpm2_5(request, *args, **kwargs):
    try:
        room_id = int(request.GET.get("room_id"))
        pm2_5_table = [
            {"conclo": 0.0, "conchi": 12.0, "aqilo": 0, "aqihi": 50,},
            {"conclo": 12.1, "conchi": 35.4, "aqilo": 51, "aqihi": 100,},
            {"conclo": 35.5, "conchi": 55.4, "aqilo": 101, "aqihi": 150,},
            {"conclo": 55.5, "conchi": 150.4, "aqilo": 151, "aqihi": 200,},
            {"conclo": 150.5, "conchi": 250.4, "aqilo": 201, "aqihi": 300,},
            {"conclo": 250.5, "conclo": 500.4, "aqilo": 301, "aqihi": 500,},
        ]
        hourly = 0
        daily = 0
        ctime = int((datetime.datetime.now()).timestamp()) + (7*60*60) #!< convert to our local timestamp
        # print(ctime)
        #calculate hourly data
        latest_time = int(RawSensorMonitor.objects.order_by("-time")[0].time)
        # print(latest_time)
        # print("____________________________________________________________")
        filter_time = latest_time - 12*60*60
        node_sensor_list = RegistrationSerializer(Registration.objects.filter(room_id=room_id, status="sync"),many=True)
        hourly_dust_data = RawSensorMonitorSerializer(RawSensorMonitor.objects.filter(room_id=room_id, time__gt=filter_time, dust__gt=0), many=True).data #!< have to add many=True
        if len(hourly_dust_data) != 0:
            df = pd.DataFrame(hourly_dust_data)
            df = df[["time", "id", "dust"]]
            df['datetime'] = pd.to_datetime(df['time'], unit='s')
            df["hour"] = df["datetime"].dt.hour
            df = df.groupby(['hour'], as_index=False).mean()
            df.sort_values(by='hour', ascending=False, inplace=True)
            # print(df)
            power_index = 0
            pre_row = None
            l = []
            first_record_flag = True
            for index, row in df.iterrows():
                if first_record_flag:
                    pre_row = row["hour"]
                    l.append({"value": row["dust"], "pow": power_index})
                    first_record_flag = False
                else:
                    dif = pre_row - row["hour"]
                    pre_row = row["hour"]
                    power_index = int(power_index + dif)
                    l.append({"value": row["dust"], "pow": power_index})

            # print(l)
            temp_list = [i["value"] for i in l]
            range = round(max(temp_list) - min(temp_list),1)
            scaled_rate_of_change = range/max(temp_list)
            weight_factor = 1 - scaled_rate_of_change
            weight_factor = 0.5 if weight_factor < 0.5 else round(weight_factor, 1)
            sum = 0
            sum_of_power = 0
            
            for i in l:
                sum = sum + i["value"]*pow(weight_factor, i["pow"])
                sum_of_power = sum_of_power + pow(weight_factor, i["pow"])
                
            hourly = round(sum/sum_of_power, 1)
            conclo = None
            conchi = None
            aqilo = None
            aqihi = None
            for i in pm2_5_table:
                if round(hourly) > 500:
                    hourly = 500
                    break
                if round(hourly) <= i["conchi"] and round(hourly) >= i["conclo"]:        
                    conclo = i["conclo"]
                    conchi = i["conchi"]
                    aqilo = i["aqilo"]
                    aqihi = i["aqihi"]
                    hourly = round((aqihi - aqilo)*(hourly-conclo)/(conchi-conclo) + aqilo)
                    break
            # print(hourly)
            return Response({"hourly": hourly, "daily": 0, "time": latest_time}, status=200)
        else:
            return Response({"Response": "No data available!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except:
        return Response({"Response": "Error on server!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




##
# @brief: This view is for fetching all data of room for room table in configuration page
#
# @params: 
#       urls: "api/configuration/room/all"
# @return:
#   if there is any data:
#       [
#     {
#         "id": 1,
#         "room_id": 1,
#         "construction_name": "building",
#         "x_length": 18,
#         "y_length": 18,
#         "information": "C1B 401"
#     }
#   ]
#      if there is none:
#       []
@api_view(["GET"])
@authentication_classes([jwtauthentication.JWTAuthentication])  #!< use JWTAuthentication
@permission_classes([permissions.IsAuthenticated])              #!< permitted to use APi only if JWT is authenticated
def getConfigurationRoomAll(request, *args, **kwargs):
    try:
        if Room.objects.count() > 0:
            all_room_data = RoomSerializer(Room.objects.all(), many=True).data  #!< have to add many=True
            return Response(all_room_data, status=status.HTTP_200_OK)
        else:
            return Response([], status=status.HTTP_200_OK) 
    except:
        return Response({"Response": "Error on server!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


##
# @brief: This view is for creating new room record, deleting room record or configuring record
#         Notice: if you use postman to test create, the data in JSON form should be exactly like this
#            {
#                 "room_id": "2",
#                 "construction_name": "building",
#                 "x_length": "12",
#                 "y_length": "25",
#                 "information": "TETIONSG"
#             }
#
# @params: 
#       urls: "api/configuration/room/command"
#       - method = "POST":
#               body (data in JSON format): {
#                 "room_id": "2",
#                 "construction_name": "building",
#                 "x_length": "12",
#                 "y_length": "25",
#                 "information": "TETIONSG"
#             } 
#       - method = "DELETE":
#               body (data in JSON format): {"id": ...}
#       - method = "PUT":
#               body (data in JSON format): {
#                 "room_id": "2",
#                 "construction_name": "building",
#                 "x_length": "12",
#                 "y_length": "25",
#                 "information": "TETIONSG"
#             } 
# @return:
#   data in JSON format {"Response": ...} + status 
@api_view(["POST", "DELETE", "PUT"])
@authentication_classes([jwtauthentication.JWTAuthentication])  #!< use JWTAuthentication
@permission_classes([permissions.IsAuthenticated])              #!< permitted to use APi only if JWT is authenticated
def configurationRoom(request, *args, **kwargs):
    try:
        if request.method == "POST":
            new_room = json.loads(request.body)

            # print(f"new room data {new_room}")
            # print(">???????????????????,,,,,,,,")
            if Room.objects.filter(room_id=new_room["room_id"]).count() > 0:
                return Response({"Response": "This room already existed!"}, status=status.HTTP_400_BAD_REQUEST)

            new_data_serializer = RoomSerializer(data=new_room)
            if new_data_serializer.is_valid():
                new_data_serializer.save()
                # print("Successfully save new room to database!")
                return Response({"Response": "Successfully create new room!"}, status=status.HTTP_200_OK)
            else:
                # print("Failed to save new room to database!")
                return Response({"Response": "Failed to create new room!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif request.method == "DELETE":
            id = json.loads(request.body)["id"]
            record = Room.objects.filter(id=id)[0]
            # print(record)
            try:
                record.delete()
                return Response({"Response": "Successfully delete room!"}, status=status.HTTP_200_OK)
            except:
                # print("Failed to delete room!")
                return Response({"Response": "Failed to delete room!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif request.method == "PUT":
            new_setting = json.loads(request.body)
            record = Room.objects.filter(id=new_setting["id"])[0]
            record.construction_name = new_setting["construction_name"]
            record.x_length = new_setting["x_length"]
            record.y_length = new_setting["y_length"]
            record.information = new_setting["information"]
            try:
                record.save()
            except:
                return Response({"Response": "Can not update new room data!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({"Response": "Successfully update new room data"}, status=status.HTTP_200_OK)
    except:
        return Response({"Response": "Error on server!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
##
# @brief: This view is for creating new room node, deleting node record or configuring record
#         
#
# @params: 
#       urls: "api/configuration/node/command"
#       - method = "GET":
#               query parameter: room_id={room_id}
#       - method = "POST":
#               body (data in JSON format): {
#                 "room_id": ...,
#                 "node_id": ...,
#                 "x_axis": ...,
#                 "y_axis": ...,
#                 "function": "sensor"/"fan"/"air"
#                 "mac": ....,
#             } 
#       - method = "DELETE":
#               body (data in JSON format): {"id": ...}
#       - method = "PUT":
#               body (data in JSON format): {
#                 "room_id": ...,
#                 "node_id": ...,
#                 "x_axis": ...,
#                 "y_axis": ...,
#                 "function": "sensor"/"actuator"/"air"
#                 "mac": ....,
#             } 
# @return:
#       - method = "GET":
#               all sensor data in json format filtered by room_id given
#       - all other method:
#               data in JSON format {"Response": ...} + status 
from .djangoClient import sendNodeConfigToGateway, client
from threading import Thread
from .models import NodeConfigBuffer
from .serializers import NodeConfigBufferSerializer

@api_view(["GET", "POST", "DELETE", "PUT"])
@authentication_classes([jwtauthentication.JWTAuthentication])  #!< use JWTAuthentication
@permission_classes([permissions.IsAuthenticated])              #!< permitted to use APi only if JWT is authenticated
def configurationNode(request, *args, **kwargs):
    try:
        if request.method == "GET":
            room_id = int(request.GET.get("room_id"))
            # print(room_id)
            data = Registration.objects.filter(room_id=room_id)
            data_serializer = RegistrationSerializer(data, many=True) #!< have to add many=True
            return Response(data_serializer.data, status=status.HTTP_200_OK)
        if request.method == "POST":
            new_data = json.loads(request.body)
            new_data_for_buffer = {
                "action": 1,
                "mac": new_data["mac"],
                "room_id": new_data["room_id"],
                "time": int((datetime.datetime.now()).timestamp()) + 7*60*60,
            }
            
            new_data["time"] = new_data_for_buffer["time"]  #both record in buffer and registration will have the same time data
            new_data["status"] = "sync"
            
            new_data_serializer = RegistrationSerializer(data=new_data)
            new_data_buffer_serialier = NodeConfigBufferSerializer(data=new_data_for_buffer)
            if new_data_serializer.is_valid():
                new_data_serializer.save()
                if new_data_buffer_serialier.is_valid():
                    new_data_buffer_serialier.save()
                    # print("OK set data post node to buffer")
                # sendNodeConfigToGateway(client, new_data, "add")
                #this thread will run side by side with django main thread 
                t = Thread(target=sendNodeConfigToGateway, args=(client, new_data, "add"))
                t.start()
                return Response({"Response": "Successfully save new node record!"}, status=status.HTTP_200_OK)
            else:
                return Response({"Response": "Unsuccessfully save new node record!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if request.method == "DELETE":
            try:
                new_data = json.loads(request.body)
                id = new_data["id"]
                # print(id)
                record = Registration.objects.filter(id=id)[0]
                record.status = "deleted"
                record.save()
                # print(record)
                new_data_for_buffer = {
                    "action": 0,
                    "mac": str(record.mac),
                    "room_id": str(record.room_id.room_id),         #record.room_id will result in "Room Object"
                    "time": int((datetime.datetime.now()).timestamp()) + 7*60*60,
                }
                # print(new_data_for_buffer)
                # print("OK")
                new_data_buffer_serialier = NodeConfigBufferSerializer(data=new_data_for_buffer)
                if new_data_buffer_serialier.is_valid():
                    # print("????????????????????????")
                    new_data_buffer_serialier.save()
                    # print("OK set data delete node to buffer")
                    t = Thread(target=sendNodeConfigToGateway, args=(client, new_data, "delete"))
                    t.start()
                    return Response({"Response": "Successfully delete node!"}, status=status.HTTP_200_OK)
                else:
                    return Response({"Response": "Unsuccessfully save new node record!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  
            except:
                return Response({"Response": "Unsuccessfully delete node!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if request.method == "PUT":
            new_node_data = json.loads(request.body)
            # print(new_node_data)
            record = Registration.objects.filter(id=new_node_data["id"])[0]
            record.node_id = new_node_data["node_id"]   #!< each column in a record is like a property of calss object, record is not like dictionary
            record.x_axis = new_node_data["x_axis"]
            record.y_axis = new_node_data["y_axis"]
            record.function = new_node_data["function"]

            try:
                record.save()
                return Response({"Response": "Successfully update node!"}, status=status.HTTP_200_OK)
            except:
                return Response({"Response": "Unsuccessfully update node!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   
    except:
        return Response({"Response": "Error on server!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




##
# @brief: This view is for sign up new user
#         
#
# @params: 
#       urls: "api/signup"
#       - method = "GET":
#               query parameter: room_id={room_id}
#       - method = "POST":
#               body (data in JSON format): {
#                 "room_id": ...,
#                 "node_id": ...,
#                 "x_axis": ...,
#                 "y_axis": ...,
#                 "function": "sensor"/"actuator"
#             } 
#       - method = "DELETE":
#               body (data in JSON format): {"id": ...}
#       - method = "PUT":
#               body (data in JSON format): {
#                 "room_id": ...,
#                 "node_id": ...,
#                 "x_axis": ...,
#                 "y_axis": ...,
#                 "function": "sensor"/"actuator"
#             } 
# @return:
#       - method = "GET":
#               all sensor data in json format filtered by room_id given
#       - all other method:
#               data in JSON format {"Response": ...} + status
from django.contrib.auth.models import User
from .serializers import UserSerializer
@api_view(["GET", "POST"])
def signUp(request, *args, **kwargs):
    if request.method == "POST":
        new_user_data = json.loads(request.body)
        data = User.objects.all()
        for i in data:
            # print(i.get_username())
            if new_user_data["username"] == i.get_username():
                return Response({"Response": "Username've already existed!"}, status=status.HTTP_417_EXPECTATION_FAILED)
        new_user = User.objects.create_user(username=new_user_data["username"], password=new_user_data["password"])
        try:
            new_user.save()
            return Response({"Response": "Successfully create user!"}, status=status.HTTP_200_OK)
        except:
            return Response({"Response": "Unsuccessfully create user!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
    else:
        return Response({"Response": "Request method not allowed!"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    


##
# @brief: This view is for fetching the latest data status of the actuator to see if it is on or off
#
# @params: 
#       urls: "/api/actuator_status?room_id=1&node_id=9"

@api_view(["GET"])
# @authentication_classes([jwtauthentication.JWTAuthentication])  #!< use JWTAuthentication
# @permission_classes([permissions.IsAuthenticated])              #!< permitted to use APi only if JWT is authenticated
def getActuatorStatus(request, *args, **kwargs):
    # print(request)
    room_id = request.GET.get("room_id")
    node_id = request.GET.get("node_id")
    print(f"Get actuator status in room id: {room_id} node id: {node_id}")
    if Registration.objects.filter(room_id=room_id, node_id=node_id, status="sync").count() == 0:
        return Response({"Response": "Actuator not available"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    actuator_node = RegistrationSerializer(Registration.objects.filter(room_id=room_id, node_id=node_id, status="sync"), many=True).data
    data_actuator_node = actuator_node[0]
    if RawActuatorMonitor.objects.filter(node_id=data_actuator_node["node_id"], room_id=data_actuator_node["room_id"]).count() == 0:
        print("No actuator status data")
        return Response({"Response": "No actutor status data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    status_record = RawActuatorMonitorSerializer(RawActuatorMonitor.objects.filter(node_id=data_actuator_node["node_id"], room_id=data_actuator_node["room_id"]).order_by("-time").first()).data
    print(f"actuator status {status_record}")
    return Response({"Response": status_record}, status=status.HTTP_200_OK) 


##
# @brief: This view is for frontend to send turn on or off command to actuator
#
# @params: 
#       urls: ""http://127.0.0.1:8000/api/actuator_command""
# @return:
#  
#      if there is none:
#       []
from .djangoClient import send_actuator_command_to_gateway, client
from .serializers import ControlSetpointSerializer
@api_view(["POST"])
# @authentication_classes([jwtauthentication.JWTAuthentication])  #!< use JWTAuthentication
# @permission_classes([permissions.IsAuthenticated])              #!< permitted to use API only if JWT is authenticated
def setActuator(request, *args, **kwargs):
    try:
        data_command = json.loads(request.body)
        print(f"Data command from user: {data_command}")
        data = send_actuator_command_to_gateway(client, data_command)
        """_summary_
           send_actuator_command_to_gateway will return this 
                    new_data = { 
                        "operator": "air_conditioner_control", 
                        "status": 1, 
                        "info": { 
                            "room_id": data["room_id"], 
                            "node_id": data["node_id"], 
                            "device_type": str(device_type), 
                            "power": data["power"],         #1=On, 0=Off
                            "temp": data["temp"], 
                            "start_time": data["start_time"],
                            "end_time": data["end_time"],
                            "time": date,
                            "result": ... 0 or 1, 
                            },
                        } 
        """
        new_data = data["info"]
        print(f"Actuator command {new_data}")

        new_data_serializer = ControlSetpointSerializer(data=new_data)
        if new_data_serializer.is_valid():
            new_data_serializer.save()
        return Response({"Response": 1}, status=status.HTTP_200_OK)    
    except:
        return Response({"Response": 0}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   
    

##
# @brief: This view is for sending AqiRef to Frontend, component AqiRef
#
# @params: 
#       urls: "api/aqi_ref"
# @return:
#  
#      if there is none:
#       []
from api.models import AqiRef
from api.serializers import AqiRefSerializer
@api_view(["GET"])
# @authentication_classes([jwtauthentication.JWTAuthentication])  #!< use JWTAuthentication
# @permission_classes([permissions.IsAuthenticated])              #!< permitted to use APi only if JWT is authenticated
def getAqiRef(request, *args, **kwargs):
    try:
        if AqiRef.objects.count() == 0:
            return Response({"Response": "No data"}, status=status.HTTP_204_NO_CONTENT)
        else:
            latest_data_in_database = AqiRefSerializer(
                AqiRef.objects.order_by("-time"),
                many = True                                     #!< have to add many = True
                                ).data[0]
            return Response({"Response": latest_data_in_database}, status = status.HTTP_200_OK)
            
    except:
        return Response({"Response": 0}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




#DELETE superuser
# > python manage.py shell
# $ from django.contrib.auth.models import User
# $ User.objects.get(username="name", is_superuser=True).delete()

#overider TokenObtainPariView
    """_summary_
    This is for seting up django to alow us take the status of user out of database and wrap it up into reponse return by token API.
    So the json data that returned by token API will contain access token, refresh token and status of user (is supper user or not).
    """
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer
class CustomTokeObtainPairview(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# API for real-time weather data

from api.models import WeatherData
from api.serializers import WeatherDataSerializer
@api_view(["GET"])
# @authentication_classes([jwtauthentication.JWTAuthentication])  #!< use JWTAuthentication
# @permission_classes([permissions.IsAuthenticated])              #!< permitted to use APi only if JWT is authenticated
def getWeatherdata(request, *args, **kwargs):
    try:
        if WeatherData.objects.count() == 0:
            return Response({"Response": "No data"}, status=status.HTTP_204_NO_CONTENT)
        else:
            new_data = WeatherDataSerializer(
                WeatherData.objects.order_by("-id"), many=True
            ).data
            return Response({"Response": new_data[0]}, status=status.HTTP_200_OK)
 
    except:
        return Response({"Response": 0}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# API for real-time electric data
from .models import EnergyData
from .serializers import EnergyDataSerializer
class EnergyDataAPIView(generics.RetrieveAPIView,generics.ListAPIView):

    queryset = EnergyData.objects.all()
    serializer_class = EnergyDataSerializer
    # lookup_field = 'pk'

    def get_object(self, request):
        room_id = request.GET.get("room_id")
        queryset = self.filter_queryset(self.get_queryset())
        obj = models.EnergyData.objects.filter(room_id = room_id).order_by('-time').first()
        return obj
    def retrieve(self, request, *args, **kwargs):

        instance = self.get_object(request)
        serializer = self.get_serializer(instance)
        print(serializer.data)
        data_array = [value for key, value in serializer.data.items() if key != 'id' and key != 'room_id']
        return Response(data_array)
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
 
# API for energy consumption in each month
class EnergyDataChartAPIView(generics.ListAPIView):

    queryset = EnergyData.objects.all()
    serializer_class = EnergyDataSerializer
    year = 2024
    offset_energy = 17.02
    # lookup_field = 'pk'
    def end_of_month_unixtimestamp(self, year, month):
        if month == 12:
            next_month = 1
            next_year = year + 1
        else:
            next_month = month + 1
            next_year = year
        first_day_of_next_month = datetime.datetime(next_year, next_month, 1)
        end_of_month = first_day_of_next_month - datetime.timedelta(seconds=1)
        return int(end_of_month.timestamp() - 7 * 60 * 60)
    
    def filter_queryset(self, queryset):

        dataFirstObj = self.get_serializer(queryset.first(), many=False)
        month_start = datetime.datetime.fromtimestamp(dataFirstObj.data['time']).month
        dataLastObj = self.get_serializer(queryset.last(), many=False)

        month_end = datetime.datetime.fromtimestamp(dataLastObj.data['time']).month
        data_return = []
        for month in range(month_start, month_end+1):
            obj = queryset.filter(time__lte=self.end_of_month_unixtimestamp(self.year, month)).order_by('-time').first()
            data_return.append(obj)
        return data_return
    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        month_year_list = []
        active_power_list = []
        time_activeEnergy_List = []
        for item in serializer.data:  
            month_year_list.append(f"{datetime.datetime.fromtimestamp(item['time']).month}_{datetime.datetime.fromtimestamp(item['time']).year}")
            active_power_list.append(item['active_energy'])

        active_power_list[0] -= self.offset_energy
        energy_consumption_in_month = [active_power_list[0]]
        for i in range(1, len(active_power_list)):
            if i == 1:
                adjusted_value = active_power_list[i] - active_power_list[i - 1]
            else:
                adjusted_value = active_power_list[i] - (active_power_list[i - 1] - active_power_list[i - 2])
            energy_consumption_in_month.append(adjusted_value)
        time_activeEnergy_List.append(month_year_list)
        time_activeEnergy_List.append(energy_consumption_in_month)
        return Response(time_activeEnergy_List)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
# API for heatmap
from .models import Room
class HeatMapData(generics.ListAPIView):

    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer
    # list node which monitoring air
    def filter_queryset(self, queryset, room_id):
        return queryset.filter(room_id=room_id, status = 'sync', aim = 'air_monitor')
    def list(self, request, *args, **kwargs):
        room_id = request.GET.get("room_id")
        queryset = self.filter_queryset(self.get_queryset(), room_id)

        serializer = self.get_serializer(queryset, many=True)
        room_record = Room.objects.all().filter(room_id = room_id).first()
        room_obj = RoomSerializer(room_record, many = False)
        HeatMapData = []
        area = [room_obj.data['x_length'], room_obj.data['y_length']]
        node_id = []
        node_type = []
        x_axis = []
        y_axis = []
        temp = []
        
        timeQueryUpper = int(datetime.datetime.now().timestamp())
        timeQueryLower = timeQueryUpper - 2*60

        for record in serializer.data:
            lastest_record = RawSensorMonitor.objects.all().filter(room_id = room_id, node_id = record['node_id']).last()
            lastest_record_data = RawSensorMonitorSerializer(lastest_record, many = False)
            node_id.append(record['node_id'])
            node_type.append(record['function'])
            x_axis.append(record['x_axis'])
            y_axis.append(record['y_axis'])
            temp.append(lastest_record_data.data['temp'])
        HeatMapData.append(area)
        HeatMapData.append(node_id)
        HeatMapData.append(node_type)
        HeatMapData.append(x_axis)
        HeatMapData.append(y_axis)
        HeatMapData.append(temp)
        return Response(HeatMapData)
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)