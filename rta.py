import os
import sys
import json
import time
import socket
import requests
import argparse

from datetime import datetime
from pymongo import MongoClient

from recon.Sublist3r import sublist3r

from recon.custom import spfcheck
from recon.custom import subtakeover
from recon.custom import zonetransfer

from scanning.nessus import Nessus
from scanning.wpscan import WpScan

from recon.scraper import scraper

from notifications.slack import Slack

from Wappalyzer import Wappalyzer, WebPage


class Recon(object):
    """
    Class which deals with finding out as many subdomains and enumerate as 
    much as possible

    """

    def __init__(self):

        # colors
        self.G = '\033[92m'  # green
        self.Y = '\033[93m'  # yellow
        self.B = '\033[94m'  # blue
        self.R = '\033[91m'  # red
        self.W = '\033[0m'   # white

        # Global Class Variables
        self.subdomains = set()
        self.verified_domains = list()
        self.exposed_files = list()
        self.sub_takeover = dict()

        # MongoDB variables
        self.mongocli = MongoClient('localhost', 27017)
        self.dbname = self.mongocli['RTA']

        # Object initiation
        self.scraper = scraper.Scraper()
        self.slack = Slack()

        # Slack push notification message
        self.message = ""
        return

    ############################ Finding Subdomains ############################

    def zonetransfer(self, target):
        """
        The function checks if Zonetransfer is enabled for the target and if
        so, it will try to get all of its subdomains from it.

        Module: recon/custom/zonetransfer.py
        """
        print(self.Y + "[i] Checking for Zonetransfer")
        zoneresult = json.loads(zonetransfer.zonetransfer(target))
        
        if zoneresult["enabled"]:
            print(self.R + "[+] Zone Transfer is enabled")
            self.subdomains |= set([str(x) for x in zoneresult["list"]])
        else:
            print(self.G + "[i] Zone Transfer is not enabled\n")
        
        return

    def sublister(self, target, silent=True):
        """
        Sublist3r tool (located in recon/Sublist3r) is run against the target
        and it returns a list of subdomains.

        self.subdomains  -> List of all subdomains returned by sublist3r
        """
        self.subdomains |= set(sublist3r.main(target, 5, savefile=None,
                                              ports=None, silent=silent, verbose=False,
                                              enable_bruteforce=False, engines=None))

        # Enter the subdomains to MongoDB
        collection = self.dbname['subdomains']
        collection.create_index('domain', unique=True)
        count = self.dbname.collection.count()

        # Get the list of domains already in the DB for slack notifications
        old_subs = collection.find({}, {'domain':1, '_id':0})
        old_sub = set()
        for i in old_subs:
            old_sub.add(i['domain'])

        # New subs is the diff between old set and new one
        diff = list(self.subdomains - old_sub)

        # Slack push notification
        if diff:
            self.message = "[+] New subdomains enumerated "
            self.message += "(previous results are not included):\n```"
            # Keep 30 domains per slack message
            for i in range(len(diff)):
                self.message += diff[i].strip("\n") + ",\n"
                if (i+1) % 30 == 0:
                    self.message += "```"
                    self.slack.notify_slack(self.message)
                    if i+1 != len(diff):
                        self.message = "```"
            
            if len(diff) > 30 and len(diff) % 30 != 0:
                self.message += "```"

            if len(diff) < 30:
                self.message += "```" 
            self.slack.notify_slack(self.message)

        for domain in self.subdomains:
            try:
                data = {"id": count+1, "domain": domain, "time": datetime.now(), "parent": target}
                dataid = collection.insert(data)
                count += 1
            except Exception as e:
                pass

        return

    ############################ Verifying Subdomains ############################

    def verify(self, target):
        """
        By initiating a request, we verify if the subdomain has a webserver
        running in it based on if it gets resolved correctly or not.

        If the status is any other value than 200, the CNAME lookup is done 
        and if it points out to 3rd parties, then the details is listed.

        self.verified_domains -> list of all verified subdomains (webserver running)
        """

        # Enter the subdomains to MongoDB
        collection = self.dbname['verified_subdomains']
        collection.create_index('domain', unique=True)
        count = self.dbname.collection.count()

        print("\n" + self.Y + "[i] Verifying Subdomains and takeover options")
        for url in self.subdomains:
            cname = False
            url = url.strip("\n")
            data = {"id": count+1, "time": datetime.now(), "parent": target}
            try:
                req = requests.get("http://" + url, timeout=4, verify=False, 
                                   allow_redirects=False)
                # print "url: " + url
                self.verified_domains.append(url)
                if req.status_code != 200:
                    # Checking for subdomain takeover
                    cname = subtakeover.check_takeover(target, url)

                if cname:
                    self.sub_takeover[url] = cname
                    data.update({"cname": cname, "domain": url, "takeover": "true"})
                else:
                    data.update({"cname": "", "domain": url, "takeover": "false"})

                # push the data into MongoDB
                dataid = collection.insert(data)
                count += 1

            except Exception as e:
                continue

        if(len(self.sub_takeover) > 0):
            # Slack push notifications
            self.message = "[+] Possible subdomain takeovers"
            self.message += "(Manual verification required):\n```"
            
            print("\n" + self.Y + "[+] Possible subdomain takeovers (Manual verification required): ")
            
            for url, cname in self.sub_takeover.items():
                print(self.W + " " + url + ": " + self.R + cname)
                length = len(url)
                length = 30 - length
                self.message += url + " --> ".rjust(length) + cname + "\n"
        
            self.message += "```\n"
            self.slack.notify_slack(self.message)
        return


    def wappalyzer(self, target, verbose=False):
        """
        All verified subdomains are scanned with Wappalyzer to find out the  
        technology stack used in each of them.

        Once wappalyzer is run, it prints out all verified domains
        """
        print("\n" + self.Y + "[i] Verified and Analyzed Subdomains: \n")
        wappalyzer = Wappalyzer.latest()

        # Tech stack db which contains the tech stack of all the sub domains
        collection = self.dbname['tech_stack']
        collection.create_index('domain', unique=True)
        count = self.dbname.collection.count()

        for url in self.verified_domains:
            try:
                webpage = WebPage.new_from_url('http://' + url, verify=False)
                tech_stack = wappalyzer.analyze(webpage)
                if tech_stack and verbose:
                    print(self.G + "[i] URL: " + url)
                    print(self.B + "[i] Wappalyzer: " + 
                          str(list(tech_stack)) + "\n")

                    # Push the above data to DB
                    data = {"id": count+1, "domain": url, "time": datetime.now()}
                    data["parent"] = target
                    data['tech_stack'] = list(tech_stack)
                    dataid = collection.insert(data)
                    count += 1

            except Exception as e:
                continue
        return


    ############################ SPF Records ############################

    def spfcheck(self, target):
        """
        The function will check the number of look up needed for the SPF record
        and checks if it is greater than 10 or not.
        """
        print(self.Y + "[i] Checking for SPF records")
        resolves = spfcheck.spflookups(target)
        if(resolves > 10):
            print(self.R + "[-] SPF record lookup exceeds 10. Current value is: " + str(resolves) + "\n")
        else:
            print(self.G + "[+] SPF record lookups is good. Current value is: " + str(resolves) + "\n")
        return


    ############################ Open Source Intelligence ############################

    def scrape(self, target):
        """
        Run the scraper
        """
        print(self.Y + "[i] Scraper Results" + self.G)
        self.scraper.run_scrape(target)
        return


