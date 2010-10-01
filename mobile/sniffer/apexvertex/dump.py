"""

    Dump Apex database as JSON.
    
    SQL magic to add missing primary key to capability table::
    
        ALTER TABLE handset_capability ADD COLUMN id MEDIUMINT NOT NULL AUTO_INCREMENT PRIMARY KEY;
        
    Needed before dumping - Django requires primary key to be able to modelize SQL.
    
    

"""

__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.fi>"
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL"
__docformat__ = "epytext"

import os, sys

os.environ["DJANGO_SETTINGS_MODULE"] = "mobile.sniffer.apexvertex.dump_settings"

from mobile.sniffer.apexvertex.models import UserAgent
from mobile.sniffer.apexvertex.sniffer import ApexVertexSniffer

def get_phone(ua):
    
    class MockRequest:
        environ = {}
        
    req = MockRequest()
    req.environ["HTTP_USER_AGENT"] = ua
    
    sniffer = ApexVertexSniffer()
    ua = sniffer.sniff(req)
    return ua
    
def create_public_dump():
    """ Create distributable sample file with less models """
    
    from django.core import serializers
    ser = serializers.get_serializer("json")
    
    # Create set of capabilities and phones which are outputted
    items = [ get_phone("NokiaN95"), get_phone("iPhone"), get_phone("Nokia6600") ]
    
    capas = []
    for ua in items:
        capas += list(ua.capability_set.all())
    
    items += capas
    
    json = serializers.serialize("json", items)
                          
    file = "public_handsets.json"
    out = open(file, "wt")       
    print >> out, json
    out.close()
    
    print "Created " + os.path.realpath(file)

if __name__ == "__main__":
    print "Has %d user agents" % UserAgent.objects.all().count()
    
    create_public_dump()
    
    from django.core.management.commands import dumpdata
    cmd = dumpdata.Command()
    data = cmd.handle("apexvertex")
        
    file = os.path.join(os.environ["HOME"], "apexvertex.json")

    out = open(file, "wt")
    print >> out, data
    out.close()
    
    print "Created:" + file
    

    
    
    
    
    
    