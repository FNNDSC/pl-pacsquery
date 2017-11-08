#!/usr/bin/env python3
#                                                            _
#
# (c) 2016 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#

str_version = "1.0.4"

str_name = """
    NAME

        pacsquery.py
"""
str_synposis = """

    SYNOPSIS

        pacsquery.py    --pfdcm <PACserviceIP:port>             \\
                        [--version]                             \\
                        [--msg <jsonMsgString>]                 \\
                        [--patientID <patientID>]               \\
                        [--PACSservice <PACSservice>]           \\
                        [--summaryKeys <keylist>]               \\
                        [--summaryFile <summaryFile>]           \\
                        [--resultFile <resultFile>]             \\
                        [--numberOfHitsFile <numberOfHitsFile>] \\
                        <outputdir>
"""
str_description = """

    DESCRIPTION

    'pacsquery.py' is a "FeedStarter" (FS) ChrisApp plugin that is used
    to query a PACS and start a new Feed.

    Importantly, this app does *not* actually talk to a PACS directly;
    instead it interacts with an intermediary service, typically 'pfdcm'.
    This intermediary service actually connects to a PACS and performs
    queries, which it returns to this app.

    Thus, it is important to understand that this app does not need 
    specific details on the PACS IP, port, AETITLE, etc. All of this
    information is managed by 'pfdcm'. This does mean of course, that
    'pfdcm' needs to be intantiated correctly. Please see the 'pfdcm'
    github wiki for specific instructions. 

    Note though that it is possible to pass to this app a 'pfdcm' 
    compliant message string using the [--msg <jsonMsgString>]. This
    <jsonMsgString> can be used to set 'pfdcm' internal lookup and 
    add new PACS entries. This <jsonMsgString> can also be used to 
    perform a query.

    However, most often, the simplest mechanism of query will be through
    the '--patientID' and 'PACSservice' flags.

    Finally, the <outputdir> positional argument is MANDATORY and defines
    the output directory (or relative dir when called through the
    CHRIS API) for result tables/files.
"""
str_results = """

    RESULTS

    Results from this app are typically three files in the <outputdir>.
    These are:

        o summary file of the hits, using <keyList>, <summaryFile>
        o JSON formatted results from 'pfdcm', <resultFile>
        o hit file containing number of hits, <numberOfHitsFile>
"""
str_args = """

    ARGS

    --pfdcm <PACserviceIP:port> 

        The IP and port specifier of the 'pfdcm' service. 

    --msg <jsonMsgString>]    

        A 'pfdcm' conforming message string. If sent to this app,
        the message string is passed through unaltered to 'pfdcm'.
        This allows for setting up internals of 'pfdcm' and/or
        doing queries and interactions directly. 

        USE WITH CARE.

    --patientID <patientID>] 

        The <patientID> string to query.

    --PACSservice <PACSservice>] 

        The "name" of the PACS to query within 'pfdcm'. This is 
        used to look up the PACS IP, port, AETitle, etc.

    --summaryKeys <keylist>]
    
        A comma separated list of 'keys' to include in the 
        summary report. Typically:

        PatientID,PatientAge,StudyDescription,StudyInstanceUID,SeriesDescription,SeriesInstanceUID,NumberOfSeriesRelatedInstances

    --summaryFile <summaryFile>] 

        The name of the file in the <outputdir> to contain the summary report.

    --resultFile <resultFile>]

        The name of the file in the <outputdir> to contain the results.Misc utilities for FNNDSC python repos
    
    --numberOfHitsFile <numberOfHitsFile>]

        The name of the file in the <outputdir> to contain the number of hits.

    <outputdir>

        The output directory.

"""

