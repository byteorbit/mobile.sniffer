"""

    TODO: Disabled for now due to Django dependency

    To execute these tests::
    
        export DJANGO=~Django-1.0.2-final/
        export PYTHONPATH=$DJANGO:~/workspace/mobile.sniffer
        python $DJANGO/django/bin/django-admin.py test --settings=mobile.sniffer.apexvertex.test_settings apexvertex

"""

__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.fi>"
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL"
__docformat__ = "epytext"

import unittest
import os

from mobile.sniffer.apexvertex.sniffer import ApexVertexSniffer
from mobile.sniffer.apexvertex.installer import install_apex_vertex

class TestWAPProfileSniffer(unittest.TestCase):
    """ Test Apex Vertex sniffing backend basic functionality """
    
    def setUp(self):
        install_apex_vertex()
            
    def get_phone_by_user_agent(self, ua):
        
        class MockRequest:
            environ = {}
            
        req = MockRequest()
        req.environ["HTTP_USER_AGENT"] = ua
        
        sniffer = ApexVertexSniffer()
        ua = sniffer.sniff(req)
        return ua
        
            
    def test_n95(self):
            
        ua = self.get_phone_by_user_agent("Nokia N95: Mozilla/5.0 (SymbianOS/9.2; U; Series60/3.1 NokiaN95/21.0.016; Profile/MIDP-2.0 Configuration/CLD(-1.1) AppleWebKit/413 (KHTML, like Gecko) Safari/413")
    
        assert ua.get("stream.3gp.h263") == True
        assert ua.get("mp4.h264.level11") == True    
