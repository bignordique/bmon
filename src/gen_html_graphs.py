#!/home/pi/bmon/venv/bin/python


import logging
import re
from time import time, sleep, strftime, localtime
from datetime import datetime

zone_logfile = "/mnt/nfsshare/zone_change"
temps_logfile = "/mnt/nfsshare/temps"
parse_zone = re.compile("^(\d+.\d+)\s+(\w+)\s+([0-1])")
trace_time_secs = 8 * 60 * 60
canvas_x = 350
x_scale = canvas_x/trace_time_secs

class gen_html_graphs ():

    def __init__ (self, name):
        self.name = name
        self.logger = logging.getLogger(__name__)
        self.now_secs = int(time())
        yesterday_secs = self.now_secs - 24*60*60
        self.yesterday_suffix = strftime(".%Y-%m-%d", localtime(yesterday_secs))

        self.start_time_secs = self.now_secs - trace_time_secs

        self.zone_info = {"lower_lake":[0, 0, 10.5, "blue"], 
                          "lower_street":[0, 0, 20.5, "red"], 
                          "shop":[0, 0, 30.5, "green"],
                          "upper_family":[0, 0, 40.5, "yellow"], 
                          "upper_hallway":[0, 0, 50.5, "magenta"],
                          "upper_bedroom":[0, 0, 60.5, "cyan"],
                          "hw_tank":[0, 0, 70.5, "purple"],
                          "boiler":[0, 0, 80.5, "azure"]}

        self.outstring = 'canvas = document.getElementById("zone_plots");'
        self.outstring += 'ctx = canvas.getContext("2d");'

        self.outstring += "ctx.lineWidth = 5;\n"
        self.outstring += 'ctx.lineCap = "butt";\n'

    def stroke_line(self, room):
        start = self.zone_info[room][0] * x_scale
        end = self.zone_info[room][1] * x_scale
        self.outstring += f'ctx.beginPath();\n'
        self.outstring += f'ctx.moveTo({start:.4f}, {self.zone_info[room][2]});\n'
        self.outstring += f'ctx.lineTo({end:.4f}, {self.zone_info[room][2]});\n'
        self.outstring += f'ctx.strokeStyle = "{self.zone_info[room][3]}";\n'
        self.outstring += f'ctx.stroke();\n'

    def gen_zones(self):
        for log_file in (zone_logfile + self.yesterday_suffix, zone_logfile):
            try: 
                f = open(log_file, "r")
            except FileNotFoundError:
                self.logger.warning(f'{self.name} file "{log_file}" not found')
            except Exception as e:
                self.logger.error(f'{e}')

            for line in f:
                mobj = parse_zone.search(line)
                if mobj is not None: 
                    trace_time = int(float(mobj.group(1))) - self.start_time_secs
                    if trace_time >= 0:
                        room = mobj.group(2)
                        if mobj.group(3) == "1":
                            self.zone_info[room][0] = trace_time
                        else:
                            self.zone_info[room][1] = trace_time
                            self.stroke_line(room)
            f.close()

        for room in self.zone_info:
            if self.zone_info[room][0] > self.zone_info[room][1]:
                self.zone_info[room][1] = trace_time_secs
                self.stroke_line(room)

        return(self.outstring)

if __name__ == "__main__":

    logging.basicConfig(format="%(asctime)s %(name)s %(module)s:%(lineno)d "+\
                               "%(levelname)s:%(message)s",
                        level=logging.DEBUG) 

    inst = gen_html_graphs("gen_html_graphs")

    print(inst.gen_zones())
