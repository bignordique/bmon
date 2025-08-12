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
# Make sure the shebang ponits to the correct Python executable.
sudo ln -s /home/leith/bmon/cgi/hw.fcgi /var/www/cgi-bin
sudo ln -s /home/leith/bmon/cgi/gen_html_graphs.py /var/www/cgi-bin/gen_html_graphs.py  #not working yet though???

sudo ln -s /home/leith/bmon/html/index.html /var/www/html
sudo ln -s /home/leith/bmon/html/hw_pump.html /var/www/html
sudo ln -s /home/leith/bmon/html/Chart.js /var/www/html
sudo ln -s /home/leith/bmon/html/images/steam_icon.png /var/www/html/images/steam_icon.png

sudo apt-get install telnet

sudo systemctl edit --full lighttpd
# Delete displayed contents.   Copyin contents of repository lighttpd.service
# and save.    This will create a new service file in /etc/systemd/system 
# that overrides the one in /lib/systemd/system.
# Be careful that the shebang points to the correct Python executable.
sudo systemctl daemon-reload

# modify /boot/firmware/config.txt to define 1-wire pins.   Do not use
# preferences -> interfaces to enable 1-wire.   This assume GPIO4 is
# a 1-wire and will conflict with the boiler monitor stuff.

sudo ln -s /home/leith/bmon/daemon/lighttpd.service /etc/systemd/system/lighttpd.service 
sudo ln -s /home/leith/bmon/daemon/boiler_monitor.service /etc/systemd/system/boiler_monitor.service
sudo ln -s /home/leith/bmon/daemon/rd_w1_temps.service /etc/systemd/system/rd_w1_temps.service
sudo systemctl enable boiler_monitor
sudo systemctl enable rd_w1_temps


