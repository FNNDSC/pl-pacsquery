# Docker file for the pacsquery

FROM fnndsc/ubuntu-python3:latest
MAINTAINER fnndsc "dev@babymri.org"

ENV APPROOT="/usr/src/pacsquery"  VERSION="0.1"
COPY ["pacsquery", "${APPROOT}"]
COPY ["requirements.txt", "${APPROOT}"]

WORKDIR $APPROOT

RUN apt-get update \
  && apt-get install dcmtk imagemagick\
  && pip install -r requirements.txt

CMD ["pacsquery.py", "--json"]