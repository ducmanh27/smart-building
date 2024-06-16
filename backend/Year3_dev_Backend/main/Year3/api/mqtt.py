
import paho.mqtt.client as mqtt

# Inheritance class
class Client(mqtt.Client):
    def __init__(self, _topic, _topic_array=[]):
        super().__init__()
        self.__check = False
        self.__topic = _topic
        self._topic_arry = _topic_array
        # self.__logger = Log(__name__)

    def on_connect(self, client, userdata, flags, rc):
        """Called when the broker responds to our connection request"""
        # The connection result
        if rc == 0:
            print("Successfully connect to mqtt")
            self.subscribe(self.__topic)
            print(f"Successfully connect to {self.__topic}")
            for i in self._topic_arry:
                self.subscribe(i)
                print(f"Successfully subscribe to {i}")
        else:
            print("Unsuccessfully connect to mqtt")
    
    def on_connect_fail(self, client, userdata):
        """Called when the client failed to connect to the broker"""
        print("Unsuccessfully connect to mqtt")

    def on_disconnect(self, client, userdata, rc):
        if rc == 0:
            # self.__logger.info("Disconnected to broker")
            pass

    def on_message(self, client, userdata, message):
        """Called when a message has been received on a topic that the client subscribes to"""
        # self.__logger.info("Received message from broker")
        self.__check = True
        self.__msg = message.payload.decode("utf-8")

    def on_publish(self, client, userdata, mid):
        '''Called when publish() function has been used'''
        # self.__logger.info("Published successfully")

    def on_subscribe(self, client, userdata, mid, granted_qos):
        """Publish a message on a topic"""
        # self.__logger.info("Subscribed successfully")
        # print("this is on_subscribe function in class CLIENT")

    def msg_arrive(self):
        if self.__check == True:
            self.__check = False
            return self.__msg
        return None

if __name__=="__main__":
    pass
