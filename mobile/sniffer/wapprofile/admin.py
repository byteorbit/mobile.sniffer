"""

    Django web admin interface mappings for WAP profile data.

"""

__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.fi>"
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL"
__docformat__ = "epytext"

from django.contrib import admin

import models

class WAPProfile(admin.ModelAdmin):    
    pass

admin.site.register(models.WAPPRofile, WAPProfile)
    
