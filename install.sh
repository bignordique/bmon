#! /bin/bash

# Not necessarily an install script.   Mostly documentation of what needs to 
# be done.   Could turn into an install script.

#sudo /usr/sbin/lighty-enable-mod accesslog
#sudo /usr/sbin/lighty-disable-mod accesslog

sudo /usr/sbin/lighty-enable-mod fastcgi

sudo ln -s /home/leith/bmon/config/lighttpd.conf /etc/lighttpd
