from django.db import models

# Create your models here.
from django.conf import settings


##
# @brief This table is for Room data, how many rooms are there, including 
#        their id (unique), construction name ("farm" or "building"),
#        their size (length and width) which is used for rendering heatmap.
#
class Room(models.Model):
    id = models.BigAutoField(primary_key=True,db_column="id",)
    room_id = models.IntegerField(null=False, unique=True, db_column="room_id",)   #!< BigAutoField make the field keep increaing value and unique.
    construction_name = models.TextField(db_column="construction_name")
    x_length = models.IntegerField(db_column="x_length")
    y_length = models.IntegerField(db_column="y_length")
    information = models.TextField(null=False, db_column="information")
##
# @brief This table is for storing gateway, for synchronizing time from server to gateway
#
class Gateway(models.Model):
    id = models.BigAutoField(primary_key=True,db_column="id",)
    room_id = models.ForeignKey(Room, 
                                to_field='room_id',
                                verbose_name=("Refering to id of room where this node is implemented"),
                                on_delete=models.CASCADE,
                                null=False, 
                                db_column="room_id",
                                )
    ip = models.TextField(unique = True,null=False, db_column="ip",)
    status = models.TextField(null=False, db_column="status",)
    error = models.TextField(null=False, db_column="error",)
    time = models.BigIntegerField(null=False, db_column="time",)

##
# @brief This table is for storing node data, including how many node are being emplemented,
#        the id of the room where it is being emplemented, and their mac address.
#
class Registration(models.Model):
    id = models.BigAutoField(primary_key=True,db_column="id",)
    room_id = models.ForeignKey(Room, 
                                to_field='room_id',
                                verbose_name=("Refering to id of room where this node is implemented"),
                                on_delete=models.CASCADE,
                                null=False, 
                                db_column="room_id",
                                )
    node_id = models.IntegerField(null=False, db_column="node_id",)
    x_axis = models.IntegerField(null=False, db_column="x_axis",)
    y_axis = models.IntegerField(null=False, db_column="y_axis",)
    function = models.TextField(null=False, db_column="function",)
    mac = models.TextField(null=False, db_column="mac",)
    status = models.TextField(null=False, db_column="status",)
    aim = models.TextField(null = True, db_column="aim",)
    time = models.BigIntegerField(null=False, db_column="time",)



##
# @brief This table is for storing sensor node data.
#
class RawSensorMonitor(models.Model):
    id = models.BigAutoField(primary_key=True,db_column="id",)
    room_id = models.ForeignKey(Room, 
                                to_field='room_id',
                                verbose_name=("Refering to id of room where this node is implemented"),
                                on_delete=models.CASCADE,
                                null=False, 
                                db_column="room_id",
                                )
    node_id = models.IntegerField(null=False, db_column="node_id",)
    co2 = models.SmallIntegerField(null=True,db_column="co2",)
    temp = models.FloatField(null=True, db_column="temp",)
    hum  = models.FloatField(null=True, db_column="hum",)
    light = models.FloatField(null=True, db_column="light",)
    dust = models.FloatField(null=True, db_column="dust",)
    sound = models.FloatField(null=True, db_column="sound",)
    red = models.SmallIntegerField(null=True, db_column="red",)
    green = models.SmallIntegerField(null=True, db_column="green",)
    blue = models.SmallIntegerField(null=True, db_column="blue",)
    tvoc = models.SmallIntegerField(null=True, db_column="tvoc",)
    motion = models.SmallIntegerField(null=True, db_column="motion",)
    time = models.BigIntegerField(null=False, db_column="time",)
    def __str__(self):
        return self.time

class SensorMonitor(models.Model):
    id = models.BigAutoField(primary_key=True,db_column="id",)
    room_id = models.ForeignKey(Room, 
                                to_field='room_id',
                                verbose_name=("Refering to id of room where this node is implemented"),
                                on_delete=models.CASCADE,
                                null=False, 
                                db_column="room_id",
                                )
    node_id = models.IntegerField(null=False, db_column="node_id",)
    co2 = models.SmallIntegerField(null=True,db_column="co2",)
    temp = models.FloatField(null=True, db_column="temp",)
    hum  = models.FloatField(null=True, db_column="hum",)
    light = models.FloatField(null=True, db_column="light",)
    dust = models.FloatField(null=True, db_column="dust",)
    sound = models.FloatField(null=True, db_column="sound",)
    red = models.SmallIntegerField(null=True, db_column="red",)
    green = models.SmallIntegerField(null=True, db_column="green",)
    blue = models.SmallIntegerField(null=True, db_column="blue",)
    tvoc = models.SmallIntegerField(null=True, db_column="tvoc",)
    motion = models.SmallIntegerField(null=True, db_column="motion",)
    time = models.BigIntegerField(null=False, db_column="time",)
    def __str__(self):
        return self.time

class RawActuatorMonitor(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="id")
    room_id = models.ForeignKey(Room, 
                                to_field='room_id',
                                verbose_name=("Refering to id of room where this node is implemented"),
                                on_delete=models.CASCADE,
                                null=False, 
                                db_column="room_id",
                                )
    node_id = models.IntegerField(null=False, db_column="node_id",)
    device_type = models.TextField(null=False, db_column="device_type")
    speed = models.SmallIntegerField(db_column="speed")
    temp = models.SmallIntegerField(db_column="temp")
    time = models.BigIntegerField(db_column="time")
    def __str__(self):
        return self.time
   
