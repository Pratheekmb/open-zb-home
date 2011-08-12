from twisted.internet import reactor, threads
from twisted.internet.protocol import Protocol, Factory, defer
from twisted.web import static
from twisted.web.server import Site
from twisted.web.resource import Resource
import serial
from xbee import ZigBee, XBee
import cgi

################################################################################
# Globals and init:
################################################################################

import AutoHomeConf #the file with all your settings.

TCPClients = []
ser = serial.Serial(AutoHomeConf.ZB_PORT, AutoHomeConf.ZB_SPEED)
xbee = ZigBee(ser) 



################################################################################
# Handle reading from XBEE. Since it's currently blocking, 
# it's handled within a twisted deferToThread and respawns itself before exit
################################################################################
def getFromXBeeThread():
	while True:
		response = xbee.wait_read_frame()
		if response ["id"]=="rx":
			print response["rf_data"],
			threads.deferToThread(getFromXBeeThread).addCallback(dispatchTCP)
			return response["rf_data"]


################################################################################
# Send data to all TCP clients.
################################################################################
def dispatchTCP(data):
	for client in TCPClients:
		client.transport.write(data)


################################################################################
# Dispatch addressed commands to zigbee devices.
# eg: data = "2[f1]" will transmit "[f1]" to specific device
# eg: data = "[x]"   will broadcast [x]
################################################################################
def dispatchZB(data):
	print data
	if data[0] == '2':
		xbee.send('tx', dest_addr_long=AutoHomeConf.ZB_2, dest_addr='\xFF\xFE', data=data[1:])
	elif data[0] == '4':
		xbee.send('tx', dest_addr_long=AutoHomeConf.ZB_4, dest_addr='\xFF\xFE', data=data[1:])
	else:
		xbee.send('tx', dest_addr_long=AutoHomeConf.ZB_BCAST, dest_addr='\xFF\xFE', data=data[1:])


################################################################################
# Handle TCP socket connections:
################################################################################
class TcpSerialEcho(Protocol):

	def connectionMade(self):
		self.factory.clients.append(self)

	def connectionLost(self, reason):
		self.factory.clients.remove(self)

	def dataReceived(self, data):
		for client in self.factory.clients:
			if client != self:		#echo to all tcp clients except self.
				client.transport.write(data)
		dispatchZB(data)

class TcpSerialEchoFactory(Factory):
    protocol = TcpSerialEcho
    def __init__(self):
        self.clients = TCPClients

reactor.listenTCP(AutoHomeConf.TCP_PORT, TcpSerialEchoFactory())

################################################################################
# Set up web interface. This sets up the form handling section
# and the webserver root folder.
################################################################################
class FormPage(Resource):

	def render_POST(self, request):
		#password not yet implemented in web page..
		"""if  ('cmd' in request.args) & ('pwd' in request.args):
			if cgi.escape(request.args["pwd"][0]) == PASSWORD:
				dispatchZB(cgi.escape(request.args["cmd"][0]))
				return '<html><body>You submitted: %s</body></html>' % (cgi.escape(request.args["cmd"][0]),)
			return '<html><body>Wrong PWD</body></html>'
		return '<html><body>Not Submitted</body></html>'"""
		if  'cmd' in request.args :
			dispatchZB(cgi.escape(request.args["cmd"][0]))
			return '<html><body>You submitted: %s</body></html>' % (cgi.escape(request.args["cmd"][0]),)
		return '<html><body>Not Submitted</body></html>'

root = static.File(AutoHomeConf.WEBSITE_ROOT)
root.putChild("form", FormPage())
factory = Site(root)
reactor.listenTCP(AutoHomeConf.WEBSITE_PORT, factory)


################################################################################
################################################################################

                   
# Initial call for xbee listen. It will respawn itself for the next ones..
threads.deferToThread(getFromXBeeThread).addCallback(dispatchTCP)

# Start reactor:
reactor.run()