FROM python:3.7-stretch

WORKDIR /mauka

ADD . /mauka

RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 8911

CMD ["python3", "opq_mauka.py", "config.json"]