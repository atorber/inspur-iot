import paho.mqtt.client as mqtt
import sys
import time
import json
import configparser
import uuid
import random

cf = configparser.ConfigParser()
ret = cf.read("./user.conf")

# 判断配置文件是否存在
if len(ret) == 0:
    raise("can not find user.conf file")

#验证配置文件参数是否完整
opts = cf.options("param")
list_mode = ["host", "port", "devicetype", "endpointcode", "productkey", "thingname", "rootca", "cert", "key"]
list_req = [i for i in list_mode if i not in opts]

if list_req:
    logging.error("user.conf missing the following param：")
    logging.error(list_req)
    raise ("user.conf is not complete")
else:
    host = cf.get("param", "host")
    host_port = cf.getint("param", "port")
    deviceType = cf.get("param", "devicetype")
    endpointCode = cf.get("param", "endpointcode")
    productKey = cf.get("param", "productkey")
    thingName = cf.get("param", "thingname")
    rootCAPath = cf.get("param", "rootca")
    certificatePath = cf.get("param", "cert")
    privateKeyPath = cf.get("param", "key")

clientId = endpointCode + "@" + productKey + "@" + thingName
topic='iot/'+endpointCode+'/'+productKey+'/'+thingName+'/shadow/update/accepted'
subtopic='iot/'+endpointCode+'/'+productKey+'/'+thingName+'shadow/update/accepted'

def on_connect(client, userdata, flags, rc):
    print('Connected. Client id is: ' + clientId)
    client.subscribe(topic)
    print('Subscribed to topic: ' + topic)
    print(userdata)

def on_message(client, userdata, msg):
    msg = str(msg.payload, 'utf-8')
    t = time.time()
    localtime = time.asctime(time.localtime(t))
    # print(int(t))  # 秒级时间戳
    # print(int(round(t * 1000)))  # 毫秒级时间戳
    # print('MQTT message received: ' + localtime + '|||' + msg)
    print("get the message:")
    print(json.loads(msg))
    print(int(round(t * 1000)) - json.loads(msg)['t'])
    client.publish(topic, 'Message from Inspur IoT demo')
    print('MQTT message published.')
    if msg == 'exit':
        sys.exit()

client = mqtt.Client(clientId)
client.on_connect = on_connect
client.on_message = on_message
client.tls_set(rootCAPath, certificatePath, privateKeyPath, cert_reqs=mqtt.ssl.CERT_REQUIRED, tls_version=mqtt.ssl.PROTOCOL_TLSv1, ciphers=None)
client.connect(host, host_port, 60)
client.loop_forever()

