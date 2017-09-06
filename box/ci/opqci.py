from ngrokconnector import NgrokConnector
from githookmanager import GitHookManager
from gitpostlistner import GitPostListner
import logging
import json
import sys
import os

GITHUB_PORT_NUMBER = 4567

class OpqCi:
    def __init__(self, fname):
        with open(fname) as data_file:
            data = json.load(data_file)
        repo = data["repo"]
        user = data["user"]
        branch = data["branch"]
        actions = data["actions"]
        p =  user + "/" + repo + "/branch:"+ branch
        logging.basicConfig(level=logging.INFO)
        ngrok = NgrokConnector()
        try:
            tname = ngrok.getTunnelName()
            tname += "/git_push"
        except TypeError:
            logging.fatal("Could not connect to ngrok daemon")
            sys.exit(1)
        gitm = GitHookManager()
        gitm.updateHookUrlUser(repo,tname)
        self.git = GitPostListner({p : map(lambda act: lambda: os.system(act),actions)})

    def startListner(self):
        self.git.start(GITHUB_PORT_NUMBER)

def func():
    print "Hello"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Need a settings file as an argument"
    #logging.basicConfig(level=logging.INFO)
    ci = OpqCi(sys.argv[1])
    ci.startListner()