import os
import sys
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
    '''
    AUTHORS = 'FNNDSC (dev@babyMRI.org)'
    SELFPATH = os.path.dirname(os.path.abspath(__file__))
    SELFEXEC = os.path.basename(__file__)
    EXECSHELL = 'python3'
    TITLE = 'Pacs Query'
    CATEGORY = ''
    TYPE = 'fs'
    DESCRIPTION = 'An app to query a PACS using an intermediary REST service.'
    DOCUMENTATION = 'http://wiki'
    LICENSE = 'Opensource (MIT)'
    VERSION = '0.99'

    # Fill out this with key-value output descriptive info (such as an output file path
    # relative to the output dir) that you want to save to the output meta file when
    # called with the --saveoutputmeta flag
    OUTPUT_META_DICT = {}

    def __init__(self, *args, **kwargs):
        ChrisApp.__init__(self, *args, **kwargs)

        self.__name__           = 'PacsQueryApp'

        # Debugging control
        self.b_useDebug         = False
        self.str_debugFile      = '/dev/null'
        self.b_quiet            = True
        self.dp                 = pfmisc.debug(    
                                            verbosity   = 0,
                                            level       = -1,
                                            within      = self.__name__
                                            )
        self.pp                 = pprint.PrettyPrinter(indent=4)

        # Output dir
        self.str_outputDir      = ''

        # Service and payload vars
        self.str_pfdcm          = ''
        self.str_msg            = ''
        self.d_msg              = {}

        # Alternate, simplified CLI flags
        self.str_patientID      = ''
        self.str_PACSservice    = ''

        # Control
        self.b_canRun           = False

        # Summary report
        self.b_summaryReport    = False
        self.str_summaryKeys    = ''
        self.l_summaryKeys      = []
        self.str_summaryFile    = ''

        # Result report
        self.str_resultFile     = ''
       
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
            help        = 'The actual complete JSON message to send to the Q/R intermediary service.')
        self.add_argument(
            '--PatientID',
            dest        = 'str_patientID',
            type        = str,
            default     = '',
            optional    = True,
            help        = 'The PatientID to query.')
        self.add_argument(
            '--PACSservice',
            dest        = 'str_PACSservice',
            type        = str,
            default     = 'orthanc',
            optional    = True,
            help        = 'The PACS service to use. Note this a key to a lookup in "pfdcm".')
        self.add_argument(
            '--summaryKeys',
            dest        = 'str_summaryKeys',
            type        = str,
            default     = '',
            optional    = True,
            help        = 'If specified, generate a summary report based on a comma separated key list.')
        self.add_argument(
            '--summaryFile',
            dest        = 'str_summaryFile',
            type        = str,
            default     = '',
            optional    = True,
            help        = 'If specified, save (overwrite) a summary report to passed file (in outputdir).')
        self.add_argument(
            '--numberOfHitsFile',
            dest        = 'str_numberOfHitsFile',
            type        = str,
            default     = '',
            optional    = True,
            help        = 'If specified, save (overwrite) the number of hits (in outputdir).')
        self.add_argument(
            '--resultFile',
            dest        = 'str_resultFile',
            type        = str,
            default     = '',
            optional    = True,
            help        = 'If specified, save (overwrite) all the hits to the passed file (in outputdir).')
        self.add_argument(
            '--man',
            dest        = 'str_man',
            type        = str,
            default     = '',
            optional    = True,
            help        = 'If specified, print help on the passed key entry. Use "entries" for all key list')
        self.add_argument(
            '--pfurlQuiet',
            dest        = 'b_pfurlQuiet',
            type        = bool,
            default     = False,
            action      = 'store_true',
            optional    = True,
            help        = 'Silence pfurl noise.'),
        self.add_argument(
            '--version',
            dest        = 'b_version',
            type        = bool,
            default     = False,
            action      = 'store_true',
            optional    = True,
            help        = 'Show .')

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

    def man_get(self):
        """
        return a simple man/usage paragraph.
        """

        d_ret = {
            "man":  str_name + str_synposis + str_description + str_results + str_args,
            "synopsis":     str_synposis,
            "description":  str_description,
            "results":      str_results,
            "args":         str_args,
            "overview": """
            """,
            "callingSyntax1": """
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
            """,
            "callingSyntax2": """
                python3 pacsquery.py    --pfdcm ${HOST_IP}:5015         \\
                                        --PatientID LILLA-9731          \\
                                        --PACSservice orthanc
            """,
            "callingSyntax3": """
                python3 pacsquery.py    --pfdcm ${HOST_IP}:5015         \\
                                        --PatientID LILLA-9731          \\
                                        --PACSservice orthanc           \\
                                        --pfurlQuiet                    \\
                                        --summaryKeys "PatientID,PatientAge,StudyDescription,StudyInstanceUID,SeriesDescription,SeriesInstanceUID,NumberOfSeriesRelatedInstances" \\
                                        --summaryFile summary.txt       \\
                                        --resultFile results.json       \\
                                        --numberOfHitsFile hits.txt     \\
                                        /tmp
            """
        }

        return d_ret

    def numberOfHitsReport_process(self, *args, **kwargs):
        """
        Save number of hits
        """
        str_hitsFile    = ''
        hits            = 0
        for k,v in kwargs.items():
            if k == 'hitsFile':     str_hitsFile    = v
            if k == 'hits':         hits            = v

        if len(str_hitsFile):
            str_FQhitsFile    = os.path.join(self.str_outputDir, str_hitsFile)
            self.dp.qprint('Saving number of hits to %s' % str_FQhitsFile )
            f = open(str_FQhitsFile, 'w')
            f.write('%d' % hits)
            f.close()

    def dataReport_process(self, *args, **kwargs):
        """
        Process data report based on the return from the query.
        """

        d_results       = {}
        for k,v in kwargs.items():
            if k == 'resultFile':   self.str_resultFile     = v
            if k == 'results':      d_results               = v

        if len(self.str_resultFile):
            str_FQresultFile    = os.path.join(self.str_outputDir, self.str_resultFile)
            self.dp.qprint('Saving data results to %s' % str_FQresultFile )
            f = open(str_FQresultFile, 'w')
            js_results  = json.dumps(d_results, sort_keys = True, indent = 4)
            f.write('%s' % js_results)
            f.close()

    def summaryReport_process(self, *args, **kwargs):
        """
        Generate a summary report based on CLI specs
        """

        l_data                  = []
        self.str_summaryKeys    = ''
        for k,v in kwargs.items():
            if k == 'summaryKeys':  self.str_summaryKeys    = v
            if k == 'summaryFile':  self.str_summaryFile    = v
            if k == 'data':         l_data                  = v
        
        str_report      = ''
        l_summaryKeys   = self.str_summaryKeys.split(',')

        if len(l_data):
            # Header
            for key in l_summaryKeys:
                str_report  = str_report + "%-60s\t" % key

            # Body
            for entry in l_data:
                str_report  = str_report + "\n"
                for key in l_summaryKeys:
                    str_report  = str_report + "%-60s\t" % (entry[key]['value'])

        if len(self.str_summaryFile):
            str_FQsummaryFile   = os.path.join(self.str_outputDir, self.str_summaryFile) 
            self.dp.qprint('Saving summary to %s' % str_FQsummaryFile )
            f = open(str_FQsummaryFile, 'w')
            f.write(str_report)
            f.close()

    def manPage_checkAndShow(self, options):
        """
        Check if the user wants inline help. If so, present requested help

        Return a bool based on check.
        """

        ret = False
        if len(options.str_man):
            ret = True
            d_man = self.man_get()
            if options.str_man in d_man:
                str_help    = d_man[options.str_man]
                print(str_help)
            if options.str_man == 'entries':
                print(d_man.keys())

        return ret

    def directMessage_checkAndConstruct(self, options):
        """
        Checks if user specified a direct message to the 'pfdcm' service, 
        and if so, construct the message.

        Return True/False accordingly
        """

        ret = False
        if len(options.str_msg):
            ret = True
            self.str_msg        = options.str_msg
            try:
                self.d_msg      = json.loads(self.str_msg)
                self.b_canRun   = True
            except:
                self.b_canRun   = False
        return ret

    def queryMessage_checkAndConstruct(self, options):
        """
        Checks if user specified a query from a pattern of command line flags,
        and if so, construct the message.

        Return True/False accordingly
        """

        if len(options.str_patientID) and len(options.str_PACSservice):
            self.str_patientID      = options.str_patientID
            self.str_PACSservice    = options.str_PACSservice
            self.d_msg  = {
                'action':   'PACSinteract',
                'meta': {
                    'do':   'query',
                    'on': {
                        'PatientID': self.str_patientID
                    },
                    "PACS": self.str_PACSservice
                }
            }
            self.b_canRun   = True

    def outputFiles_generate(self, options, hits, d_ret, l_data):
        """
        Check and generate output files.
        """
        if len(options.str_numberOfHitsFile):
            self.numberOfHitsReport_process(
                                        hits        = hits,
                                        hitsFile    = options.str_numberOfHitsFile
                                        )

        if len(options.str_resultFile):
            self.dataReport_process     (    
                                        results     = d_ret,
                                        resultFile  = options.str_resultFile
                                        )

        if len(options.str_summaryKeys):
            self.summaryReport_process  ( 
                                        data        = l_data,
                                        summaryKeys = options.str_summaryKeys,
                                        summaryFile = options.str_summaryFile
                                        )
       

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """

        d_ret                   = {
            'status': False
        }
        self.b_pfurlQuiet       = options.b_pfurlQuiet
        self.str_outputDir      = options.outputdir

        if options.b_version:
            print(str_version)

        if not self.manPage_checkAndShow(options) and not options.b_version:
            if len(options.str_pfdcm):
                self.str_pfdcm      = options.str_pfdcm
                if not self.directMessage_checkAndConstruct(options):
                    self.queryMessage_checkAndConstruct(options)

                if self.b_canRun:
                    d_ret   = self.service_call(msg = self.d_msg)
                    l_data  = d_ret['query']['data']
                    hits    = len(l_data) 
                    self.dp.qprint('Query returned %d study hits' % hits)

                    self.outputFiles_generate(options, hits, d_ret, l_data)

        return d_ret

# ENTRYPOINT
if __name__ == "__main__":
    app = PacsQueryApp()
    app.launch()
