FROM python:3.7-slim-stretch

RUN apt-get update -y       \
    && apt-get install -y   \
           gcc              \
           python3-dev

WORKDIR /build

ADD build /build

# Some of the requirements depend on numpy to be installed first (looking at you Pandas)
RUN pip3 install --no-cache --trusted-host pypi.python.org numpy \
    && pip3 install --no-cache --trusted-host pypi.python.org -r mauka/requirements.txt

# Cleanup
RUN apt-get purge -y            \
        gcc                     \
        python3-dev             \
    && apt-get autoremove -y    \
    && rm -rf /var/lib/apt/lists/*

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

CMD ["python3", "mauka/opq_mauka.py"]
