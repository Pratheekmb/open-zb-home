################################################################################
# Set up your parameters:
################################################################################
TCP_PORT = 4321

import hashlib
WEBSITE_PASSWORD = hashlib.md5("mypass").hexdigest() 
WEBSITE_ROOT = "/Users/ruzz/open-zb-home/Site"
WEBSITE_PORT = 8880
WEBSOCKET_PORT = 8881

ZB_PORT = '/dev/tty.usbserial-A800czWn'
ZB_SPEED = 57600

#Change with values shown on the back of your XBee Modules.


ZB={
        "1":'\x00\x13\xA2\x00\x40\x3B\x8F\x4E',
        "2":'\x00\x13\xA2\x00\x40\x7A\x38\x58',
        "3":'\x00\x13\xA2\x00\x40\x76\x47\xB4',
        "4":'\x00\x13\xA2\x00\x40\x76\x47\xB6',
        "BC":'\x00\x00\x00\x00\x00\x00\xFF\xFF'
}

#ZB_reverse = dict((ZB[i],i) for i in ZB)

ZB_reverse={
        ZB["1"]:'M1',
        ZB["2"]:'AC',
        ZB["3"]:'M2',
        ZB["4"]:'ML',
        ZB["BC"]:'BC'
}



############################
# To create key and certificate:
# openssl genrsa > privkey.pem
# Then:
# openssl req -new -x509 -key privkey.pem -out cacert.pem -days 1000
# feel free to comment these out if you dont want to use ssl, also update the main script accordingly.
###############################
SSL_PRIVKEY = '/Users/ruzz/open-zb-home/privkey.pem'
SSL_CERT = '/Users/ruzz/open-zb-home/cacert.pem'
