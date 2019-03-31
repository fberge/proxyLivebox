from flask import Flask, request
from flask_restful import Resource, Api
import xml.etree.ElementTree as ET
from time import sleep
import requests

serverPort = '5002'
serverIp = '0.0.0.0'
liveboxPort = '8080'
liveboxIp = '0.0.0.0'
		
treeConf = ET.parse('config.xml')
cf = treeConf.getroot().find('configuration')
for child in cf:
	if child.tag.lower() == 'server':
		serverPort = child.attrib['port']
		serverIp = child.attrib['ip']
	if child.tag.lower() == 'livebox':
		liveboxPort = child.attrib['port']
		liveboxIp = child.attrib['ip']

print "Server address  : " + serverIp
print "Server port     : " + serverPort
print "Livebox address : " + liveboxIp
print "Livebox port    : " + liveboxPort
app = Flask(__name__)
api = Api(app)

def getCode(key_id):
	keyId = treeConf.getroot().find('keys')
	for child in keyId:
		if child.attrib['name'].lower() == key_id.lower():
			return child.attrib['code']	
	return "error"
	
def sendCode(key_id, mode):
	keyId = treeConf.getroot().find('keys')
	for child in keyId:
		if child.attrib['name'].lower() == key_id.lower():
			params = {'operation': '01', 'key': child.attrib['code'], 'mode': mode}
			r = requests.get('http://'+liveboxIp+':'+liveboxPort+'/remoteControl/cmd?operation=01&key='+child.attrib['code']+'&mode=0')
			print 'http://'+liveboxIp+':'+liveboxPort+'/remoteControl/cmd'
			return "ok"
	return "error"

class key(Resource):
    def get(self, key_id):
		return sendCode(key_id,'0')
		
				
class channel(Resource):
    def get(self, channel_id):
		channelId = treeConf.getroot().find('channels')
		for child in channelId:
			if child.attrib['name'].lower() == channel_id.lower().replace(' ','').replace('%20',''):
				for action in child:
					sendCode(action.attrib['action'],'0')
					#sleep(0.5)					
				return 'ok'
		return "error"

class macro(Resource):
    def get(self, macro_id, param):
		channelId = treeConf.getroot().find('macros')
		for child in channelId:
			if child.attrib['name'].lower() == macro_id.lower().replace(' ','').replace('%20',''):
				for action in child:
					mode=action.attrib['mode'].lower()
					repeat=action.attrib['repeat'].lower()
					if mode=='param':
						mode=param
					if repeat=='param':
						repeat=int(param)
					if repeat > 1:
						for i in range(repeat):
							sendCode(action.attrib['action'],mode)
					else:
						sendCode(action.attrib['action'],mode)	
				return 'ok'
		return "error"		
        
api.add_resource(key, '/key/<key_id>') # Route_1
api.add_resource(channel, '/channel/<channel_id>') # Route_2
api.add_resource(macro, '/macro/<macro_id>/<param>') # Route_3


if __name__ == '__main__':
     app.run(host=serverIp, port=int(serverPort))
