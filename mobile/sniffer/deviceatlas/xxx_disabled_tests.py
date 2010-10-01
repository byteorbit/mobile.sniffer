"""

    Simple run-through test for DeviceAtlas.

    TODO: Disabled for now, because valid DeviceAtlas
    user account would be required.

"""
__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.fi>"
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL"
__docformat__ = "epytext"

import os,sys

from installer import DAInstaller
from sniffer import DeviceAtlasSniffer


if __name__ == "__main__":
    # Simple test run for DeviceAtlas sniffer
    
    # Assume device atlas username and password are in environment evariables
    # to avoid accidental credential leakages when committing to public SVN
    username = os.environ["da_user"]
    password = os.environ["da_password"]
    
    installer = DAInstaller(username, password)
    api_file = installer.proceed()
    
    
    class FakeRequest:
        """ Mock HTTP request """
        environ = {"HTTP_USER_AGENT" : "Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543a Safari/419.3"} 
    
    sniffer = DeviceAtlasSniffer(api_file)
    
    phone = sniffer.sniff(FakeRequest())
    
    assert phone.get("usableDisplayWidth") == 320, "Got width:" + str(phone.get("usableDisplayWidth"))

    assert phone.get("fakeProperty") == None # A property for which we don't have value
    
    print "OK!"
    