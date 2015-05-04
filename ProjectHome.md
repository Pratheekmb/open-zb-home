A Python written "base-station" for ZigBee home automation.
The server, written with Python's [Twisted](http://twistedmatrix.com/trac/) network-engine and the [python-xbee](http://code.google.com/p/python-xbee/) libraries, consists of a web-server for the interface and a form listener where it will receive POSTed commands for dispatch to a ZigBee network via a serial-port connected ZigBee. On supporting browsers, websockets are used for commands and offer feedback from the system too.

Two examples are provided for Arduino controlled end-point modules:
  * An Air Conditioning controlling Infra-Red transmitter which has pre-stored IR codes for ON/OFF and fan speeds. The module has a timer function too. IR functionality using  [Ken Shirriff's Arduino IR Library](http://www.arcfn.com/2009/08/multi-protocol-infrared-remote-library.html).
  * A lighting module which either turns ON/OFF a single digital output and a PWM RGB controller for either setting colors directly, or telling it to fade to a random color.

It should be pretty straight forward to adapt to your needs from there, eg: solid state relay to turn your toaster oven on. Also, this is just a framework for a system. Both Twisted and python-xbee libraries are very flexible and I urge you to review them to add the functionality you desire, but please chirp in and let me know what you're up to! :)

The interface is currently pretty simple HTML. Form submissions use either websockets or AJAX methods to send commands to the server. The current [color-picker](http://developer.yahoo.com/yui/colorpicker/) is part of [Yahoo's YUI library](http://developer.yahoo.com/yui/).

Update: SSL is implemented for both web server and websockets (wss). Non encrypted connections are NOT accepted. Simple authentication is implemented as a password's hash is stored in a cookie and sent either as first websocket frame or as a parameter with every AJAX post. Currently in the ssl branch until I've spent a few days with it.

![http://dl.dropbox.com/u/1351218/open-zb-home/Interface_Screen_Shot.png](http://dl.dropbox.com/u/1351218/open-zb-home/Interface_Screen_Shot.png)

<a href='http://www.youtube.com/watch?feature=player_embedded&v=7ahT2vtcdmY' target='_blank'><img src='http://img.youtube.com/vi/7ahT2vtcdmY/0.jpg' width='425' height=344 /></a>

The project is pretty young and I've only been programming for about a year and a half, so **constructive** feedback is more than welcome. Contact me if you would like to contribute to the code.

