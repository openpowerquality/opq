#!/usr/bin/env python
import io
import os
import re
import sys
import json
import requests
import ipaddress
import logging
from bottle import Bottle, route, run, request, abort


class GitPostListner:
    def __init__(self, callbacks):
        self.log = logging.getLogger("GIT POST")
        self.app = Bottle()
        self.app.route(path="/git_push", method='POST', callback=lambda: self.index())
        self.callback = callbacks

    def index(self):
        if request.method != 'POST':
            return 'OK'
        logging.debug("Received webhook call from Github, fetching IP range...")
        # Store the IP address blocks that github uses for hook requests.
        logging.debug("Received webhook call from Github, fetching IP range...")
        hook_blocks = requests.get('https://api.github.com/meta').json()['hooks']

        # Check if the POST request is from github.com
        for block in hook_blocks:
            ip = ipaddress.ip_address(u'%s' % request.remote_addr)
            if ipaddress.ip_address(ip) in ipaddress.ip_network(block):
                break  # the remote_addr is within the network range of github
        else:
            abort(403)

        if request.headers.get('X-GitHub-Event') == "ping":
            return json.dumps({'msg': 'Hi!'})
        if request.headers.get('X-GitHub-Event') != "push":
            return json.dumps({'msg': "wrong event type"})

        payload = request.json
        repo_meta = {
            'name': payload['repository']['name'],
            'owner': payload['repository']['owner']['name'],
        }
        match = re.match(r"refs/heads/(?P<branch>.*)", payload['ref'])
        if match:
            repo_meta['branch'] = match.groupdict()['branch']
            actions = self.callback.get('{owner}/{name}/branch:{branch}'.format(**repo_meta), None)
        else:
            actions = self.callback.get('{owner}/{name}'.format(**repo_meta), None)
        if actions:
            for action in actions:
                logging.debug("Triggering action for " +  '{owner}/{name}/branch:{branch}'.format(**repo_meta))
                action()
        return 'OK'

    def start(self, port_number):
        server = os.environ.get('SERVER', "auto")
        #
        self.app.run(host='0.0.0.0', port=port_number, debug=True, server=server)
