##################
pl-pacsquery 1.0.3
##################

.. image:: https://img.shields.io/github/tag/fnndsc/pl-pacsquery.svg?style=flat-square   :target: https://github.com/FNNDSC/pl-pacsquery
.. image:: https://img.shields.io/docker/build/fnndsc/pl-pacsquery.svg?style=flat-square   :target: https://hub.docker.com/r/fnndsc/pl-pacsquery/


Abstract
========

A CUBE 'fs' plugin to query a remote PACS.

NAME
====
        pacsquery.py


SYNOPSIS
========

..code-block:: bash

        pacsquery.py    --pfdcm <PACserviceIP:port>             \\
                        [--msg <jsonMsgString>]                 \\
                        [--patientID <patientID>]               \\
                        [--PACSservice <PACSservice>]           \\
                        [--summaryKeys <keylist>]               \\
                        [--summaryFile <summaryFile>]           \\
                        [--resultFile <resultFile>]             \\
                        [--numberOfHitsFile <numberOfHitsFile>] \\
                        <outputdir>

DESCRIPTION
===========

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


RESULTS
=======

    Results from this app are typically three files in the <outputdir>.
    These are:

        o summary file of the hits, using <keyList>, <summaryFile>
        o JSON formatted results from 'pfdcm', <resultFile>
        o hit file containing number of hits, <numberOfHitsFile>

ARGS
====

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

        The name of the file in the <outputdir> to contain the results.
    
    --numberOfHitsFile <numberOfHitsFile>]

        The name of the file in the <outputdir> to contain the number of hits.

    <outputdir>

        The output directory.

Run
===
Using ``docker run``
--------------------

.. code-block:: bash

  docker run -t --rm                      \
    -v $(pwd)/output:/output              \
    fnndsc/pl-pacsquery pacsquery.py      \
    --pfdcm localhost:5015                \
    --PACSservice orthanc                 \
    --PatientID 1234567                   \
    /output
