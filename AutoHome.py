#!/usr/bin/python

from twisted.internet import reactor, threads
from twisted.internet.protocol import Protocol, Factory, defer
from twisted.web import static
from twisted.web.server import Site
from twisted.web.resource import Resource

from websocket import WebSocketHandler, WebSocketSite

import serial
from xbee import ZigBee, XBee

from time import strftime
import cgi

################################################################################
# Globals and init:
################################################################################

from AutoHomeConf import * #the file with all your settings.

TCPClients = []
WebSockClients=[]
ser = serial.Serial(ZB_PORT, ZB_SPEED)
xbee = ZigBee(ser) 

################################################################################
# Dispatch addressed commands to zigbee devices, after making sure frame starts correctly.
# eg: data = "2[f1]" will transmit "[f1]" to specific device
# eg: data = "2![f1]" will transmit "[f1]" to specific device without ack on zibee layer.
# eg: data = "[x]"   will broadcast [x]
# note there are no acks on zibee layer during broadcast so ">[" is not valid anyway
################################################################################
def dispatchZB(data):
	if len(data) > 2:

		index=1
		frame_id='\x01'
		dest_addr = ZB["BC"]

		print strftime("%Y-%m-%d %H:%M:%S").encode('utf8'), " CMD: ", data,

		# First, make sure frame starts correctly and determin the addressing scheme to use:
		if data[0] == '[':			#No address specified: broadcast.
			index=0
		elif data[0] in ZB:			#Valid Address Specified.
			dest_addr=ZB[data[0]]
			if data[1:3] == '![':	#No ack transmit to specific address.
				index=2
				frame_id='\x00'
			elif data[1] == '[':
				pass
			else:
				print "INVALID START OF FRAME"
				return
		else:
			print "INVALID ADDRESS"
			return
			
		# Also, make sure frame ends correctly, only then send, otherwise just return.	
		if data[-1] == ']':
			xbee.send('tx', dest_addr_long=dest_addr, dest_addr='\xFF\xFE', frame_id=frame_id, data=data[index:])
			print "SENT"
		else:
			print "INVALID END OF FRAME"

	return

################################################################################
# Send data to all TCP + Websocket clients.
################################################################################
def broadcastToClients(data, source=None, timestamp=True):

	if timestamp:
		data = strftime("%Y-%m-%d %H:%M:%S").encode('utf8') + ": " + data
		
	for client in TCPClients:
		if client != source:
			client.transport.write(data)
	for client in WebSockClients:
		if client != source:
			client.transport.write(data)

################################################################################
# Handle TCP socket connections:
################################################################################
class TcpSocket(Protocol):

	def connectionMade(self):
		self.factory.clients.append(self)

	def connectionLost(self, reason):
		self.factory.clients.remove(self)

	def dataReceived(self, data):
		dispatchZB(data)

class TcpSocketFactory(Factory):
    protocol = TcpSocket
    def __init__(self):
        self.clients = TCPClients

reactor.listenTCP(TCP_PORT, TcpSocketFactory())

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

root = static.File(WEBSITE_ROOT)
root.putChild("form", FormPage())
factory = Site(root)
#reactor.listenTCP(WEBSITE_PORT, factory) #If you choose not to use ssl for https. update index.html file too.

from twisted.internet import ssl
reactor.listenSSL(WEBSITE_PORT, factory, ssl.DefaultOpenSSLContextFactory(SSL_PRIVKEY, SSL_CERT,))

################################################################################
# Run our websocket server which also serves a website, so the WEBSITE_ROOT is just served anyway.
# The prob is that WebSocketSite can't handle POST requests, so it can't be the only server.
################################################################################
class WSHandler(WebSocketHandler):
	def __init__(self, transport):
		WebSocketHandler.__init__(self, transport)

	def frameReceived(self, frame):
		dispatchZB(frame);
		
	def connectionMade(self):
		print 'Connected to client.'
		WebSockClients.append(self)

	def connectionLost(self, reason):
		print 'Lost connection.'
		WebSockClients.remove(self)

root = static.File(WEBSITE_ROOT)
site = WebSocketSite(root)
site.addHandler('/ws', WSHandler)
#reactor.listenTCP(WEBSOCKET_PORT, site)
reactor.listenSSL(WEBSOCKET_PORT, site, ssl.DefaultOpenSSLContextFactory(SSL_PRIVKEY, SSL_CERT,))


################################################################################
# Handle reading from XBEE. 
################################################################################
from xbeeService import *

class XbeeReader:
	def decodeFloat(self, var):
		text = ""
		for i in range(0, len(var)):
			text += var[i]
		return unpack('f', text)[0]

	def handle_packet(self, xbeePacketDictionary):
		response = xbeePacketDictionary
		print response
		if response ["id"]=="rx":
			broadcastToClients(response["rf_data"])
			return response["rf_data"]
			
class XbeeTest(ZigBeeProtocol, XbeeReader):
	pass
			
SerialPort(XbeeTest(), ZB_PORT, reactor, ZB_SPEED)

################################################################################
################################################################################


# Start reactor:
print "Web server listening on port: ", WEBSITE_PORT
print "Websocket listening on port : ", WEBSOCKET_PORT
print "TCP socket listening on port: ", TCP_PORT
reactor.run()
