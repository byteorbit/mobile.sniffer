Introduction
------------

``mobile.sniffer`` is Python framework for abstracting mobile handset detection and feature database access.

When rendering web pages for mobile phones one must deal with varying handset features: 
different screen sizes and shapes, different supported file formats, different sets of web browser features. 
Also, the fact that you know the user is browsing on a mobile phone is most critical for building
successful mobile web user experience.

``mobile.sniffer`` provides two phase mobile phone detection (a.k.a sniffing) 

* *mobile detection* - this simply detects whether a browser is a mobile phone based or not.
  This is done in ``mobile/sniffer/detect.py`` module. This is useful to redirect to your
  visitors from a web site to a mobile site if they are using a mobile phone to arrive on your web site.
  
* *mobile handset feature extraction* - the handset database is looked for a mobile web browser
  user agent match. Since there might be version changes, local varieties, etc. in user agent 
  strings, heurestics are applied to the string matching. If a database entry is found, with
  certain match accuracy, it's records like device screen width and height are made
  available to the web server so that it can tailor HTML, image and video output suitable
  for this particular mobile phone.

Mobile detection can be done with a fast regular expression match. Mobile handset feature
extraction always requires a some sort of database of mobile phone entries and mobile.sniffer framework
provides abstraction of these databases.

Features
--------

* Easily plug-in mobile redirects to your Python based web sites

* Able to source data from multiple sniffing backends leading better handset coverage

* Automatically download, parse and cache complex RDF based WAP profiles

* Very convenient Python API designed by professionals

* Open source

* Unit test coverage

The code is Django, WSGI and Zope/Plone compatible.

Supported sniffing backends
----------------------------

* `Wurfl <http://wurfl.sourceforge.net/>`_ 

* ApexVertex. Commercially available from `mFabrik <http://mfabrik.com>`_.

* DeviceAtlas. Commercially available.

* WAP profiles. User agents post a link to their WAP profile data, which is an XML file
  and maintained by the handset manufacturer. (note: as WAP is deprecating protocol these are not supported on newer smartphones)

Installation
------------

``mobile.sniffer`` is distributed as Python egg in PyPi repository.
The usual method to install Python eggs is easy_install command.

Simple (Unix version)::

	sudo easy_install mobile.sniffer


Dependencies
============

.. note::

        Python package comes with a copy of Wurfl database which dates around the release.
        You might want to update this.

You might need to install additional libraries depending on what handset database you use

* Wurfl: `pywurlf library <http://wurfl.sourceforge.net/python/index.php>`_ and
  `python-Levenshtein <http://pypi.python.org/pypi/python-Levenshtein/>`_

* WAP profiles: Django (for database abstraction) and rdflib

* Apex Vertex: Django  (for database abstraction) 

Usage examples
--------------

There is no single standard to name properties queried from the handset database.
For legacy reasons, we use DeviceAtlas database column names (keys)
and then map them to database-dependent keys. 

Detection and redirect example
====================================

``detect_mobile_browser(user_agent)`` will return True of False
whether the HTTP request was made by a mobile phone.

Example::

        from mobile.sniffer.detect import  detect_mobile_browser
        from mobile.sniffer.utilities import get_user_agent

        # Get HTTP_USER_AGENT from HTTP request object
        ua = get_user_agent(self.request)
        if ua:
            # Apply reg
            if detect_mobile_browser(ua):
                # Redirect the visitor from a web site to a mobile site 
                pass
            else:
                # A regular web site visitor
                pass
        else:
            # User agent header is missing from HTTP request
            return False
    

Feature extraction example
===================================

This example will work out of the box with the included pywurlf database.

