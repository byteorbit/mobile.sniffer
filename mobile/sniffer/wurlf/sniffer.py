"""

     Wurlf based user agent sniffing backend.

     http://pypi.python.org/pypi/pywurfl/

"""

__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.fi>"
__copyright__ = "2010 Twinapex Research"
__license__ = "BSD"
__docformat__ = "epytext"

import copy
import os, sys

import Levenshtein

from pywurfl.algorithms import Tokenizer, JaroWinkler, Algorithm
from pywurfl import DeviceNotFound

from mobile.sniffer import base

class WurlfSniffer(base.Sniffer):
    """

    Native Wurlf capabilities are listed here: http://wurfl.sourceforge.net/help_doc.php
    """

    def __init__(self, database_file=None, accuracy_threshold=0.5):
        """

        @param database_file: Path to Wurlf XML file or None to use internal database
        """

        if database_file is None:
            # Import devices from the internal database shipped
            # with the source code
            from wurfl import devices
            self.devices = devices
        else:
            raise NotImplementedError("TODO")

        # Set search algorithm
        #self.search = JaroWinkler()
        #self.search = CustomJaroWinkler(accuracy=accuracy)
        self.accuracy_threshold = accuracy_threshold
        self.search = CustomJaroWinkler(self.accuracy_threshold)



    def sniff(self, request):
        """ Look up handset from DeviceAtlas database using HTTP_USER_AGENT as a key """

        agent = self.get_user_agent(request)

        if not agent:
            # print "No HTTP_USER_AGENT"
            return None
        
        if type(agent) == str:
            # Unicodify
            agent = agent.decode("utf-8")

        device = self.devices.select_ua(agent, search=self.search, normalize=True)
    
        # Fallback algo for convergence sites
        
        if device is None:
            # print "select_ua yield no result"
            return None
        
        if not hasattr(device, "accuracy"):
            # Direct match - no search algo involved
            # thus the match is perfect and use special number
            # to symbolize this ( > 1 )
            device.accuracy = 1.1
        
        if device.accuracy < self.accuracy_threshold:
            return None
    
        if not device.is_wireless_device:
            # Matched a desktop browser
            return None
        
        return UserAgent(device)
        
class UserAgent(base.UserAgent):
    """ Wurfl record wrapper, abstracted in mobile.sniffer way.
    """

    def __init__(self, device_object):

        # internal DA properties object
        self.device_object = device_object
                
        self.certainty = device_object.accuracy 
        
    def getCertainty(self):
        return self.certainty
    
    def getMatchedUserAgent(self):
        """
        """
        return self.device_object.devua

    def get(self, name):
        """ Get property in DeviceAtlas compatible way.

        @param name: Property name, like usableDisplayWidth
        @return: Property value, string converted to a real object

        """

        if name == "is_wireless_device":
            return self.device_object.is_wireless_device

        if not self.device_object.is_wireless_device:
            # TODO: Make generic resolution
            # for identifying web browsers with width fallback
            # otherwise returned values for usable display with will be
            # the lowest common denominator (90 x 35)
            return None

        if name == "usableDisplayWidth":
            return self.device_object.max_image_width
        elif name == "usableDisplayHeight":
            return self.device_object.max_image_height
        else:
            return getattr(self.device_object, name, None)



class CustomJaroWinkler(JaroWinkler):
    """
    JaroWinkley algo implementation which exposes the hit accuracy.
    
    XXX: HACK: We create clone of the device and stick the match accuracy there,
    as pywurlf architecture does not allow exposing it easily.
    """


    def __call__(self, ua, devices):
        """
        @param ua: The user agent
        @type ua: string
        @param devices: The devices object to search
        @type devices: Devices
        @rtype: Device
        @raises pywurfl.DeviceNotFound
        """
        match = max((Levenshtein.jaro_winkler(x, ua, self.weight), x) for
                    x in devices.devuas)

        if match[0] >= self.accuracy:
            
            dev_clone = copy.copy(devices.devuas[match[1]])
            dev_clone.accuracy = match[0]
            # print "Got accuracy " + match[1] + " " + str(match[0])
            return dev_clone
        else:
            raise DeviceNotFound(ua)
        
class CustomTokenizer(Tokenizer):
    """ TODO: DO NOT USE - not implementd
    """
    
    def __call__(self, ua, devices):
        dev = Tokenizer.__call__(self, ua, devices)
        dev_clone = copy.copy(dev)
        dev.accuracy = calc_accuracy(ua, dev.devau)
        return dev
            
        
class CustomLevenshteinDistance(Algorithm):
    """
    Custom Levenshtein algo implementation which tries to guess how bad our match was.
    """

    def __call__(self, ua, devices):
        """
        @param ua: The user agent
        @type ua: string
        @param devices: The devices object to search
        @type devices: Devices
        @rtype: Device
        """

        match = min((Levenshtein.distance(ua, x), x) for x in
                    devices.devuas)
        dev = devices.devuas[match[1]]
        dev_clone = copy.copy(dev) 
        
        # Calculate accuraty following
        # 20 letter or more diffence = 0
        # 1 letter difference 0.9
        # 0 letter difference 1.0
        
        missed_chars = match[0]
        missed_chars = max(missed_chars, 20)
        
        dev_clone.accuracy = 1.0 - float(missed_chars) / 20.0
        
        return dev_clone
    
class DummyWebUserAgent(base.UserAgent):
    """
    This user agent is returned when we are unsure and want to default to a web browser.
    """
    
    def get(self, name):
        """ Get property in DeviceAtlas compatible way.

        @param name: Property name, like usableDisplayWidth
        @return: Property value, string converted to a real object

        """

        if name == "is_wireless_device":
            return False
        else:
            None