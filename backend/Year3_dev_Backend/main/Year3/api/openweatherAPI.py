'''
    This is program to get data from https://openweathermap.org/ insert to database.
'''
import requests
import psycopg2
import json
import time
from datetime import datetime
import os
# Information Database PostgreSQL
db_config = {
    'dbname': 'smartfarm',
    'user': 'year3',
    'password': 'year3',
    'host': 'my-postgres',
    'port': 5432
}



# URL of API OpenWeatherMap version 3.0
api_url = 'https://api.openweathermap.org/data/3.0/onecall'

# Time request
request_interval = 90

while True:
    try: 
        # Request API
        params = {
            'lat': 21.005721,
            'lon': 105.844523,
            'appid': '93e34bbdd21109078a123d27a9f4afe9',
            'units': 'metric',
            'exclude': 'hourly,daily'
        }
        response = requests.get(api_url, params=params)
        data = response.json()
        #print(f"data response: {data}")
        # Conver data JSON to string JSON
        json_string = json.dumps(data, indent=4)

        # Find position of  "minutely" in JSON string
        index = json_string.find('"minutely":')

        if index != -1:
            # String JSON begin from start to "minutely"
            sliced_json = json_string[:index]
        else:
            # If don't find "minutely", using initial string json
            sliced_json = json_string
        '''
            {
            "lat": 21.0067,
            "lon": 105.8401,
            "timezone": "Asia/Bangkok",
            "timezone_offset": 25200,
            "current": {
                "dt": 1697433214,
                "sunrise": 1697410319,
                "sunset": 1697452342,
                "temp": 30.01,
                "feels_like": 30.91,
                "pressure": 1013,
                "humidity": 49,
                "dew_point": 18.13,
                "uvi": 8.82,
                "clouds": 79,
                "visibility": 10000,
                "wind_speed": 2.99,
                "wind_deg": 1,
                "wind_gust": 3.92,
                "weather": [
                    {
                        "id": 803,
                        "main": "Clouds",
                        "description": "broken clouds",
                        "icon": "04d"
                    }
                ]
            }
        '''
        # Print string JSON was sliced
        print(sliced_json)
        # Extract data
        lat = data['lat']
        lon = data['lon']
        timezone = data['timezone']
        timezone_offset = data['timezone_offset']
        current = data['current']

        current_dt = current['dt']
        current_sunrise = current['sunrise']
        current_sunset = current['sunset']
        current_temp = current['temp']
        current_feels_like = current['feels_like']
        current_pressure = current['pressure']
        current_humidity = current['humidity']
        current_dew_point = current['dew_point']
        current_uvi = current['uvi']
        current_clouds = current['clouds']
        current_visibility = current['visibility']
        current_wind_speed = current['wind_speed']
        current_wind_deg = current['wind_deg']
        current_wind_gust = current.get('wind_gust', None)  
        current_weather = current['weather']

        # Convert field current_weather to string JSON
        current_weather_json = json.dumps(current_weather)

        # Connect to database PostgreSQL
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        #  INSERT data in table WeatherData
        sql = """
        INSERT INTO api_weatherdata (lat, lon, timezone, timezone_offset, current_dt, current_sunrise, current_sunset, current_temp, current_feels_like, current_pressure, current_humidity, current_dew_point, current_uvi, current_clouds, current_visibility, current_wind_speed, current_wind_deg, current_wind_gust, current_weather)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        cur.execute(sql, (
            lat, lon, timezone, timezone_offset, current_dt, current_sunrise, current_sunset, current_temp,
            current_feels_like, current_pressure, current_humidity, current_dew_point, current_uvi, current_clouds,
            current_visibility, current_wind_speed, current_wind_deg, current_wind_gust, current_weather_json))
        
        record_id = cur.fetchone()[0]
        conn.commit()
        conn.close()
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{current_time}: INSERT one record have ID {record_id} TO DATABASE: weather.")

    except Exception as e:
        print("Error:", str(e))

    time.sleep(request_interval)