Example::

        try:
            from mobile.sniffer.wurlf.sniffer import WurlfSniffer
        
            # Wrapper sniffer instance
            # All start-up delay goes on this line
            sniffer = WurlfSniffer()
        except ImportError, e:
            import traceback
            traceback.print_exc()
            logger.exception(e)
            logger.error("Could not import Wurlf sniffer... add pywurfl and python-Lehvenstein to buildout.cfg eggs section")
            sniffer = None

	def sniff_request(request):
	    """
	    @param request: Request can be Django, WSGI or Zope HTTPRequest object
            """
            
            if not sniffer:
                # We failed to initialize Wurfl
                return None

	    user_agent = sniffer.sniff(request)

	    if user_agent == None:
	        # No match in the handset database,
	        return None
            else:
                return user_agent # mobile.sniffer.wurlf.sniffer.UserAgent object


        def web_or_mobile(request)
                ua = sniff_request(request)
                
                # How certain we must be about UA 
                # match to make decisions
                # float 0...1, the actual value is UA search algorithm specific
                # We use JaroWinkler as the default algorithm
                certainty_threshold = 0.7
                
                if ua.get("is_wireless_device") and ua.getCertainty() > certainty_threshold:
                        # Mobile code
                        pass
                else:
                        # Webby code
                        pass
                        
Match-making process for Wurfl
==============================

Since Wurfl is the default backend the process of finding UA record is explained more carefully

* Wurlf database is usually loaded during the start-up (slow operation) - it is possible
  to make this to use lazy initialization pattern

* The search algorithm is initialized with certain match threshold - all matches below this threshold
  will be ignored. The default search algorithm is JaroWinkler from Lehvenstein Python package.

* When the user agent is searched

        * Take in HTTP request User-Agent header
        
        * Go through all entries in database
        
        * Match this entry against incoming User-Agent using the search algorithm
        
                * First search pass is doing using exact string matches (no algorithm involved). In this 
                  case exposed certainty will be 1.1.
                
                * If there was no match in the first pass, do the second pass using the search algorithm
        
        * If match is found and threshold is exceed return this user agent record 
        
                * User agent record is retrofitted with the information how accurate the match was
                  (ua.getCertainty() method exposes this)
                  
Chained example
====================

Use all available handset information sources to accurately get device data.
Matching is done on property level - if one data source lacks the property information the next data source is tried. Finally if the handset is unknown, but it publishes WAP profile information, the profile is downloaded and analyzed and saved for further requests.

Example::

    from mobile.sniffer.chain import ChainedSniffer
    from mobile.sniffer.apexvertex.sniffer import ApexVertexSniffer
    from mobile.sniffer.wapprofile.sniffer import WAPProfileSniffer
    from mobile.sniffer.deviceatlas.sniffer import DeviceAtlasSniffer

    # Create all supported sniffers
    da = DeviceAtlasSniffer(da_api_file)
    apex = ApexVertexSniffer()
    wap = WAPProfileSniffer()

    # Preferred order of sniffers
    sniffer = ChainedSniffer([apex, da, wap])

    ua = sniffer.sniff(request) # Sniff HTTP_USER_AGENT, HTTP_PROFILE and many other fields
    property = ua.get("usableDisplayWidth") # This will look up data from all the databases in the chain

Automatic database installers
--------------------------------

Proprietary handset databases do not publicly distribute their APIs or data. 
mobile.sniffer deals with the problem by automatic installation wrappers. 
Also, these handset database APIs are not open source compatible which makes 
it further difficult to use them in open source projects. 
Instead of manually download and set up bunch of files each time 
you deploy your code on a new server, just make call to one magical Python function which 
will take care of all of this for you.

Source code
------------

Source code is available via Google Code.

* http://code.google.com/p/mobilesniffer/source/browse/#svn/trunk/mobile.sniffer

Beta software
-------------

This software is still in much development and aimed for advanced Python developers only.

Author
------

`mFabrik Research Oy <mailto:info@mfabrik.com>`_ - Python and Plone professionals for hire.

* `mFabrik web site <http://mfabrik.com>`_ 

* `mFabrik mobile site <http://mfabrik.mobi>`_ 

* `Blog <http://blog.mfabrik.com>`_

* `About Plone CMS <http://mfabrik.com/technology/technologies/content-management-cms/plone>`_ 





