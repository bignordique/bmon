Boiler Monitor

Monitor the 6 floor zones, HW tank zone and the main burner.

Boiler utilizes 24VAC as control voltage.   Optoisolators convert this to 
3.3V half wave, 60 hertz.  

Software converts this half wave into a DC like signal.   Catch the 
rising edge, start a timer.   If we catch another positive edge, restart 
timer.   If timer times out, set output to zero.

Pi pin assignments from /boot/config.txt for the one wire and optoisolated 24VAC inputs for boiler_monitor:
<ul>
<li>lower_lake 4
<li>boiler 5
<li>hw_tank 6
<li>w1-gpio gpiopin=16
<li>lower_street 17
<li>DHW disable 18
<li>upper_hallway 19
<li>w1-gpio gpiopin=20
<li>w1-gpio gpiopin=21
<li>upper_family 22
<li>w1-gpio gpiopin=23
<li>w1-gpio gpiopin=24
<li>w1-gpio gpiopin=25
<li>upper_bedroom 26
<li>shop 27
</ul>

