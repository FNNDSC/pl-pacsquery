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
import pypx

# import the Chris app superclass
from chrisapp.base import ChrisApp

# dicom settings
#
DICOM = {}
DICOM['server_ip'] = '173.48.120.248'
DICOM['server_port'] = '4242'
DICOM['called_aet'] = 'ORTHANC'
DICOM['calling_aet'] = 'CHIPS'

if 'DICOM_SERVER_IP' in os.environ:
    DICOM['server_ip'] = os.environ['DICOM_SERVER_IP']
if 'DICOM_SERVER_PORT' in os.environ:
    DICOM['server_port'] = os.environ['DICOM_SERVER_PORT']
if 'CALLING_AET' in os.environ:
    DICOM['calling_aet'] = os.environ['DICOM_CALLING_AET']
if 'CALLED_AET' in os.environ:
    DICOM['called_aet'] = os.environ['CALLED_AET']

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
    VERSION = '0.1'

    def define_parameters(self):
        """ Define parameters """
        # PACS settings
        self.add_argument(
            '--aet',
            dest='aet',
            type=str,
            default=DICOM['calling_aet'],
            optional=True,
            help='aet')
        self.add_argument(
            '--aec',
            dest='aec',
            type=str,
            default=DICOM['called_aet'],
            optional=True,
            help='aec')
        self.add_argument(
            '--serverIP',
            dest='server_ip',
            type=str,
            default=DICOM['server_ip'],
            optional=True,
            help='PACS server IP')
        self.add_argument(
            '--serverPort',
            dest='server_port',
            type=str,
            default=DICOM['server_port'],
            optional=True,
            help='PACS server port')

        # Query settings
        self.add_argument(
            '--patientID',
            dest='patient_id',
            type=str,
            default='',
            optional=True,
            help='Patient ID')
        self.add_argument(
            '--patientName',
            dest='patient_name',
            type=str,
            default='',
            optional=True,
            help='Patient name')
        self.add_argument(
            '--patientSex',
            dest='patient_sex',
            type=str,
            default='',
            optional=True,
            help='Patient sex')
        self.add_argument(
            '--studyDate',
            dest='study_date',
            type=str,
            default='',
            optional=True,
            help='Study date (YYYY/MM/DD)')
        self.add_argument(
            '--modalitiesInStudy',
            dest='modalities_in_study',
            type=str,
            default='',
            optional=True,
            help='Modalities in study')
        self.add_argument(
            '--performedStationAETitle',
            dest='performed_station_aet',
            type=str,
            default='',
            optional=True,
            help='Performed station aet')
        self.add_argument(
            '--studyDescription',
            dest='study_description',
            type=str,
            default='',
            optional=True,
            help='Study description')
        self.add_argument(
            '--seriesDescription',
            dest='series_description',
            type=str,
            default='',
            optional=True,
            help='Series Description')

    def run(self, options):
        """ Run plugin """

        # common options between all request types
        # aet
        # aec
        # ip
        # port
        pacs_settings = {
            'aet': options.aet,
            'aec': options.aec,
            'server_ip': options.server_ip,
            'server_port': options.server_port
        }

        # echo the PACS to make sure we can access it
        pacs_settings['executable'] = '/usr/bin/echoscu'

        echo = pypx.echo(pacs_settings)
        if echo['status'] == 'error':
            with open(os.path.join(options.outputdir, echo['status'] + '.txt'), 'w') as outfile:
                json.dump(echo, outfile, indent=4, sort_keys=True, separators=(',', ':'))
            return

        # find in the PACS
        # find ALL by default (studies + series + images)
        # type: all, study, series, image
        pacs_settings['executable'] = '/usr/bin/findscu'

        first_patient_id = options.patient_id.split(',')[0]

        # query parameters
        query_settings = {
            'PatientID': first_patient_id,
            'PatientName': options.patient_name,
            'PatientSex': options.patient_sex,
            'StudyDate': options.study_date,
            'ModalitiesInStudy': options.modalities_in_study,
            'PerformedStationAETitle': options.performed_station_aet,
            'StudyDescription': options.study_description,
            'SeriesDescription': options.series_description
        }

        # python 3.5 is required!
        find = pypx.find({**pacs_settings, **query_settings})
        with open(os.path.join(options.outputdir, find['status'] + '.txt'), 'w') as outfile:
            json.dump(find, outfile, indent=4, sort_keys=True, separators=(',', ':'))

        return json.dumps(find)

# ENTRYPOINT
if __name__ == "__main__":
    app = PacsQueryApp()
    app.launch()
