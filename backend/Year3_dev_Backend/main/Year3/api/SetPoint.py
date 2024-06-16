import paho.mqtt.client as mqtt
import json
import random 
import time 
import calendar
import datetime
import os

class SetPoint():
    mqtt_broker = os.environ.get('BROKER_ADDRESS')
    mqtt_port = int(os.environ.get('BROKER_PORT'))
    topic = "Year3"

    client_id = f'python-mqtt-{random.randint(0,1000)}'
    # client_id = 'clientId-dhhSHVoTBA'
    
    def connect_mqtt(self):
        def on_connect(client, userdata, flag, rc):
            if rc == 0:
                print("Connected to MQTT Brocker!")
              
            else:
                print(f"Failed to connect, return code {rc}")
        
        client = mqtt.Client(self.client_id)
        client.on_connect = on_connect
        client.connect(self.mqtt_broker, self.mqtt_port, 60)
        return client

    def publish(self, client, setPoint):
        date = datetime.datetime.utcnow()
        utc_time = calendar.timegm(date.utctimetuple())

        new_data = {
                        'operator':'sendSetPoint',
                        'infor':{
                            'time':utc_time,
                            "status":setPoint,
                        }
                    }

        time.sleep(2)
        msg = json.dumps(new_data)
        result = client.publish(self.topic, msg)
        status = result[0]
        if status == 0:
            print(f"Succesfully send '{msg}' to topic '{self.topic}' PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP")
        else:
            print(f"Fail to send '{msg}' to topic '{self.topic}' PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP")
            raise Exception(f"Fail to send '{msg}' to topic '{self.topic}' PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP")

    def run(self, setPoint):
        client = self.connect_mqtt()
        client.loop_start()
        try:
            self.publish(client, setPoint)
        except Exception:
            print(str(Exception))
        finally:
            client.disconnect()

