import urllib.request

def install_latest(updates_endpoint, out_path):
    with open(out_path, "wb") as fout:
        resp = urllib.request.urlopen(updates_endpoint + "/latest")
        fout.write(resp.read())


