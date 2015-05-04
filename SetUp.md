#How to get started..

# Hardware #

You will need at least 2 XBee/ZBee modules. The way this is currently set up is to have the one connected to the server in API mode, while the routers/end devices are in transparent/AT mode.

I won't get into how to do that since there are plenty of available resources.

I'm using ZigBee (Series 2) modules. If you use XBee (S1), change ZigBee to XBee in the xbeeservive.protocol file (after importing XBee).

I've supplied 2 example PDEs for Arduino which show a simple way to process incoming command frames. This should be pretty straight forward to adapt to your needs.

I'm working on directly interfacing with the xbee pins, this is partially implemented and will still undergo revisions.

# Software #

The server is based on 2 primary additions:
  1. [Twisted](http://twistedmatrix.com/trac/) - an event-driven networking engine written in Python.
  1. [python-xbee](http://code.google.com/p/python-xbee/) - Python tools for working with XBee radios.


It took me a few set-up's to finally settle on Twisted but a brief review of the server code will show you why. It's really simple to create the web-server and websocket handler, and will be pretty simple to enhance for future functionality.

You will need a Python interpreter, Twisted and the python-xbee libraries installed. OSX and Ubuntu come with the first 2 already set up and python-xbee is a mere setup.py install away.

You will need to modify parameters in the AutoHomeConf.py file:
**WEBSITE\_ROOT** needs to point to the included **Site** folder.
**ZB\_PORT**, **ZB\_SPEED** need to be set up, and you need to create ssl keys (instructions in the conf file). You will also need to update the MAC addresses for your devices