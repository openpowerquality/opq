import time
import requests

i = 0
while True:
    with requests.Session() as x:
        data = x.get('http://localhost:8911').json()
        msg = str(i) + ': ' + str(data['ThdPlugin'])
        print(msg)
    i += 1
    time.sleep(30)
