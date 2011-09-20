#!/usr/bin/python

from twisted.internet import reactor, threads, task
from twisted.internet.protocol import Protocol, Factory, defer
from twisted.web import static
from twisted.web.server import Site
from twisted.web.resource import Resource

from websocket import WebSocketHandler, WebSocketSite

from xbeeService.protocol import ZigBeeProtocol
from twisted.internet.serialport import SerialPort

from time import strftime

import cgi

################################################################################
# Globals and init:
################################################################################

from AutoHomeConf import * #the file with all your settings.

TCPClients = []
WebSockClients=[]
xbee=[]
timer = None
delimiter = None



################################################################################
# Handle XBEE I/O
################################################################################
################################################################################
# Dispatch addressed commands to zigbee ZB, after making sure frame starts correctly.
# eg: data = "2[f1]" will transmit "[f1]" to specific device
# eg: data = "2![f1]" will transmit "[f1]" to specific device without ack on zibee layer.
# eg: data = "[x]"   will broadcast [x]
# note there are no acks on zibee layer during broadcast so ">[" is not valid anyway
################################################################################
	
class ZBHandler(ZigBeeProtocol):
	def __init__(self, *args, **kwds):
		super(ZBHandler, self).__init__(*args, **kwds)
		xbee.append(self)


	def handle_packet(self, xbeePacketDictionary):
		response = xbeePacketDictionary

			
		if response.get("source_addr_long", "default") in ZB_reverse:
			if response["id"] == "rx":
				# Silently respond "OK" to AT calls (when module starts up).
				if response["rf_data"]=="AT":
					reactor.callFromThread(self.send,
								 "tx",
								 frame_id="\x01",
								 dest_addr_long=response["source_addr_long"],
								 dest_addr="\xff\xfe",
								 data="OK")
				else:
					print strftime("%Y-%m-%d %H:%M:%S").encode('utf8'), "<<< FROM:",\
					ZB_reverse[response["source_addr_long"]],\
					"DATA: ", response["rf_data"],
					
					broadcastToClients(response["rf_data"])

			elif response["id"] == 'remote_at_response':
					print strftime("%Y-%m-%d %H:%M:%S").encode('utf8'), "<<< FROM:",\
					ZB_reverse[response["source_addr_long"]],\
					" CMD:", response["command"],\
					" STATUS:", response["status"].encode('hex')

			else:
				print response
			

	def dispatchZB(self, data):
		if len(data) > 2:
	
			index=0
			frame_id='\x01'
			dest_addr = ZB["BC"]
			type=None;
	
			print strftime("%Y-%m-%d %H:%M:%S").encode('utf8'), ">>>  ", data,
	
			# First, make sure frame starts correctly and determin the addressing scheme to use:
			if data[0] == '[':				#No address specified: broadcast.
				index=0
				type="tx";
			elif data[0] == '(':			#No address specified: broadcast.
				index=0
				type="at";
				
				
			elif data[0] in ZB:			#Valid Address Specified.
				dest_addr=ZB[data[0]]
				if data[1:3] == '![':	#No ack transmit to specific address.
					index=2
					frame_id='\x00'
					type="tx";
				elif data[1:3] == '!(':	#No ack transmit to specific address.
					index=2
					frame_id='\x00'
					type="at";
					
					
				elif data[1] == '[':
					type="tx"
	
				elif data[1] == '(':
					type="at"
					index=1
					
				else:
					print "INVALID START OF FRAME"
					return
			else:
				print "INVALID ADDRESS"
				return
				
			# Also, make sure frame ends correctly, only then send, otherwise just return.	
			if (type=="tx" and data[-1] == ']'):	
				reactor.callFromThread(self.send,
										'tx',
										dest_addr_long=dest_addr,
										dest_addr='\xFF\xFE',
										frame_id=frame_id,
										data=data[index:])
				print ""
			elif (type=="at" and data[-1]==')'):
				parts= data[index+1:-1].split(":")
				if len(parts) !=3:
					print "BAD COMMAND"
					return
				option = parts[0]
				command = parts[1]
				parameter = parts[2] 
				print "[Option = ", option, ", Command = ", command, ", Parameter = ", parameter, "]" 
				reactor.callFromThread(self.send,
										'remote_at',
										frame_id='A',
										dest_addr_long=dest_addr,
										dest_addr='\xFF\xFE',
										options=option.decode('hex'),
										command=command,
										parameter=parameter.decode('hex'))
			else:
				print "INVALID END OF FRAME"

