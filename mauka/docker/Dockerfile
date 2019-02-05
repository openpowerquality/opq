FROM python:alpine3.7

# These are mostly required for matplotlib, scipy, and pandas
RUN apk --no-cache --update-cache add build-base pkgconfig freetype-dev libpng-dev gfortran openblas-dev

WORKDIR /opq

ADD . /opq

# Some of the requirements depend on numpy to be installed first (looking at you Pandas)
RUN pip3 install --no-cache --trusted-host pypi.python.org numpy
# Then install the rest of the deps
RUN pip3 install --no-cache --trusted-host pypi.python.org -r mauka/requirements.txt

# Health interface
EXPOSE 8911

# CLI interface
EXPOSE 12000

# ZMQ triggering interface
EXPOSE 9881

# ZMQ event interface
EXPOSE 9899

# Mauka pub/sub interfaces
EXPOSE 9882
EXPOSE 9883

# Makai push interface
EXPOSE 9884

CMD ["python3", "mauka/opq_mauka.py", "mauka/config.json"]
