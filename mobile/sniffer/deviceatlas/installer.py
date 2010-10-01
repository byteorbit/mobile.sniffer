"""
    DeviceAtlas API and data installation automatizer.

"""
import os, sys

from mobile.sniffer import base

__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.fi>"
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL"
__docformat__ = "epytext"

class DAInstaller:
    """ Automatically download DeviceAtlas API bundle and extract.
        
        DeviceAtlas Python API files are downloaded from 
        and installed to ${your home folder}/da_distribution.
        This is to keep proprietary files away from your own 
        (potentially open source) source tree.
            
        zc.testbrowser class is used to mimic the real web browser.
        
        To install zope.testbrowser, type:
        
            easy_install zope.testbrowser
        
        You might or might not want to do this, since Zope dependencies are quite heavy.
        
    """
    
    def __init__(self, username, password, path=None):
        """
        
        @param username: DeviceAtlas username
        @param password: DeviceAtlas password        
        @param path: Path to install API and database files or None to use ~/da_distribution. Path is added to PYTHONPATH.    
        """
        

        try:
            from zope.testbrowser.browser import Browser
        except ImportError:
            raise
            raise RuntimeError("zope.testbrowser must be installed to automatize DeviceAtlas downloads")

        self.browser = Browser()
        
        if not path:
            path = os.path.abspath(os.path.join(os.getenv("HOME"), "da_distribution"))
                       
        self.path = path
        
        # Wrap things away from Python namespace
        self.api_path = os.path.join(path, "da_api")
        
        if not os.path.exists(self.path):
            os.makedirs(self.path)
            os.makedirs(self.api_path)
        
        if not path in sys.path:
            # Include autodownload folder in Python import
            sys.path.append(self.path)
        
        self.fname = "da.zip"
        self.json_file = "json.zip"
        self.raw_json = os.path.join(self.path, "data.json") # Unzipped json database  
        
        self.username = username
        self.password = password
        

        self.login_url = "http://deviceatlas.com"
        self.api_url = url="http://deviceatlas.com/getAPI/python"
        
        
    def login(self):
        """
        """
        self.browser.open(self.login_url)
        
        if "Signed in as" in self.browser.contents:
            return # already logged in
        
        field = self.browser.getControl(name="name")
        field.value = self.username

        field = self.browser.getControl(name="pass")
        field.value = self.password
        
        submit = self.browser.getControl("Go")
        submit.click()
        
        if not "http://deviceatlas.com/user" in self.browser.url:
            raise RuntimeError("Could not log in to deviceatlas.com with username " + self.username)
            #print self.browser.url
            #print self.browser.headers
            #print self.browser.contents
                
    def need_download(self):
        """
        
        @return: True if zip download needed
        """
        if not os.path.exists(os.path.join(self.path, self.fname)):
            return True
        
        return False
    
    def need_unzip(self):
        """
        @return: True if zip extract needed
        """
        if not os.path.exists(os.path.join(self.api_path, "api.py")):
            return True
        
        return False
        
    def download_zip(self):
        import urllib2
        
        self.browser.open("http://deviceatlas.com/getAPI/python")
        
        assert self.browser.headers["Content-Type"] == "application/zip" # Check that we fetch the correct file
                
        assert len(self.browser.contents) > 0, "Could not download da.zip API distribution"
        
        o = open(os.path.join(self.path, self.fname), "wb")
        o.write(self.browser.contents)
        o.close()
            
    def unzip_file_into_dir(self, file, dir, override_name=None):
        import zipfile
        
        if not os.path.exists(dir):
            os.mkdir(dir)
        
        zfobj = zipfile.ZipFile(file)
        for name in zfobj.namelist():
            if name.endswith('/'):
                os.mkdir(os.path.join(dir, name))
            else:
                
                if override_name:
                    # Set extracted file name
                    fname = override_name
                else:
                    fname = name
                
                outfile = open(os.path.join(dir, fname), 'wb')
                outfile.write(zfobj.read(name))
                outfile.close()
                
    def need_database(self):
        if not os.path.exists(self.raw_json):
            return True
        
        return False
        
        
    def download_database(self):
            
        self.browser.open("http://deviceatlas.com")
        
        self.browser.getLink("My account").click()
                
        # Assume Community ZIP link
        self.browser.getLink(url="/zip", index=0).click()
        
        # Check that we fetch the correct file
        assert self.browser.headers["Content-Type"] == "application/zip", "Assume zip content:" + str(self.browser.headers)
        
        o = open(os.path.join(self.path, self.json_file), "wb")
        o.write(self.browser.contents)
        o.close()
            
                                        
    def proceed(self):
        """ Download & unzip DA Python API files if needed.
        
        @return: Path to Downloaded DeviceAtlas JSON data file
        """
                
        if self.need_download():            
            self.login()            
            self.download_zip()
        
        if self.need_unzip():
            self.unzip_file_into_dir(os.path.join(self.path, self.fname), self.api_path)
            
            # create __init__.py to mark the module
            f = open(os.path.join(self.api_path, "__init__.py"), "wt")
            f.write("# This package is automatically generated by DAAPIInstaller")
            f.close()
            
            
        if self.need_database():
            self.login()            
            self.download_database()
            self.unzip_file_into_dir(os.path.join(self.path, self.json_file), self.path, "data.json")
        

        return self.raw_json
                    
                    
