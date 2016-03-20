import os
import sys
import datetime
import socket
import struct
import threading
import fcntl
import time
import json
import logging
try:
	import re2 as re
except ImportError:
	import re

import bottle
from bottle import route, run

MYPORT = 9131
MYGROUP_4 = '239.255.250.250'

NIC = os.environ.get('DDDP_CLIENT_NIC', 'wlan0')

if '--debug' in sys.argv[1:] or 'SERVER_DEBUG' in os.environ:
	# Debug mode will enable more verbose output in the console window.
	# It must be set at the beginning of the script.
	import bottle
	bottle.debug(True)

registered_devices = {}
log = logging.getLogger()

TEST = b'AMXB<-UUID=GC100_000000000000_GCTestElement><-SDKClass=Utility><-Make=GlobalCache><-Model=GC-100-12><-Revision=1.0.0><Config-Name=GC-100><Config-URL=http://0.0.0.0>\r'

class DiscoveryBeaconRegistration(dict):
	REGEX = 'AMXB(?:<-UUID\=(?P<UUID>([^>]*))>)(?:<-SDKClass\=(?P<SDKClass>([^>]*))>)(?:<-Make\=(?P<Make>([^>]*))>)(?:<-Model\=(?P<Model>([^>]*))>)(?:<-Revision\=(?P<Revision>([^>]*))>)(?:<Config-Name\=(?P<ConfigName>([^>]*))>)?(?:<Config-URL\=(?P<ConfigURL>([^>]*))>)?\\r'

	def __init__(self, _UUID, _make, _model, _revision, _configName, _url):
		self['UUID'] = _UUID
		self['make'] = _make
		self['model'] = _model
		self['revision'] = _revision
		self['config_name'] = _configName
		self['config_url'] = _url
		self['last_updated'] = datetime.datetime.now().isoformat()

	@staticmethod
	def parseBeaconData(beaconData):
		result = re.match(DiscoveryBeaconRegistration.REGEX, beaconData.decode("utf-8"))
		log.debug(str(result))
		log.debug(result.group('UUID'))
		log.debug(result.group('Make'))
		log.debug(result.group('Model'))
		log.debug(result.group('Revision'))
		log.debug(result.group('ConfigName'))
		log.debug(result.group('ConfigURL'))

		reg = DiscoveryBeaconRegistration (result.group('UUID'), result.group('Make'), result.group('Model'), result.group('Revision'), result.group('ConfigName'), result.group('ConfigURL'))
		return reg

registered_devices = {}

def get_ip_address( NICname ):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', NICname[:15].encode("UTF-8")))[20:24])

def DiscoveredBeaconsPrinter():
	print('Will write out registrations ever five(5) seconds')
	while True:
		time.sleep(5)
		for key in registered_devices:
			log.info(key, 'value = ', registered_devices[key])

def DiscoveryBeaconRegistrationListener():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	
	s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32) 
	s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)	

	s.bind(('', MYPORT))

	host = get_ip_address(NIC)
	log.info(host)
	s.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
	s.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(MYGROUP_4) + socket.inet_aton(host))

	print('Starting to listen...')
	while True:
		try:
			data, addr=s.recvfrom(256)
			log.info('Got data: ', data)
			d = DiscoveryBeaconRegistration.parseBeaconData(data)
			registered_devices[d['UUID']] = d #Register the device or simply update its last heartbeat
		except Exception as e:
			log.error('Error parsing packet: ', data, ' from: ', addr)
			log.error(str(e))
	sock.close()

@route('/gc/devices', method='GET')
def getDevices():
	return json.dumps([d for d in registered_devices])

@route('/gc/devices/<mac>', method='GET')
def getDevice(mac):
	return json.dumps(registered_devices[mac])

if __name__ == '__main__':
	d = DiscoveryBeaconRegistration.parseBeaconData(TEST)
	registered_devices[d['UUID']] = d

	t = threading.Thread(group=None, target=DiscoveryBeaconRegistrationListener, name='ListenForBeacons')
	t.start()
	
	#t2 = threading.Thread(group=None, target=DiscoveredBeaconsPrinter, name='WriteBeacons')
	#t2.start()

	HOST = os.environ.get('GCC_REST_SERVER_HOST', get_ip_address(NIC))
	try:
		PORT = int(os.environ.get('GCC_REST_SERVER_PORT', '10333'))
	except ValueError:
		PORT = 10333

	run(server='wsgiref', host=HOST, port=PORT)

	t.join()
	#t2.join()