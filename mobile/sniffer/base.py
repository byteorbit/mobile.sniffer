"""

    Base classes/interface declarations for mobile user agent sniffers.

"""

__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.fi>"
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL"
__docformat__ = "epytext"

class Sniffer(object):
    """ Mobile user agent detector. 
    
    This utility class will take in HTTP request as a parameter and 
    returns the user agent information for it.
    """
    
    
    def get_environ(self, request):
        """ Cross-python framework compatible way to extract HTTP headers from the request object. 
        
        
        @return: Dict of HTTP headers
        """
        
        if hasattr(request, "environ"):
            return request.environ
        elif hasattr(request, "META"):
            return request.META
        
        raise RuntimeError("Unknown HTTP request class:" + str(request.__class__))
    
    def get_user_agent(self, request):
        """ Get the user agent string from the request.
        
        Deal with proxy pecularies and such.
        
        @param: WSGIRequest like object
        @return: Real user agent string
        """

        # We might have conflicting request types - assume request.environ is used 
        environ = self.get_environ(request)
                
        agent = None
        
        if "HTTP_X_OPERAMINI_PHONE_UA" in environ:
            # Opera mini proxy specia case
            agent = environ["HTTP_X_OPERAMINI_PHONE_UA"]
        elif "HTTP_USER_AGENT" in environ:
            agent = environ["HTTP_USER_AGENT"]

        return agent
    
    def sniff(self, request):
        """ Determinate user agent based on incoming HTTP request.
        
        This method is allowed to open 
        
        @param request: WSGIRequest compatible HTTP request object
        @return: UserAgent
        """
        raise NotImplementedError("The subclass must implement")
    
    
class UserAgent(object):
    """ User agent information wrapper.
    
    Generic interface to access user agent information, like screen dimensions and supported videos.
    
    DeviceAtlas property naming convention was choosen as a base, since it is very well established.
    """
    
    def getCertainty(self):
        """ How confident we are about this user agent match.
        
        @return: 0...1 how certain the user agent match was. None if the information is not available.
        """
        return None
    
    def getMatchedUserAgent(self):
        """    
        @return: Which database UA entry corresponds the looked upUA
        """
        return None
    
    def get(self, name):
        """ Ask user agent record property.
        
        Available:
        
        * usableDisplayWidth
        
        * usableDisplayHeight
        
        @param name: DeviceAtlas compatible property name, see http://deviceatlas.com/properties
        
        @return: The asked property if known (any Python object, int string, etc.) or None if the database lacks this information
        """
        raise NotImplementedError("The subclass must implement")
    