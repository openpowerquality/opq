FROM python:3.7-alpine

# These are mostly required for matplotlib, scipy, pandas, zmq
RUN apk --no-cache --update-cache add build-base pkgconfig freetype-dev libpng-dev gfortran openblas-dev libffi-dev openssl-dev python3-dev curl krb5-dev linux-headers zeromq-dev

WORKDIR /opq

ADD . /opq

# Some of the requirements depend on numpy to be installed first (looking at you Pandas)
RUN pip3 install --no-cache --trusted-host pypi.python.org numpy

# Then install the rest of the deps
RUN pip3 install --no-cache --trusted-host pypi.python.org -r mauka/requirements.txt

# Remove the build deps except for the python ones
#RUN apk --no-cache del build-base pkgconfig freetype-dev libpng-dev gfortran openblas-dev libffi-dev openssl-dev curl krb5-dev linux-headers zeromq-dev
