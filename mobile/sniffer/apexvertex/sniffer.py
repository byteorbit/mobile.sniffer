"""

    Interface compatible wrapper for Apex Vertex handset database.
    

"""

__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.fi>"
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL"
__docformat__ = "epytext"

import models

from mobile.sniffer import base

class ApexVertexSniffer(base.Sniffer):
    """ DeviceAtlas database based sniffer.
    
    DeviceAtlas database is distributed as JSON file.
    DevicetAtlas own Python API is wrapped to this generic interface.
    
    Since DeviceAtlas internal API is not redistributable, you need to download it 
    from here: http://deviceatlas.com/getAPI/python
    """
    
    def __init__(self):
        """        
        """
        
    def sniff(self, request):
        agent = self.get_user_agent(request)        
        browser = models.UserAgent.objects.determine_browser(agent)
        return browser
        