class ActuatorMonitor(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="id")
    room_id = models.ForeignKey(Room, 
                                to_field='room_id',
                                verbose_name=("Refering to id of room where this node is implemented"),
                                on_delete=models.CASCADE,
                                null=False, 
                                db_column="room_id",
                                )
    node_id = models.IntegerField(null=False, db_column="node_id",)
    device_type = models.TextField(null=False, db_column="device_type")
    speed = models.SmallIntegerField(db_column="speed")
    temp = models.SmallIntegerField(db_column="temp")
    time = models.BigIntegerField(db_column="time")
    def __str__(self):
        return self.time

class ControlSetpoint(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="id")
    room_id = models.ForeignKey(Room,
                                verbose_name=("Refering to room that this is trying to set value for"),
                                on_delete=models.CASCADE,
                                null=False,     
                                db_column="room_id",                        
                                )
    node_id = models.IntegerField(null=True, db_column="node_id",)
    device_type = models.TextField(null=True, db_column="device_type",)
    power = models.IntegerField(null=True, db_column="power",)      #1=On, 0=Off
    temp = models.IntegerField(null=True, db_column="temp",)
    start_time = models.BigIntegerField(null=True, db_column="start_time")
    end_time = models.BigIntegerField(null=True, db_column="end_time")
    status = models.IntegerField(null=True, db_column="status")     #1=Successful, 0=Unsuccessful
    time = models.BigIntegerField(db_column="time")
    def __str__(self):
        return self.time
    
class SetTimerHistory(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="id")
    room_id = models.ForeignKey(Room,
                                verbose_name=("Refering to room that this is trying to set timer value for"),
                                on_delete=models.CASCADE,
                                null=False,     
                                db_column="room_id",                        
                                )
    time = models.BigIntegerField(db_column="time")
    timer = models.IntegerField(null=False, db_column="timer",)
    temperature = models.IntegerField(null=False, db_column="temperature",)
    status = models.IntegerField(null=False, db_column="status",) #1 or 0

class NodeConfigBuffer(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="id")
    action = models.IntegerField(null=False, db_column="action")
    mac = models.TextField(null=False, db_column="mac")
    room_id = models.IntegerField(null=False, db_column="room_id")
    time = models.BigIntegerField(null=False, db_column="time")
    
    
class AqiRef(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="id")
    aqi = models.IntegerField(null=True, db_column="aqi")
    pm25 = models.IntegerField(null = True, db_column="pm25") #pm2.5
    pm10 = models.IntegerField(null = True, db_column="pm10") #pm10
    o3 = models.IntegerField(null = True, db_column="o3")       
    no2 = models.IntegerField(null = True, db_column="no2")
    so2 = models.IntegerField(null = True, db_column="so2")
    co = models.IntegerField(null = True, db_column="co")
    t = models.IntegerField(null = True, db_column="t") #temperature
    p = models.IntegerField(null = True, db_column="p") #pressure
    h = models.IntegerField(null = True, db_column="h") #humidity
    w = models.IntegerField(null = True, db_column="w") #wind
    time = models.BigIntegerField(null = True, db_column="time")    #time
    dew = models.IntegerField(null = True, db_column="dew")
    wg = models.IntegerField(null = True, db_column="wg")

class EnergyData(models.Model):
    id = models.AutoField(primary_key=True)
    room_id = models.ForeignKey(Room, 
                                to_field='room_id',
                                verbose_name=("Refering to id of room where this node is implemented"),
                                on_delete=models.CASCADE,
                                null=False, 
                                db_column="room_id",
                                )
    node_id = models.IntegerField(null=True, db_column="node_id",)
    voltage = models.FloatField(null=True, db_column="voltage",)
    current = models.FloatField(null=True, db_column="current",)
    active_power = models.FloatField(null=True, db_column="active_power",)
    power_factor = models.FloatField(null=True, db_column="power_factor",)
    frequency = models.FloatField(null=True, db_column="frequency",)
    active_energy = models.FloatField(null=True, db_column="active_energy",)
    time = models.BigIntegerField(db_column="time")


class WeatherData(models.Model):
    id = models.AutoField(primary_key=True)
    lat = models.FloatField()
    lon = models.FloatField()
    timezone = models.CharField(max_length=255)
    timezone_offset = models.IntegerField()
    current_dt = models.BigIntegerField()
    current_sunrise = models.BigIntegerField()
    current_sunset = models.BigIntegerField()
    current_temp = models.FloatField()
    current_feels_like = models.FloatField()
    current_pressure = models.IntegerField()
    current_humidity = models.IntegerField()
    current_dew_point = models.FloatField()
    current_uvi = models.FloatField()
    current_clouds = models.IntegerField()
    current_visibility = models.IntegerField()
    current_wind_speed = models.FloatField()
    current_wind_deg = models.IntegerField()
    current_wind_gust = models.FloatField(null=True, blank=True)
    current_weather = models.JSONField()
    def __str__(self):
        return f"WeatherData - {self.id}, {self.lat}, {self.lon}"
    
    
    
    
    
    


