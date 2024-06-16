##
# @brief clone mqtt receiver
#       
#

backend_topic_dictionary = {"get_sensor_data": "farm/monitor/sensor",
                        "get_actuator_data": "farm/monitor/actuator",
                        "get_setpoint": "farm/control",
                        "room_sync_gateway_backend": "farm/sync_room",
                        "set_timer": "farm/set_timer",}

import mqtt 
import time
import json
import config
broker = config.BROKER_ADDRESS
client = mqtt.Client("farm/control")
client.connect(broker, int(config.BROKER_PORT), 60)
client.loop_start()
while(1):
    temp = client.msg_arrive()
    if temp != None:
        print("receive message!")
        data = json.loads(temp)
        print(json.loads(temp))
        if data["operator"] == "set_timer":
            client.publish("farm/control", json.dumps({
                "operator": "air_conditioner_control_ack",
                "info": {
                    "status": 0,
                }
            }))