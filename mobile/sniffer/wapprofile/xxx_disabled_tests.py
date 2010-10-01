"""

    TODO: Disabled these settings due to dependencies and conflicts with Zope test runner.
    WAP profiles were a bad idea anyway.

    To execute these tests::
    
        export DJANGO=~Django-1.0.2-final/
        export PYTHONPATH=$DJANGO:~/workspace/mobile.sniffer
        python $DJANGO/django/bin/django-admin.py test --settings=mobile.sniffer.wapprofile.test_settings wapprofile

"""

__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.fi>"
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL"
__docformat__ = "epytext"

import unittest
import os

from mobile.sniffer.wapprofile.sniffer import WAPProfileSniffer, WAPProfileDownloader

class MockRequest:
    
    def __init__(self):
        self.environ = {}
        
class MockDownloader(WAPProfileDownloader):
    """ Check whether we actually perform download or return cached value """
    
    def __init__(self):
        self.download_count = 0
    
    def download(self, url):
        self.download_count += 1
        return WAPProfileDownloader.download(self, url)

class TestWAPProfileSniffer(unittest.TestCase):
    
    def setUp(self):
        self.sniffer = WAPProfileSniffer()
        self.sniffer.downloader = MockDownloader()
    
    def test_download_x_wap_profile(self):
        
        request = MockRequest()
        request.environ["X-WAP-PROFILE"] = "http://nds1.nds.nokia.com/uaprof/N6230ir200.xml"
        
        ua = self.sniffer.sniff(request)
        self.assertNotEqual(ua, None)
        
        #
        # Test some DeviceAtlas compatible mappings
        #
        self.assertEqual(ua.get("usableDisplayWidth"), 208)
        
        self.assertEqual(ua.get("fakeProperty"), None)
        
    def test_support_3gp_streaming(self):
        """ Check that we extract 3GP streaming information properly from the profile """

        # N6230i
        request = MockRequest()
        request.environ["X-WAP-PROFILE"] = "http://nds1.nds.nokia.com/uaprof/N6230ir200.xml"

        ua = self.sniffer.sniff(request)
        
        streaming_3gp = ua.get("stream.3gp.h263")
        self.assertEqual(streaming_3gp, True)
                
        # N95
        request = MockRequest()
        request.environ["X-WAP-PROFILE"] = "http://nds1.nds.nokia.com/uaprof/NN95-1r100-VF3GMIP.xml"

        ua = self.sniffer.sniff(request)
        
        streaming_3gp = ua.get("stream.3gp.h263")
        self.assertEqual(streaming_3gp, True)
        
        
    def test_support_mp4(self):

        # N6230i
        request = MockRequest()
        request.environ["X-WAP-PROFILE"] = "http://nds1.nds.nokia.com/uaprof/N6230ir200.xml"

        ua = self.sniffer.sniff(request)
        
        self.assertEqual(ua.get("mp4.h264.level11"), False)
                
        # N95
        request = MockRequest()
        request.environ["X-WAP-PROFILE"] = "http://nds1.nds.nokia.com/uaprof/NN95-1r100-VF3GMIP.xml"

        ua = self.sniffer.sniff(request)
        
        
        self.assertEqual(ua.get("mp4.h264.level11"), True)

        
    def test_sony(self):
        """ Test sony style mobile sniffing """
        # http://wap.sonyericsson.com/UAprof/T68R502.xml

        request = MockRequest()
        
        # TODO: Fill in Sony style headers here... how?
        request.environ["HTTP_PROFILE"] = "http://wap.sonyericsson.com/UAprof/T68R502.xml"
        
        ua = self.sniffer.sniff(request)
        ua.dump()
        
        self.assertEqual(ua.url, "http://wap.sonyericsson.com/UAprof/T68R502.xml")
        
        self.assertNotEqual(ua, None)
        
        self.assertEqual(ua.get("usableDisplayWidth"), 101)
        
        
    def test_cache(self):

        request = MockRequest()
        request.environ["X-WAP-PROFILE"] = "http://nds1.nds.nokia.com/uaprof/N6230ir200.xml"
        
        ua = self.sniffer.sniff(request)
        ua = self.sniffer.sniff(request)
        
        self.assertEqual(self.sniffer.downloader.download_count, 1)
        
        
    