class Scan():
    """ This class will take care of the Active/Passive scanning """

    def __init__(self):
        # colors
        self.G = '\033[92m'  # green
        self.Y = '\033[93m'  # yellow
        self.B = '\033[94m'  # blue
        self.R = '\033[91m'  # red
        self.W = '\033[0m'   # white

        # object initialization
        self.nessus = Nessus()
        self.wpscan = WpScan()

        # MongoDB variables
        self.mongocli = MongoClient('localhost', 27017)
        self.dbname = self.mongocli['RTA']

        # Slack notification
        self.slack = Slack()
        

    def nessus_scan(self, target, filename):
        """ This function will take care of nessus scans and getting its output"""
        self.nessus.login()
        self.nessus.get_custom_uuid()
        self.nessus.get_policy_id()
        self.nessus.add_scan(list(target))
        print(self.G + "[i] Successfully added the Nessus scan")
        self.nessus.launch_scan()
        print("[i] Successfully launched the Nessus scan & waiting for the scan to complete")
        
        while True:
            time.sleep(60)
            try:
                status = self.nessus.check_status()
                if(status != "running"):
                    break
            except Exception as e:
                continue
        self.nessus.scan_results(filename)
        print(self.G + "[+] Nessus consolidated report:")
        self.nessus.slack_notify()
        return

    def wp_scan(self, parent):
        """
        Launch WpScan if the techstack used is wordpress.
        """
        collection = self.dbname['wpscan']
        collection_tech = self.dbname['tech_stack']
        count = self.dbname.collection.count()
        # collection.create_index('domain', unique=True)
        
        flag = True

        for item in collection_tech.find({'parent': parent}):
            message = ""
            if 'wordpress' in str(item['tech_stack']).lower():
                
                if flag:
                    message = "[+] *Wpscan report*: (" + item['domain'] + ")\n"
                    flag = False

                result = self.wpscan.scan(item['domain'], parent)
                data = {'id': count+1, 'domain': item['domain'], 'time': datetime.now()}
                data['version'] = result['version']['number']
                message += "Version: `" + data['version'] + "`\n"
                
                data['vulnerabilities'] = []
                data['plugins'] = {}

                message += "Wordpress core vulnerabilities: \n```\n"
                for value in result['version']['vulnerabilities']:
                    data['vulnerabilities'].append(value['title'])
                    message += value['title'] + "\n"
                message += "```\nPlugins: \n"

                for key, value in result['plugins'].iteritems():
                    if message[-1] != "\n":
                        message += "```"
                    message += "\n" + key + ": \n```"

                    for vuln in value['vulnerabilities']:
                        message += "\n"
                        try:
                            data['plugins'][key].append(vuln['title'])
                        except:
                            data['plugins'][key] = []
                            data['plugins'][key].append(vuln['title'])
                        message += vuln['title']


            # Push the above data to DB
            message += "\n```"
            print(self.W + message)
            self.slack.notify_slack(message)
            dataid = collection.insert(data)
            count += 1


