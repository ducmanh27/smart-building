import json
import paho.mqtt.client as mqtt
import os
def send_json_to_mqtt_server(json_data, broker_address=os.environ.get('BROKER_ADDRESS'), broker_port=os.environ.get('BROKER_PORT'), topic="farm/monitor/alive"):
    print(json_data)
    # Kết nối tới broker MQTT
    client = mqtt.Client()
    client.connect(broker_address, int(broker_port))

    # Gửi chuỗi JSON tới chủ đề MQTT
    client.publish(topic, json_data)

    # Đóng kết nối tới broker MQTT
    client.disconnect()



