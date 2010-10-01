"""
    Apex Vertex database SQL mappings and query functions.

    http://www.twinapex.com

"""

__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.fi>"
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL"
__docformat__ = "epytext"

import datetime
from django.db import models
from django.contrib import admin

# TODO: Clean up logging references
import logging
logger = logging.getLogger("ApexVertex")

class Manager(models.Manager):
    """ Manage Browser database """
    
    def get_by_user_agent(self, http_user_agent):
        """ Determine mobile browser type based on HTTP user agent string.
        
        Fuzzy matching is used. 
        
        Pieces of user agent strings are stored in the database. These pieces should be matched the longest first.        
        """
        
        if http_user_agent == None:
            return None
        
        agents = UserAgent.objects.all()
        matched_agents = []
        for agent in agents:
            if http_user_agent.find(agent.user_agent) != -1:
                matched_agents.append(agent)
        
        longest = None
        for agent in matched_agents:
            if longest == None:
                longest = agent
            elif len( agent.user_agent ) > len( longest.user_agent ):
                longest = agent
            elif len( agent.user_agent ) == len( longest.user_agent ):
                logger.debug('Got user agents with same length:' +str(agent.user_agent) +' and ' +str(longest.user_agent) )
                #TODO: how this is solved if its possible at all?
        logger.debug("Found user agent:" + str(longest))
    
        if longest:
            longest.full_user_agent = http_user_agent
    
        return longest

    def determine_browser(self, http_user_agent):    
        """ Determinate stroable Browser object.
        
        Fall back to GenericBrowser if no browser was detected.
        """
        browser = self.get_by_user_agent(http_user_agent)        
        return browser

class UserAgent(models.Model):
    """ Describe handset row in the database. 
    
    This wraps the basic properties of the mobile handset and part of its user agent string (partial match).    
    
    We have some basic functions to shortcut checks for common phone series (Nokia, iPhone).
    """
    
    class Meta:
        db_table = "handset"
        
    id = models.AutoField(primary_key=True)
    
    name = models.CharField(max_length=30)
    user_agent = models.CharField(max_length=250, db_column="useragent")
    browser = models.CharField(max_length=10)
    screen_height = models.IntegerField()
    screen_width = models.IntegerField()
    canvas_height = models.IntegerField(db_column="usable_screen_height")
    canvas_width = models.IntegerField(db_column="usable_screen_width")
    
    # Hackyish: Since we do not store the full user agent field in the database
    # it gets set here after the object has been looked up 
    full_user_agent = None
    
    objects = Manager()
        
    
    def __unicode__(self):
        return unicode(self.name) + u" " + unicode(self.user_agent)
        
    def get_tags(self):
        """ Tags describe general properties of the device. 
        
        These can be used to discriminate handset models based on their series.
        
        @return: List of strings
        """
    
        # TODO: for now, hardcoded, move to database
        tags = []
        
        # Can be None if omitted by the browser
        user_agent = str(self.full_user_agent)
                
        if "iPhone" in user_agent:
            tags.append("iphone")
            
        if ("Series60" in user_agent):
            tags.append("series60")
            
        return tags
        
    def get_effective_display_size(self):
        return [self.canvas_width, self.canvas_height]
    
    def is_iphone(self):
        """ Shortcut method to categorize iphones """
        return "iphone" in self.get_tags()
    
    def is_series_60(self):    
        """ Shortcut method to categorize Series 60 Nokia phones """
        return "series60" in self.get_tags()
    
    def is_series_60_fp1(self):
        """ Shortcut method to categorize Series 60 feature pack 1 Nokia phones """
        
        # TODO: Check WebKit version here
        
        return "series60" in self.get_tags()
    
    def has_location_support(self):
        """ Can we have location information extracted from this device somehow """
        return self.is_series_60_fp1() or self.is_iphone()
    
    def has_phonegap(self):
        """ Determines whether the phone supports PhoneGap Javascript API. 
        
        Note that we can't rely on the user agent detection on this,
        we need to perform additional check in the Javascript code.
        
        http://phonegap.pbwiki.com/Building+your+first+mobile+application
        """
        return "iphone" in self.get_tags()

    def get_capabilities(self):
        """ Get capabilities of this handset.
        
        @return: List of capability ids (integers). See Capability class.
        """
        capas = self.capability_set.all()
        return [ int(c.capability) for c in capas ]
    
    def get(self, name):
        """ Get property in DeviceAtlas compatible way. """
        
        if name == "usableDisplayWidth":
            return self.canvas_width
        elif name == "usableDisplayHeight":
            return self.canvas_height
        elif name == "stream.3gp.h263":
            caps = self.get_capabilities()
            print "Got caps:" + str(caps)
            return Capability.VIDEO_3GP in caps
        elif name == "mp4.h264.level11":
            print self.get_tags()
            return self.is_iphone() or self.is_series_60_fp1() # TODO Currently hardcoded support - will be added later

    
class UserAgentAdmin(admin.ModelAdmin):
    """ """
    search_fields = ["name","user_agent"]
    
admin.site.register(UserAgent, UserAgentAdmin)
    
class Capability(models.Model):
    """ Describe handset supported capability """
    
    class Meta:
        db_table = "handset_capability"
    
    """
       10=>"image/jpeg",
       11=>"image/gif",
       12=>"image/gif89a",
       20=>"video/3gp",
       21=>"video/rm",
       22=>"video/x-ms-wmv",
       30=>"audio/mid",
       31=>"audio/mp3",
       32=>"audio/wav",
       33=>"audio/NB-AMR",
       34=>"audio/mp4",
       35=>"audio/aac",
       1200=>"3G Network Support"
    """

    id = models.AutoField(primary_key=True)    
    handset = models.ForeignKey(UserAgent, db_column="handset")
    capability = models.IntegerField(max_length=30)
        
    IMAGE_JPEG = 10
    
    VIDEO_3GP = 20
    
