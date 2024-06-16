##
# @brief Dummy data to mqtt
#       
#
import mqtt 
import time
import json
import random
broker = "125.212.231.64"
topic = "farm/test"
data = {
    "operator": "room_sync",
    "status": 0,
    "info": 
    {
        "room_id": 2,
        "construction_name": "farm",
        "x_length": 20,
    	"y_length": 20,
        "node_list":
        [
            {
                "node_id": 1,
                "function": "sensor",
                "x_axis": 10,
                "y_axis": 10,
            },
            {
                "node_id": 2,
                "function": "sensor",
                "x_axis": 11,
                "y_axis": 11,
            },
            {
                "node_id": 3,
                "function": "sensor",
                "x_axis": 12,
                "y_axis": 12,
            },
        ]
    }
}
import datetime



client = mqtt.Client(topic)
client.connect(broker, int(1883), 60)
client.loop_start()
while True:
    temp = client.msg_arrive()
    if temp != None:
        print("receive message!")
        print(json.loads(temp))
    random.seed(int((datetime.datetime.now()).timestamp()))
    data1 = { 
    "operator": "data_response", 
    "status": 1, 
    "info": { 
        "room_id": 3, 
        "node_id": random.randint(5,6),
        # "node_id": 7, 
        "co2": random.randint(100,400) + round(random.random(),2), 
        "dust": random.randint(0,50) + round(random.random(),2),
        "temp": random.randint(20,30) + round(random.random(),2), 
        "hum": random.randint(70,80) + round(random.random(),2),
        "time": int((datetime.datetime.now()).timestamp()) + (7*60*60), 
    } 
    } 
    client.publish(topic, json.dumps(data1))
    print("Done sending message")
    time.sleep(20)