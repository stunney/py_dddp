# py_dddp_rest
Dynamic Device Discovery Protocol - REST API

This script listens for DDDP (http://www.amx.com/assets/whitePapers/AMX.Dynamic.Device.Discovery.White.Paper.pdf) multicast/broadcast messages.

Prerequisites:
Python3
Python3-bottle

This script provides a REST interface for cached results of devices discovered during its runtime.  It is meant to reduce discovery
time of devices on the network for front-facing applications that are not always running.  This script is designed to run on OpenWRT
on your router or an IoT device such as an Onion Omega (onion.io).

Steps 1:  Configure the NIC you want to listen on for messages
Add an environment variable with the name of the NIC you want to connect to.  Default is 'wlan0'.  DDDP_CLIENT_NIC
Step 2:  Configure the NIC you want to serve HTTP REST calls from
Add an environment variable with the name of the NIC you want to serve from.  Default is DDDP_CLIENT_NIC.  GCC_REST_SERVER_HOST
Step 3:  Configure the PORT you want to serve HTTP REST calls from
Add an environment variable with the name of the NIC you want to serve from.  Default is 10333.  GCC_REST_SERVER_PORT

Now, run the script:
python3 dddp_rest.py

You will see lots of output.  If it is too chatty, comment out some print lines :)

From here, you should now be able to get a list of the registered UUIDs in the service's cache.
GET http://<host>:10333/gc/devices

From here, you can view details on each registered device by appending a UUID to the URL.
GET http://<host>:10333>/gc/devices/00-00-00-00-00-00

All returned data is in JSON UTF-8 format.

A couple of extended values have been added to support devices such as the GlobalCache (http://www.globalcache.com/) devices
config_url
config_name

If a non-GlobalCache device has been registered, these values will be 'None'.

There is also ALWAYS a test device registered with a UUID of 'GC100_000000000000_GCTestElement'.  Please ignore it.
