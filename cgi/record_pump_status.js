#!/home/pi/bmon/venv/bin/python

import logging
import cgi

pump_status_file = "/tmp/pump_status"

class record_pump_status ():

    def __init__ (self): 

        cmd = cgi.parse()['q'][0][0:20]  #truncate to 20 characters
        print(cmd)  #lighttpd generates as error is cgi generates no response

        with open(pump_status_file, "w") as file:
            file.write(cmd)

if __name__ == "__main__":

    main = record_pump_status()
