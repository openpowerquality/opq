from bottle import route, run
import sys
sys.path.append("../util")
import json_util

@route('/updates/<file_name>', method='GET')
def get_latest_update(file_name):
    latest_updates = json_util.file_to_dict(file_name)
    return latest_updates

run(host='localhost', port=8080, debug=True)
