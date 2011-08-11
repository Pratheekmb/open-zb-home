from twisted.internet import reactor, threads
from twisted.internet.protocol import Protocol, Factory, defer
from twisted.web import static
from twisted.web.server import Site
from twisted.web.resource import Resource
import serial
from xbee import ZigBee, XBee
import cgi


################################################################################
# Set up your parameters:
################################################################################
PASSWORD = "yourpasswordhere"
TCP_PORT = 4321

ZB_PORT = '/dev/tty.usbserial-A800czWn'
ZP_SPEED = 57600

ZB_2 = '\x00\x13\xA2\x00\xNN\xNN\xNN\xNN' #replane NNs with your ZBs ADDR.
ZB_4 = '\x00\x13\xA2\x00\xNN\xNN\xNN\xNN'
ZB_BCAST = '\x00\x00\x00\x00\x00\x00\xFF\xFF'

################################################################################
# Globals and init:
################################################################################
TCPClients = []
ser = serial.Serial(ZB_PORT, ZB_SPEED)
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
		xbee.send('tx', dest_addr_long=ZB_2, dest_addr='\xFF\xFE', data=data[1:])
	elif data[0] == '4':
		xbee.send('tx', dest_addr_long=ZB_4, dest_addr='\xFF\xFE', data=data[1:])
	else:
		xbee.send('tx', dest_addr_long=ZB_BCAST, dest_addr='\xFF\xFE', data=data[1:])


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

reactor.listenTCP(TCP_PORT, TcpSerialEchoFactory())

################################################################################
# Set up web interface. This sets up the form handling section
# and the webserver root folder.
################################################################################
class FormPage(Resource):

	def render_POST(self, request):
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

root = static.File("/Users/ruzz/AutoHome/Site")
root.putChild("form", FormPage())
factory = Site(root)
reactor.listenTCP(8880, factory)


################################################################################
################################################################################

                   
# Initial call for xbee listen. It will respawn itself for the next ones..
threads.deferToThread(getFromXBeeThread).addCallback(dispatchTCP)

# Start reactor:
reactor.run()