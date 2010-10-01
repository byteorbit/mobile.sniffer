"""

    Command line test suite to use the full potential of mobile.sniffer. Buahahaahaa.
    
    Also serve as a standalone set-up example.
    
    1) Set up all known backends
    
    2) Chain them to one ChainedSniffer 
    
    3) Check that chained sniffer returns valid responses from all backends
    

"""

__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.fi>"
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL"
__docformat__ = "epytext"


import os,sys

from django.core import serializers

os.environ["DJANGO_SETTINGS_MODULE"] = "mobile.sniffer.tests.test_settings"

#from django.db import models

# Get all sniffers we got
from mobile.sniffer.chain import ChainedSniffer

from mobile.sniffer.apexvertex.installer import install_apex_vertex

def install_database():
    """ Create Apex Vertex + WAP profile tables in SQL datbase"""
    from django.core.management.commands import syncdb
    
    cmd = syncdb.Command()
    cmd.handle_noargs(verbosity=0)
    
    
def install_deviceatlas():
    """ Download DeviceAtlas API and data files and put them to PYTHONPATH.
    
    Set your DeviceAtlas username / pwd in da_user and da_password environment variables.
    """    
    global da_api_file
    from mobile.sniffer.deviceatlas.installer import DAInstaller
    
    username = os.environ["da_user"]
    password = os.environ["da_password"]
    
    installer = DAInstaller(username, password)
    da_api_file = installer.proceed()
        

def prepare():
    """ Load data to database. 
    
    Normally you do this only once for your persistent database.
    """
    install_database() # SQL for Apex Vertex + WAP profiles
    install_deviceatlas() # Download device atlas files
    install_apex_vertex() # Load initial Apex Vertex data
    
    
def create_test_request(user_agent=None, profile_url=None):
    """
    """
    class MockRequest:    
        environ = {}
        
    req = MockRequest()
    
    if user_agent:
        req.environ["HTTP_USER_AGENT"] = user_agent
        
    if profile_url:
        req.environ["HTTP_PROFILE"] = profile_url
        
    return req
        
def run():
    
    # Do imports here, because Django init order causes otherwise circular imports
    from mobile.sniffer.apexvertex.sniffer import ApexVertexSniffer
    from mobile.sniffer.wapprofile.sniffer import WAPProfileSniffer 
    from mobile.sniffer.deviceatlas.sniffer import DeviceAtlasSniffer
    
    
    # Create all supported sniffers
    da = DeviceAtlasSniffer(da_api_file)
    apex = ApexVertexSniffer()
    wap = WAPProfileSniffer()
        
    # Preferred order of sniffers    
    sniffer = ChainedSniffer([apex, wap, da])
        
    n95 = "Mozilla/5.0 (SymbianOS/9.2; U; Series60/3.1 NokiaN95/11.0.026; Profile MIDP-2.0 Configuration/CLDC-1.1) AppleWebKit/413 (KHTML, like Gecko) Safari/413"
    req = create_test_request(n95)
    
    multi_backend_ua = sniffer.sniff(req)    
    provider, val = multi_backend_ua.get_with_provider("stream.3gp.h263")
    
    assert provider == apex        
    assert multi_backend_ua.get("mp4.h264.level11") == True    

    # This should come from deviceatlas - BlackBerry does not announce WAP profiles    
    blackberry = "BlackBerry7100i/4.1.0 Profile/MIDP-2.0 Configuration/CLDC-1.1 VendorID/103"
    req = create_test_request(blackberry)
    
    multi_backend_ua = sniffer.sniff(req)    
    provider, val = multi_backend_ua.get_with_provider("usableDisplayWidth")
    assert provider == da
    
    print "Got:" +str(provider) + " " + str(val)
    
    # Then test something which is not user agent based -
    # this very old Sony
    sony = "http://wap.sonyericsson.com/UAprof/T68R502.xml"
    req = create_test_request(profile_url = sony)
    multi_backend_ua = sniffer.sniff(req)        
    provider, val = multi_backend_ua.get_with_provider("usableDisplayWidth")
    assert provider == wap, "Got backend: " + str(provider)
    assert val == 101, "Got " + str(val)
    

if __name__ == "__main__":
    prepare()
    run()
    
    
    