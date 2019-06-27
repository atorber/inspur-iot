import paho.mqtt.client as mqtt
import sys
import time
import json
import configparser
import uuid
import random
import threading

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

# 设置clientid和发布/订阅的topic
clientId = endpointCode + "@" + productKey + "@" + thingName #固定格式“项目编码@产品编码@设备编码”
topic='iot/'+endpointCode+'/'+productKey+'/'+thingName+'/shadow/update' #设备影子更新topic
update_accepted='iot/'+endpointCode+'/'+productKey+'/'+thingName+'/shadow/update/accepted' #设备影子更新成功响应topic
update_rejected='iot/'+endpointCode+'/'+productKey+'/'+thingName+'/shadow/update/rejected' #设备影子更新失败响应topic

def on_connect(client, userdata, flags, rc):
    print('Connected. Client id is: ' + clientId)
    client.subscribe(update_accepted)
    client.subscribe(update_rejected)
    print('Subscribed to topic sucess')
    print(userdata)

def on_message(client, userdata, msg):
    msg = str(msg.payload, 'utf-8')
    t = time.time()
    t=int(round(t * 1000))
    print('thread %s is running...' % threading.current_thread().name)
    print("get the message:",json.loads(msg))
    print("delay time:",t - json.loads(msg)['state']['reported']['t'])
    if msg == 'exit':
        sys.exit()

# 消息发布
def pub(client):
        num=0
        while 1:
            num=num+1
            t = time.time()
            t=int(round(t * 1000))
            print('thread %s is running...' % threading.current_thread().name)
            payload = {
    "state":{
        "reported":{
            "memory_usage":50,
            "gateway_version":"1.0.0",
            "cpu_usage":30,
            "system_info":"test",
            "memory_total":2147483647,
            "memory_free":483647,
            "cpu_core_number":2,
            "disk_usage":num,
            "t":t
        }
    }
}
            client.publish(topic, json.dumps(payload))
            print("pub message:")
            print(json.dumps(payload))
            time.sleep(10)
        client.loop_forever()

# 订阅消息   
def sub(client):
    print('thread %s is running...' % threading.current_thread().name)
    client.loop_forever()
        
def main():
        client = mqtt.Client(clientId)
        client.on_connect = on_connect
        client.on_message = on_message

        client.tls_set(rootCAPath, certificatePath, privateKeyPath, cert_reqs=mqtt.ssl.CERT_REQUIRED, tls_version=mqtt.ssl.PROTOCOL_TLSv1, ciphers=None)
        client.connect(host, host_port, 60)
  
        client.subscribe(update_accepted)
        client.subscribe(update_rejected)

        t = threading.Thread(target=sub,args=(client,), name='subThread')
        t2 = threading.Thread(target=pub,args=(client,), name='pubThread')
        t.start()
        t2.start()
        t.join()
        t2.join()
      
if __name__ == '__main__':
    main()




