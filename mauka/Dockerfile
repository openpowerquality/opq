FROM python:3.7-stretch

WORKDIR /mauka

ADD . /mauka

RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

# Health interface
EXPOSE 8911

# CLI interface
EXPOSE 12000

CMD ["python3", "opq_mauka.py", "config.json"]