#                                                            _
# Pacs query app
#
# (c) 2016 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#



import os
import json
import pprint

import pypx
import pfurl
import pfmisc
import pudb

# import the Chris app superclass
from chrisapp.base import ChrisApp

class PacsQueryApp(ChrisApp):
    '''
    Create file out.txt witht the directory listing of the directory
    given by the --dir argument.
    '''
    AUTHORS = 'FNNDSC (dev@babyMRI.org)'
    SELFPATH = os.path.dirname(os.path.abspath(__file__))
    SELFEXEC = os.path.basename(__file__)
    EXECSHELL = 'python3'
    TITLE = 'Pacs Query'
    CATEGORY = ''
    TYPE = 'fs'
    DESCRIPTION = 'An app to find data of interest on the PACS'
    DOCUMENTATION = 'http://wiki'
    LICENSE = 'Opensource (MIT)'
    VERSION = '0.99'

    # Fill out this with key-value output descriptive info (such as an output file path
    # relative to the output dir) that you want to save to the output meta file when
    # called with the --saveoutputmeta flag
    OUTPUT_META_DICT = {}

    def __init__(self, *args, **kwargs):
        ChrisApp.__init__(self, *args, **kwargs)

        self.__name__       = 'PacsQueryApp'

        # Debugging control
        self.b_useDebug     = False
        self.str_debugFile  = '/dev/null'
        self.b_quiet        = True
        self.dp             = pfmisc.debug(    
                                            verbosity   = 0,
                                            level       = -1,
                                            within      = self.__name__
                                            )
        self.pp             = pprint.PrettyPrinter(indent=4)

        # Service and payload vars
        self.str_pfdcm      = ''
        self.str_msg        = ''
        self.d_msg          = {}

        # Control
        self.b_canRun       = False
       
    def define_parameters(self):
        """
        Define the CLI arguments accepted by this plugin app.
        """

        # The space of input parameters is very straightforward
        #   1. The IP:port of the pfdcm service
        #   2. A 'msg' type string / dictionary to send to the service.

        # PACS settings
        self.add_argument(
            '--pfdcm',
            dest        = 'str_pfdcm',
            type        = str,
            default     = '',
            optional    = True,
            help        = 'The PACS Q/R intermediary service IP:port.')
        self.add_argument(
            '--msg',
            dest        = 'str_msg',
            type        = str,
            default     = '',
            optional    = True,
            help        = 'The actual message to send to the Q/R intermediary service.')
        self.add_argument(
            '--man',
            dest        = 'b_man',
            type        = bool,
            default     = False,
            action      = 'store_true',
            optional    = True,
            help        = 'Return a JSON formatted man/help paragraph.')
        self.add_argument(
            '--pfurlQuiet',
            dest        = 'b_pfurlQuiet',
            type        = bool,
            default     = False,
            action      = 'store_true',
            optional    = True,
            help        = 'Silence pfurl noise.')

    def df_print(self, adict):
        """
        Return a nicely formatted string representation of a dictionary
        """
        return self.pp.pformat(adict).strip()

    def service_call(self, *args, **kwargs):

        d_msg   = {}
        for k, v in kwargs.items():
            if k == 'msg':  d_msg   = v

        serviceCall = pfurl.Pfurl(
            msg                     = json.dumps(d_msg),
            http                    = self.str_pfdcm,
            verb                    = 'POST',
            b_raw                   = True,
            b_quiet                 = self.b_pfurlQuiet,
            b_httpResponseBodyParse = True,
            jsonwrapper             = 'payload',
            debugFile               = self.str_debugFile,
            useDebug                = self.b_useDebug
        )
        
        self.dp.qprint('Sending d_msg =\n %s' % self.df_print(d_msg))
        d_response      = json.loads(serviceCall())
        return d_response

    def man_show(self):
        """
        return a simple man/usage paragraph.
        """

        d_ret = {
            "help": """
                python3 pacsquery.py --pfdcm ${HOST_IP}:5015 --msg \
                '{  
                    "action": "PACSinteract",
                    "meta": 
                        {
                            "do":  "query",
                            "on" : 
                            {
                                "PatientID": "LILLA-9731"
                            },
                            "PACS" : "orthanc"
                        }
                }' /tmp
            """
        }

        return d_ret

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """

        d_ret                   = {}
        self.b_pfurlQuiet       = options.b_pfurlQuiet

        if options.b_man:
            d_ret = self.man_show()

        if len(options.str_msg) and len(options.str_pfdcm) and not options.b_man:
            self.str_msg        = options.str_msg
            self.str_pfdcm      = options.str_pfdcm
            try:
                self.d_msg      = json.loads(self.str_msg)
                self.b_canRun   = True
            except:
                self.b_canRun   = False

        if self.b_canRun:
            d_ret = self.service_call(msg = self.d_msg)

        print(self.df_print(d_ret))
        return d_ret

# ENTRYPOINT
if __name__ == "__main__":
    app = PacsQueryApp()
    app.launch()
