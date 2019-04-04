FROM python:3.7-stretch

COPY . /health

WORKDIR /health

RUN pip3 install -r requirements.txt

CMD ["python3", "-u", "health.py"]
