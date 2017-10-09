import json

# Returns .json file as a dict
def file_to_dict(file_name):
    try:
        with open(file_name) as opened_file:
            json_data = json.load(opened_file)
            return json_data
    except:
        return {}

# Turns http response obj into dict
def http_response_to_dict(response):
    data = json.loads(response.read().decode(response.info().get_param('charset') or 'utf-8'))
    return data
