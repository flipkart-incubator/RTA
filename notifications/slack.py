import os
import json
import yaml
import requests


class Slack():
    """
    Class for pushing realtime notifications to slack channel.
    
    """
    def __init__(self):
        path = os.path.dirname(os.path.abspath(__file__))
        with open(path + "/../config", "r") as ymlfile:
            config = yaml.load(ymlfile)

        try:
            self.slack_url = config['slack']['url']
        except:
            pass

        return

    def notify_slack(self, message):
        try:
            data = {'text': message}
            req = requests.post(self.slack_url, data=json.dumps(data))
        except:
            pass
            
        return