###############
pl-pacsquery
###############

.. image:: https://img.shields.io/github/tag/fnndsc/pl-pacsquery.svg?style=flat-square   :target: https://github.com/FNNDSC/pl-pacsquery
.. image:: https://img.shields.io/docker/build/fnndsc/pl-pacsquery.svg?style=flat-square   :target: https://hub.docker.com/r/fnndsc/pl-pacsquery/


Abstract
========

A CUBE 'fs' plugin to query a remote PACS.

Preconditions
=============

-


Run
===
Using ``docker run``
--------------------

.. code-block:: bash

  docker run -t --rm \
    -v $(pwd)/output:/output \
    fnndsc/pl-pacsquery pacsquery.py \
    --aet CHIPS --aec ORTHANC \
    --serverIP 192.168.1.40 --serverPort 4242 \
    /output