def main():
    print('\033[91m' + """
              ____          _   _____                         _                              _ 
             |  _ \ ___  __| | |_   _|__  __ _ _ __ ___      / \   _ __ ___  ___ _ __   __ _| |
             | |_) / _ \/ _` |   | |/ _ \/ _` | '_ ` _ \    / _ \ | '__/ __|/ _ \ '_ \ / _` | |
             |  _ <  __/ (_| |   | |  __/ (_| | | | | | |  / ___ \| |  \__ \  __/ | | | (_| | |
             |_| \_\___|\__,_|   |_|\___|\__,_|_| |_| |_| /_/   \_\_|  |___/\___|_| |_|\__,_|_|
                                                                                                          
            """)
    
    # Initialising argument parser
    parser = argparse.ArgumentParser(description='Red Team Arsenal')
    parser.add_argument('-u', '--url', type=str, help='URL to scan')
    parser.add_argument('-v', '--verbose', action='store_true', help='enter verbose mode')
    parser.add_argument('-n', '--nessus', action='store_true', help='Run Nessus scan')
    parser.add_argument('-s', '--scraper', action='store_true', help='Run scraper based on config keywords')
    args = parser.parse_args()

    # Exit if a target is not specified
    if not args.url:
        print("No URL or IP file specified.\npython rta.py -h for help")
        exit(0)

    
    recon = Recon()
    scan = Scan()

    if args.url:
        recon.zonetransfer(args.url)
        recon.spfcheck(args.url)

        if args.verbose:
            recon.sublister(args.url, False)
        else:
            recon.sublister(args.url)

        recon.verify(args.url)
        recon.wappalyzer(args.url, args.verbose)
        # scan.wp_scan(args.url)
        
        if args.scraper:
            recon.scrape(args.url)

        if args.nessus:
            filename = "Nessus_report_" + str(datetime.now()).split('.')[0]
            scan.nessus_scan(recon.subdomains, filename)

    return


if __name__ == '__main__':
    main()
