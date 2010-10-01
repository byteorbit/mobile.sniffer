#!/bin/sh
#
# Unpack and update pywurfl database


gunzip wurfl-latest.xml.gz
../../../../../bin/zopepy  wurfl2python.py  wurfl-latest.xml 

# File too big to commit
rm wurfl-latest.xml

