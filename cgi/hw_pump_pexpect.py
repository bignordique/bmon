#!/home/pi/bmon/venv/bin/python

# Rather annoyingly, the exact code that worked on the Zynq does not work on the PI.
# Two problems... sendline seems to need a \r at the end of a string for the APC to see it and,
# apparently the Zynq/Petalinux platform generates an exception for EOF and RaspberryPI OS returns
# an empty string.   Cripes.

import pexpect

class pump_pexpect():

    # The stuff below are just the expected patterns.
    eof_timeout = [pexpect.EOF, pexpect.TIMEOUT]
    user_name = ['User Name : '] + eof_timeout
    password = ['Password  : '] + eof_timeout
    control_console = '-+ Control Console -+.*> '
    device_manager = '-+ Device Manager -+.*> '
    outlet_1 = '-+ Outlet 1 -+.*> '
    control_outlet_1 = '-+ Control Outlet 1 -+.*> '
    immediate_YES = 'Immediate .* to cancel : '
    successfully_continue = '.* successfully .* to continue...'
    logfile = "/var/log/lighttpd/pump_command.log"

    def __init__(self): pass
    
    def pump_command(self, next_state):
#        self.logger.debug(f'hw pump pexpect {next_state}')
        log_file = open(self.logfile, 'w')
        run_once = True
    
        while run_once:
            run_once = False
        
            pexpt_inst = pexpect.spawn ('telnet 192.168.1.13', encoding='utf-8')
            pexpt_inst.logfile = log_file

            ii = pexpt_inst.expect(self.user_name)
            if ii != 0 : break
            pexpt_inst.sendline('apc\r')

            ii = pexpt_inst.expect(self.password)
            if ii != 0 : break
            pexpt_inst.sendline('apc\r')

            ii = pexpt_inst.expect(self.control_console)
            if ii != 0 : break
            # select device manager
            pexpt_inst.sendline('1\r')

            ii = pexpt_inst.expect(self.device_manager)
            if ii != 0 : break
            # select outlet 1
            pexpt_inst.sendline('1\r')

            ii = pexpt_inst.expect(self.outlet_1)
            if ii != 0 : break
            # select action
            pexpt_inst.sendline('1\r')

            ii = pexpt_inst.expect(self.control_outlet_1)
            if ii != 0 : break
            # turn on or off as directed
            if next_state == "on":pexpt_inst.sendline('1\r')
            if next_state == "off":pexpt_inst.sendline('2\r')

            ii = pexpt_inst.expect(self.immediate_YES)
            if ii != 0 : break
            # confirm action
            pexpt_inst.sendline('YES\r')

            ii = pexpt_inst.expect(self.successfully_continue)
            if ii != 0 : break
            # enter to continue
            pexpt_inst.sendline('\r')

            # 3 escapes        
            ii = pexpt_inst.expect(self.control_outlet_1)
            if ii != 0 : break
            pexpt_inst.sendline('\x1b')

            ii = pexpt_inst.expect(self.outlet_1)
            if ii != 0 : break
            pexpt_inst.sendline('\x1b')

            ii = pexpt_inst.expect(self.device_manager)
            if ii != 0 : break
            pexpt_inst.sendline('\x1b')

            ii = pexpt_inst.expect(self.control_console)
            if ii != 0 : break
            # 4 to exit
            pexpt_inst.sendline('4\r')

        log_file.close()
        return(ii)

if __name__ == "__main__":
    p = pump_pexpect()
    ii = p.pump_command("on")
    print(ii)


