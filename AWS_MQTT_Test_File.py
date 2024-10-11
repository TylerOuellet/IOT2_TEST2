from datetime import datetime
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import config
import json
import time
import ADC0832
import RPi.GPIO as GPIO
trig = 20
echo = 21
LED_PIN = 26

#set time
date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
print (f"Timestamp:{date}")
# user specified callback function
def customCallback(client, userdata, message):
    print("Distance Greater than 5 Detected!")
    GPIO.output(LED_PIN,True)
    time.sleep(2)
    GPIO.output(LED_PIN,False)

# configure the MQTT client
myMQTTClient = AWSIoTMQTTClient(config.CLIENT_ID)
myMQTTClient.configureEndpoint(config.AWS_HOST, config.AWS_PORT)
myMQTTClient.configureCredentials(config.AWS_ROOT_CA, config.AWS_PRIVATE_KEY,config.AWS_CLIENT_CERT)
myMQTTClient.configureConnectDisconnectTimeout(config.CONN_DISCONN_TIMEOUT)
myMQTTClient.configureMQTTOperationTimeout(config.MQTT_OPER_TIMEOUT)
#Connect to MQTT Host
if myMQTTClient.connect():
    print('AWS connection succeeded')
# Subscribe to topic
myMQTTClient.subscribe(config.REPUB_TOPIC, 1, customCallback)
time.sleep(2)
# Send message to host
collected_data = {
    "volume" : "INIT",
    "distance" : "INIT"
    }
def send(data):
    payload = json.dumps(collected_data)
    myMQTTClient.publish(config.TOPIC, payload, 1)
def init():
    ADC0832.setup()
    GPIO.setup(trig,GPIO.OUT,initial=GPIO.LOW)
    GPIO.setup(echo,GPIO.IN)
    GPIO.setup(LED_PIN,  GPIO.OUT)

def checkdist():
	GPIO.output(trig, GPIO.HIGH)
	time.sleep(0.000015)
	GPIO.output(trig, GPIO.LOW)
	while not GPIO.input(echo):
		pass
	t1 = time.time()
	while GPIO.input(echo):
		pass
	t2 = time.time()
	return (t2-t1)*340/2

def loop():
    while True:
        res = ADC0832.getADC(0)
        volume = 255 - res
        collected_data["volume"] = volume
        collected_data["distance"] = checkdist()
        json_data = json.dumps(collected_data) 
        print("Collected Data: ", collected_data)
        send(json_data)
        time.sleep(5)
        
if __name__ == '__main__':
    init()
    try:
        loop()
    except KeyboardInterrupt: 
        GPIO.output(LED_PIN,False)
        ADC0832.destroy()
        print('The end!')