s = SerialPort(ZBHandler(escaped=False), ZB_PORT, reactor, ZB_SPEED)


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

""" 
################################################################################
# Handle TCP socket connections:
# currently disabled. I will first find a good use for it (Android app?)  
# then work on it, then add ssl.
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
print "TCP socket listening on port: ", TCP_PORT
"""
################################################################################
# Set up web interface. This sets up the form handling section
# and the webserver root folder.
################################################################################
class FormPage(Resource):

	def dispatch(self, data):
		for x in xbee:
			x.dispatchZB(data)

	def render_POST(self, request):
		if  ('pass' in request.args) & ('cmd' in request.args):
			if cgi.escape(request.args["pass"][0]) == WEBSITE_PASSWORD:
				print "Authenticated ",
				data = cgi.escape(request.args["cmd"][0])
				#Handle a delayed request. ie, t180*4[l1] will send the command [l1] to device 4 in 2 minutes.
				if data[0] == 't':
					delimiter= data.find("*")
					if 1 < delimiter < data.find("["):
						if int(data[1:delimiter]):
							timer = reactor.callLater(int(data[1:delimiter]), self.dispatch, data[delimiter+1:])

				else:
					self.dispatch(data)
				return '<html><body>Submitted</body></html>'
			else:
				print "Wrong password in POST request"
				return '<html><body>Wrong PWD</body></html>'
		else:	
			print "No command AND password in post request"
			return '<html><body>Not Submitted</body></html>'


root = static.File(WEBSITE_ROOT)
root.putChild("form", FormPage())
factory = Site(root)
#reactor.listenTCP(WEBSITE_PORT, factory) #If you choose not to use ssl for https. Update index.html appropriately.

from twisted.internet import ssl
reactor.listenSSL(WEBSITE_PORT, factory, ssl.DefaultOpenSSLContextFactory(SSL_PRIVKEY, SSL_CERT,))
print "Web server listening on port: ", WEBSITE_PORT

################################################################################
# Run our websocket server which also serves a website, so the WEBSITE_ROOT is just served anyway.
# The prob is that WebSocketSite can't handle POST requests, so it can't be the only server.
################################################################################
class WSHandler(WebSocketHandler):
	def __init__(self, transport):
		WebSocketHandler.__init__(self, transport)
		self.authenticated = False;

	def dispatch(self, data):
		for x in xbee:
			x.dispatchZB(data)

	def frameReceived(self, data):
		if not self.authenticated:
			if data==WEBSITE_PASSWORD:
				self.authenticated=True
				WebSockClients.append(self)
				print "Authenticated"
		else:
			#Handle a delayed request. ie, t180*4[l1] will send the command [l1] to device 4 in 2 minutes.
			if data[0] == 't':
				delimiter= data.find("*")
				if 1 < delimiter < data.find("["):
					if int(data[1:delimiter]):
						timer = reactor.callLater(int(data[1:delimiter]), self.dispatch, data[delimiter+1:])
						


			else:
				self.dispatch(data)
	
	def connectionMade(self):
		print 'Connected to client..',

	def connectionLost(self, reason):
		print 'Lost connection.'
		if self.authenticated:
			WebSockClients.remove(self)

root = static.File(WEBSITE_ROOT)
site = WebSocketSite(root)
site.addHandler('/ws', WSHandler)
#reactor.listenTCP(WEBSOCKET_PORT, site) #If you choose not to use wss, update index.html appropriately.
reactor.listenSSL(WEBSOCKET_PORT, site, ssl.DefaultOpenSSLContextFactory(SSL_PRIVKEY, SSL_CERT,))
print "Web socket listening on port: ", WEBSOCKET_PORT



################################################################################
################################################################################


if __name__ == '__main__':

	# Start reactor:
	reactor.run()
