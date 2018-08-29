import os
import sys
import yaml
import json
import requests

from twitter import OAuth
from twitter import Twitter
from datetime import datetime

from pymongo import ASCENDING
from pymongo import DESCENDING
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


sys.path.append('../..')
from notifications.slack import Slack


class Scraper():
    """ Class which scrapes the internet to figure out any confidential data leak"""

    def __init__(self):

        # colors
        self.G = '\033[92m'  # green
        self.Y = '\033[93m'  # yellow
        self.B = '\033[94m'  # blue
        self.R = '\033[91m'  # red
        self.W = '\033[0m'   # white

        # MongoDB variables
        self.mongocli = MongoClient('localhost', 27017)
        self.dbname = self.mongocli['RTA']
        self.collection = self.dbname['scraper']
        self.collection.create_index([("url", DESCENDING), ("hostname", ASCENDING)], unique=True)

        # Config parser
        path = os.path.dirname(os.path.abspath(__file__))
        with open(path + "/../../config", "r") as ymlfile:
            config = yaml.load(ymlfile)

        # Github config
        self.github_token = config['scraper']['github_token']
        self.github_keywords = config['scraper']['github_keywords']
        self.github_url = "https://api.github.com"

        # Shodan config
        self.shodan_token = config['scraper']['shodan_token']
        self.shodan_url = "https://api.shodan.io/shodan/host/search"

        #twitter config
        self.twitter_keywords = config['scraper']['twitter_keywords']
        self.access_key = config['scraper']["twitter_access_token"]
        self.access_secret = config['scraper']["twitter_access_token_secret"]
        self.consumer_key = config['scraper']["twitter_consumer_key"]
        self.consumer_secret = config['scraper']["twitter_consumer_secret"]

        # Slack configuration
        self.slack = Slack()
        self.message = "[+] Scraper Results:\n"

        return


    def github(self):
        """
        Search the github for results based on keywords in config. This runs as 2 parts:

        1) search in code
        2) search in commits

        """
        print(self.G + "[+] Github" + self.W)
        message = "\n*Github*:\n"
        headers = {"Accept": "application/vnd.github.cloak-preview"}
        slack_flag = 0

        # Mongodb setup
        count = self.collection.count()
        
        for i in ['code', 'commits']:
            path = "/search/" + i
            url = self.github_url + path

            for search_string in self.github_keywords:
                payload = {"access_token": self.github_token, "q": search_string}
                req = requests.get(url, headers=headers, params=payload)
                
                if req.status_code == 200:
                    message = ""
                    message += "Searched String: " + search_string + "\n```\n"
                    slack_flag = flag =0
                    results = json.loads(req.text)
                    for item in results['items']:
                        try:
                            data = {"id": count+1, "source": "github", "search_string": search_string, "url": item['html_url']}
                            data['profile'] = item['repository']['full_name']
                            data['timestamp'] = datetime.now()
                            dataid = self.collection.insert(data)
                            count += 1
                            flag += 1

                            # Slack push notifications
                            message += data['url'] + "\n"
                            slack_flag += 1
                            if slack_flag > 9 and len(results['items']) - flag != 0:
                                message += "```\n"

                                if len(results['items']) - flag > 18:
                                    self.slack.notify_slack(message)
                                    message = ""

                                message += "```\n"
                                slack_flag = 0
                            # self.message += "url: " + data['url'] + " (Searched String: " + search_string + ")\n"
                        except Exception as e: 
                            #message += "```\n"
                            pass
                    message += "```\n"
                    print(message)
                    self.slack.notify_slack(message)
            break
        return


    def shodan(self, target):
        """
        Search the shodan for results regarding "example.com" domain.

        This uses the query=hostname:example.com to get the subdomains and ports which are open

        """

        message = ""
        url = self.shodan_url
        payload = {"key": self.shodan_token, "query": "hostname:" + target}

        req = requests.get(url, params=payload)
        results = json.loads(req.text)

        # MongoDB variables
        count = self.collection.count()

        for result in results['matches']:
            try:
                data = {"id": count+1, "source": "shodan", "timestamp": datetime.now()}
                data['port'] = result['port']
                data['ip_str'] = result['ip_str']
                data['hostname'] = result['hostnames']
                dataid = self.collection.insert(data)
                count += 1

                # Slack notification
                length = 38 - len(data['hostname'][0])
                message += "\nHostname: " + data['hostname'][0] + "IP: ".rjust(length) + data['ip_str']
                length = 28 - len(data['ip_str'])
                message += "Ports: ".rjust(length) + str(data['port'])

            except Exception as e:
                pass

        if message:
            print(self.G + "[+] Shodan" +self.R + message + "\n")
            self.message += "*Shodan*:\n```"
            self.message += message
            self.message += "\n```"

        return



    def twitter(self):
        """
        Keywords based search on twitter and returns the recent results based on the same

        """
        message = ""
        count = self.collection.count()

        twitter = Twitter(auth = OAuth(self.access_key, self.access_secret, self.consumer_key, self.consumer_secret))
        for keyword in self.twitter_keywords:
            query = twitter.search.tweets(q = keyword)
            for result in query['statuses']:
                try:
                    data = {"id": count+1, "source": "twitter", "timestamp": datetime.now()}
                    data['tweet'] = result['text']
                    data['name'] = result["user"]["screen_name"]
                    data['url'] = "https://twitter.com/" + data["name"] + "/status/" + str(result['id'])
                    data['search_string'] = keyword
                    try:
                        dataid = self.collection.insert(data)
                    except DuplicateKeyError as e:
                        continue
                    count += 1

                    # Slack push notification
                    length = 82 - len(data['url'])
                    message += "\nURL: " + data['url'] + " search string: ".rjust(length) + keyword

                except Exception as e:
                    print(e)
                    pass
        
        if message:
            print(self.G + "[+] Twitter" + self.B + message + self.W + "\n")
            self.message += "\n*Twitter*:\n```"
            self.message += message
            self.message += "\n```\n*Github*:\n"

        return


    def run_scrape(self, target):
        """
        Get all possible results for all the defined websites.

        """
        try:
            self.shodan(target)
        except Exception as e:
            # print("Exception occured: \n" + str(e))
            print("\033[91m" + "[+]Skipping Shodan since config file is not updated")
            pass

        try:
            self.twitter()
        except Exception as e:
            print("Exception occured: \n" + str(e))
            print("\033[91m" + "[+]Skipping Twitter since config file is not updated")
            pass

        self.slack.notify_slack(self.message)
        self.github()

        return