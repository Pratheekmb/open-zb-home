################################################################################
# Set up your parameters:
################################################################################
TCP_PORT = 4321

WEBSITE_PASSWORD = "makeupsomepassword" #not yet implemented 
WEBSITE_ROOT = "/Users/ruzz/open-zb-home/Site"
WEBSITE_PORT = 8880
WEBSOCKET_PORT = 8881

ZB_PORT = '/dev/tty.usbserial-A800czWn'
ZB_SPEED = 57600

#Change with values shown on the back of your XBee Modules.


ZB={
        "2":'\x00\x13\xA2\x00\x40\x7A\x38\x58',
        "4":'\x00\x13\xA2\x00\x40\x76\x47\xB6',
        "BC":'\x00\x00\x00\x00\x00\x00\xFF\xFF'
}

