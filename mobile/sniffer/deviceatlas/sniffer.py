"""

    Interface compatible wrapper for DeviceAtlas.
    
    Work around DeviceAtlas Python API ugliness:
    
        - It exists in global Python namespace, colliding with all other api.fi files
        
        - It is not easily distributable dependency in open source projects
        
        - JSON data is not real JSON but just strings (PHP "coders" should learn programming)
        
        - etc.
        
    This module wraps the API and provides automatic download & install utility for it.

    http://www.twinapex.com

"""

import os, sys

from mobile.sniffer import base

__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.fi>"
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL"
__docformat__ = "epytext"

class DeviceAtlasSniffer(base.Sniffer):
    """ DeviceAtlas database based sniffer.
    
    DeviceAtlas database is distributed as JSON file.
    DevicetAtlas own Python API is wrapped to this generic interface.
    
    Since DeviceAtlas internal API is not redistributable, you need to download it 
    from here: http://deviceatlas.com/getAPI/python
    """
    
    def __init__(self, database_file):
        """
        
        @param database_file: Path to DeviceAtlas JSON drop in
        """
        
        # Delayed import since 
        
        from da_api import api as da
        
        self.da_api = da.DaApi()    
        self.da_tree = self.da_api.getTreeFromFile(database_file)
        
    def sniff(self, request):
        """ Look up handset from DeviceAtlas database using HTTP_USER_AGENT as a key """
        agent = self.get_user_agent(request)
        
        if not agent:
            return None
        
        properties = self.da_api.getProperties(self.da_tree, agent)
        if properties:
            return UserAgent(properties)
        else:
            return None        

class UserAgent(base.UserAgent):
    """ DeviceAtlas JSON user agent record wrapper.
    """
    
    def __init__(self, properties):
        
        # internal DA properties object
        self.properties = properties
    
    def sanify_property(self, value):
        """ Since DeviceAtlas data is all strings, try to guess the right Python primitive
        """
        try:
            return int(value)
        except ValueError:
            pass
        
        return value
    
    def get(self, name):
        """ Get property in DeviceAtlas compatible way.
        
        @param name: Property name, like usableDisplayWidth
        @return: Property value, string converted to a real object
        """
        val = self.properties.get(name, None)
        if val == None:
            return None
        
        return self.sanify_property(val)
