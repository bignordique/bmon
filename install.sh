#! /bin/bash

# Not necessarily an install script.   Mostly documentation of what needs to 
# be done.   Could turn into an install script.

#sudo /usr/sbin/lighty-enable-mod accesslog
#sudo /usr/sbin/lighty-disable-mod accesslog

sudo /usr/sbin/lighty-enable-mod fastcgi

sudo ln -s /home/leith/bmon/config/lighttpd.conf /etc/lighttpd

# use Code to create the Python .venv

chmod 755 /home/leith
sudo usermod -a -G www-data leith   #to look at www-files

sudo mkdir /var/www/cgi-bin
sudo ln -s /home/leith/bmon/cgi/hw.fcgi /var/www/cgi-bin

sudo ln -s /home/leith/bmon/html/index.html /var/www/html
sudo ln -s /home/leith/bmon/html/hw_pump.html /var/www/html

sudo apt-get install telnet

sudo systemctl edit --full lighttpd
# Delete displayed contents.   Copyin contents of repository lighttpd.service
# and save.    This will create a new service file in /etc/systemd/system 
# that overrides the one in /lib/systemd/system.
# Be careful that the shebang points to the correct Python executable.
sudo systemctl daemon-reload

sudo raspi-config
# Interface options -> 1-Wire
