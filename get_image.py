"""
Short script to read one image from the zmq stream of the 
slsReceiver. Requires the zmq stream to be enabled, which
is already done in the config file
"""

#import the class QuadZmqReceiver form the file receiver.py
#located in the same folder
from receiver import QuadZmqReceiver

#import the Eiger detector class from the slsdet package
from slsdet import Eiger

#Read the ip and ports to connect to from the detector.
d = Eiger()
ip = d.rx_zmqip.str()
ports = d.rx_zmqport[0::2] #Workaround for fast quad

#This could also be circumvented by hardcoding the values
#or supply them from the command line like this
# ip = "128.178.66.100"
# ports = [30001, 30003] 

#Create the receiver
r = QuadZmqReceiver(ip, ports)

#Read one image from the zmq stream. Call blocks until an 
#image is ready. To avoid blocking forever a timeout_ms parameter
#can be supplied when creating the object:
# r = QuadZmqReceiver(ip, ports, timeout_ms = 100)
#If no image is available an exception is raised (zmq.error.Again)
image = r.read_frame()

#Now you are free to manipulate the image as needed
