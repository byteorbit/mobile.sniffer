"""

    Download WAP profile information provided by HTTP headers run-time.
    
    Uses Django object relation mappings and Django database abstraction for storing persistent data in SQL database.
    Thus, Django must be configured before use.
    

"""

__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.fi>"
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL"
__docformat__ = "epytext"


import os, sys
import urllib2

from mobile.sniffer import base

from models import WAPProfile


class WAPProfileDownloader:
    """ Dummy urllib2 wrapper. 
    
    Unit tests can override this to simulate WAP profile download functionality.
    """
    
    def download(self, url):
        f = urllib2.urlopen(url)
        data = f.read()
        f.close()
        return data
        

class WAPProfileSniffer(base.Sniffer):
    """ Sniffer which looks for a WAP profile.
    
    For more information: http://www.developershome.com/wap/detection/
    """
    
    def __init__(self):
        """        
        """
        self.downloader = WAPProfileDownloader()
        
    def get_profile_url(self, request):
        """ Try extract WAP profile URL from the request.
                
        """        
        environ = self.get_environ(request)
        
        print "Got env:" + str(environ)
        
        if "X-WAP-PROFILE" in environ:
            return environ["X-WAP-PROFILE"]

        if "HTTP_PROFILE" in environ:
            return environ["HTTP_PROFILE"]
            
        # Try find opt header http://www.developershome.com/wap/detection/detection.asp?page=uaprof#4.2.Where%20to%20Find%20the%20URL%20of%20the%20UAProf%20Document%20of%20a%20Mobile%20Device|outline
        namespace = None
        for header, value in environ.items():
            if header.upper() == "OPT":
                # Opt: "http://www.w3.org/1999/06/24-CCPPexchange" ; ns=80
                # 80-Profile: "http://wap.sonyericsson.com/UAprof/T68R502.xml"
                if "http://www.w3.org/1999/06/24-CCPPexchange" in value:
                    ns, value = value.split(";")
                    number = value.split("=")[-1]
                    namespace = number.strip()
                
        if namespace:
            # 80-Profile: "http://wap.sonyericsson.com/UAprof/T68R502.xml"
            header_name  = namespace + "-" + profile
            profile_url = environ.get(header_name, None)
            return profile_url
            
        return None
        
    def download_profile(self, url):
        """ Download WAP profile XML file and save it to the database for further use.
        
        @param url: URL to wap profile, e.g. http://wap.sonyericsson.com/UAprof/T68R502.xml
        """
        data = self.downloader.download(url)        
        entry = WAPProfile.objects.create(url=url, data=data)
        return entry
        
    def get_or_download_profile(self, url):
        """ """
                
        try:
            handset = WAPProfile.objects.get(url=url)
        except WAPProfile.DoesNotExist:
            print "Downloading:" + url            
            handset = self.download_profile(url)
            
        
        return handset
    
    def sniff(self, request):
        """ Sniff handset based on WAP profile headers """
        from mobile.sniffer.wapprofile.models import WAPProfile

        url = self.get_profile_url(request)
        if not url:
            return None

        handset = self.get_or_download_profile(url)
        
        return handset

        

