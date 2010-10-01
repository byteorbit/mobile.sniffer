"""

    WAP profile storage and parsing functions.

"""

__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.fi>"
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL"
__docformat__ = "epytext"


import StringIO

from django.db import models

from mobile.sniffer import base

try:
    import rdflib
except ImportError:
    raise RuntimeError("You must have RDF lib installed in order to use WAP profile back end - http://pypi.python.org/pypi/rdflib")

from rdflib.Graph import Graph
from rdflib.StringInputSource import StringInputSource

class WAPProfile(models.Model, base.UserAgent):
    """ Provide SQL persistent cache + DeviceAtlas compatible RDF parser around WAP profile XML """
    # Resolved profile download address 
    url = models.CharField(max_length=512, unique=True)
    
    # Downloaded WAP data as XML string
    data = models.TextField()
    
    
    def parse(self):
        """ Parse RDF.
        
        Cache RDF parse results in the object for the further calls.
        """

        if not hasattr(self, "_rdf_parse_data"):
            # Use parser cache - lifetime is the same as for this model object
            source = StringInputSource(self.data)
            g = Graph()            
            self._rdf_parse_data = g.parse(source)
        

    def get(self, name):
        """ Extract properties from there in DeviceAtlas compatible way.
                
        """                
        
        self.parse()
                
        if name == "usableDisplayWidth":
            return self.get_screen_size()[0]
        elif name == "usableDisplayHeight":
            return self.get_screen_size()[1]
        elif name == "stream.3gp.h263":
            return self.get_3gp_streaming()
        elif name == "mp4.h264.level11":
            return self.get_download_mp4()
        
        return None
    
    def dump(self):
        self.parse()
        for i in self._rdf_parse_data:
            print i
        
    def _find_rdf_element(self, name=None, endswith=None):
        """ Go through RDF statements and try to find a matching element.
        
        @param name: Full rdflib.URIRef match
        @param endswith: End (anchor part) URI ref match
        @return: rdflib value (BNode or Literal)
        """
        # (rdflib.URIRef('#HardwarePlatform'), rdflib.URIRef('http://www.openmobilealliance.org/tech/profiles/UAPROF/ccppschema-20021212#Keyboard'), rdflib.Literal(u'PhoneKeyPad'))
        # (rdflib.URIRef('#HardwarePlatform'), rdflib.URIRef('http://www.openmobilealliance.org/tech/profiles/UAPROF/ccppschema-20021212#ScreenSize'), rdflib.Literal(u'208x208'))        
        # (rdflib.URIRef('#HardwarePlatform'), rdflib.URIRef('http://www.openmobilealliance.org/tech/profiles/UAPROF/ccppschema-20021212#InputCharSet'), rdflib.BNode('lqBmatRR3'))
        
        parsed = self._rdf_parse_data
        
        if name:
            name = name.lower()
            
        if endswith:
            endswith = endswith.lower()
        
        for section,property,value in parsed:   
            
            test_val = property.title().lower()
            
            if name:
                if test_val == name:
                    return value
            
            if endswith:
                if test_val.endswith(endswith):
                    return value
         
        return None  
        #raise AttributeError("WAP profile %s did not declare element %s" % (self.url, name))

    def _find_bnode_values(self, name):
        
        results = []

        for section,property,value in self._rdf_parse_data:  
            if section.title() == name:
                results.append(unicode(value)) # Assume all objects are rdflib.Literals
           
        return results

        
    def get_screen_size(self):
        # (rdflib.URIRef('#HardwarePlatform'), rdflib.URIRef('http://www.openmobilealliance.org/tech/profiles/UAPROF/ccppschema-20021212#ScreenSize'), rdflib.Literal(u'208x208')) 
        
    
        
        elem = self._find_rdf_element(endswith="#ScreenSize")
        if not elem:
            return [None, None]
        
        value = elem.decode()
        items = value.split('x')
        return [ int(items[0]), int(items[1]) ]
        
    def get_3gp_streaming(self):
        """ Check for h263 RTSP streaming in 3GP container.
        
        TODO: There is special #Streaming section but it seem not to be present in the older profiles
        
        TODO: Special cases video player accepts 3GP as a downloadable, but has no streaming support
        """        
        #http://www.3gpp.org/profiles/PSS/ccppschema-PSS6#Streaming
        elem = self._find_rdf_element(endswith="#CcppAccept")        
        if not elem:
            return False
                
        values = self._find_bnode_values(elem.title())
        
        return u"video/3gpp" in values
        
    def get_download_mp4(self):
        """ Check for (progressive) h264 + AAC MP4 download
        """
        elem = self._find_rdf_element(endswith="#ThreeGPAccept")                
        if not elem:
            return False
                
        values = self._find_bnode_values(elem.title())
        
        #for i in self._rdf_parse_data:
        #    print i
        
        #print "Got values:" + str(values)
        return u"video/mpeg4" in values
        