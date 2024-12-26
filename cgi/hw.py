#!/home/pi/bmon/venv/bin/python

from hw_daemon import hw_daemon
import logging
import json

class process_request():

    def __init__ (self):
        self.daemon = hw_daemon()
        self.logger = logging.getLogger(__name__)

    def doit(self, environ, start_response):
 
        request_body_size = int(environ.get('CONTENT_LENGTH' ,0))
        request_body = environ['wsgi.input'].read(request_body_size)
        request_decoded = json.loads(request_body)

        self.logger.debug(request_body)

        wsgi_err_handle = environ["wsgi.errors"]
#        wsgi_err_handle.write(f'Its howdy dowdy time!\n')

        start_response('200 OK', [('Content-Type', 'text/plain')])
        if request_decoded["button"] == "pump" or request_decoded["button"] == "alexa": 
            return[json.dumps(self.daemon.set_get_pump(int(request_decoded["value"])))]
        elif request_decoded["button"] == "vacay_days":
            return[json.dumps(self.daemon.set_get_vacay(int(request_decoded["value"])))]
        if request_decoded["button"] == "alexa": 
            return[json.dumps(self.daemon.set_get_alexa(int(request_decoded["value"])))]

        self.logger.error(f'No match on request_decoded:" {request_decoded}\n')
        return[json.dumps({})]

if __name__ == "__main__":

    import os
    import sys

    logging.basicConfig(format="%(asctime)s %(name)s %(module)s:%(lineno)d %(levelname)s:\n"+
                        "    %(message)s")

    process = process_request()

# Instantiating process_request has the side effect of clearing the dhw_disable_bit.
    if "--clear_dhw_disable" in sys.argv:
        logfile = "/var/log/lighttpd/hw_daemon.log"
        from logging.handlers import RotatingFileHandler
        rot_handler = RotatingFileHandler(logfile, maxBytes=30000, backupCount=5)
        logging.getLogger("dhw_disable").addHandler(rot_handler)
        logging.getLogger("dhw_disable").setLevel(logging.DEBUG)
        process.daemon.dhw_disable_inst.report_dhw()
        exit()

    def test_response(stuff, more_stuff):
        print(f'{stuff} {more_stuff}\n')

    environ = {'CONTENT_LENGTH': '10', 'QUERY_STRING': 'a=b&c=d', 'REQUEST_URI': '/hw.fcgi?a=b&c=d', 'REDIRECT_STATUS': '200',\
         'SCRIPT_NAME': '/hw.fcgi', 'SCRIPT_FILENAME': '/var/www/html/hw/hw.fcgi', 'DOCUMENT_ROOT': '/var/www/html/hw', 'REQUEST_METHOD': 'GET',\
         'SERVER_PROTOCOL': 'HTTP/2.0', 'SERVER_SOFTWARE': 'lighttpd/1.4.59', 'GATEWAY_INTERFACE': 'CGI/1.1', 'REQUEST_SCHEME': 'https',\
         'HTTPS': 'on', 'SERVER_PORT': '443', 'SERVER_ADDR': '192.168.1.55', 'SERVER_NAME': 'hw.bignordique.com', 'REMOTE_ADDR': '192.168.1.53', \
         'REMOTE_PORT': '50284', 'HTTP_HOST': 'hw.bignordique.com', 'HTTP_USER_AGENT': 'curl/7.64.0', 'HTTP_ACCEPT': '*/*', \
         'SSL_PROTOCOL': 'TLSv1.3', 'SSL_CIPHER': 'TLS_AES_256_GCM_SHA384', 'SSL_CIPHER_USEKEYSIZE': '256', 'SSL_CIPHER_ALGKEYSIZE': '256',\
         'wsgi.version': (1, 0), 'wsgi.input': 'flup.server.fcgi_base.InputStream object at 0xb5cad0b8>', \
         'wsgi.errors': 'flup.server.fcgi_base.OutputStream object at 0xb5cad0a0', 'wsgi.multithread': True, 'wsgi.multiprocess': False, \
         'wsgi.run_once': False, 'wsgi.url_scheme': 'https', 'PATH_INFO': ''}

    def submit_it(json_stuff):
        with open("wsgi.input", "w") as f:
            f.write(json.dumps(json_stuff))
        environ['CONTENT_LENGTH'] = os.path.getsize("wsgi.input")
        environ['wsgi.input'] = open("wsgi.input", "r")
        environ['wsgi.errors'] = open("wsgi.error", "w")
        print(process.doit(environ, test_response))
        environ['wsgi.input'].close()
        environ['wsgi.errors'].close()

    submit_it({"button":"pump","value":"15"})
    submit_it({"button":"vacay_days","value":"1"})
    submit_it({"button":"vacay_days","value":"-1"})
    submit_it({"button":"poop","value":"1"})




