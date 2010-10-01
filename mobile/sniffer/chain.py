"""

    Chained user agent detection.
    
    Use several sources to sniff UAs for better accuracy.

"""

__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.fi>"
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL"
__docformat__ = "epytext"

import base

class ChainedSniffer(base.Sniffer):
    """ Chained sniffer.
    
    Use several sources to sniff UAs for better accuracy.
    """
    
    def __init__(self, sniffers):
        """
        @param sniffers: List of Sniffer instances 
        """
        self.sniffers = sniffers
    
    def sniff(self, request):
        """ Get a multi-backend UserAgent property multiplexer """
        return UserAgent(self.sniffers, request)
            
            
class UserAgent(base.UserAgent):
    """ Wrap around for several sniffers/data combinations.
    
    Go through all sniffers and return the first property match which is not None.
    """
    
    def __init__(self, sniffers, request):
        self.sniffers = sniffers
        self.request = request
    
    def get(self, name):        
        """ Look property from all enlisted backends """
        sniffer, value = self.get_with_provider(name)
        return value
        
    def get_with_provider(self, name):
        """ Get property value and tell which sniffer provided it.
        
        @return: tuple(sniffer instance, value)
        """
        for s in self.sniffers:
            ua = s.sniff(self.request)
            if ua:
                value = ua.get(name)
                if value is not None:
                    return s, value
                
        return None, None
    