import os
import sys
import csv
import yaml
import json
import requests

from datetime import datetime

sys.path.append('..')
from notifications.slack import Slack
# Disabling SSL warnings !
try:
    import requests.packages.urllib3
    requests.packages.urllib3.disable_warnings()
except:
    pass


class Nessus():
    """
    Nessus scanner APIs for automatted scan and report generation
    """
    def __init__(self):

        # colors
        self.G = '\033[92m'  # green
        self.Y = '\033[93m'  # yellow
        self.B = '\033[94m'  # blue
        self.R = '\033[91m'  # red
        self.W = '\033[0m'   # white

        path = os.path.dirname(os.path.abspath(__file__))
        with open(path + "/../config", "r") as ymlfile:
            config = yaml.load(ymlfile)
        
        self.nessus_url = config['nessus']['url']
        self.username = config['nessus']['username']
        self.password = config['nessus']['password']
        self.token = ""
        self.policy_uuid = ""
        self.policy_id = ""
        self.scan_id = 0
        self.scan_uuid = ""
        self.nessus_result = ""
        self.slack = Slack()
        return


    def login(self):
        """
        login() will login to the nessus and retrieve the token which is used in all subsequent
        requests.

        self.token    ->    Access token used for subsequent Authorization
        """
        url = self.nessus_url + "/session"
        params = {"username": self.username, "password": self.password}
        headers = {"Content-Type": "application/json"}

        req = requests.post(url, data=json.dumps(params), headers=headers, verify=False)
        self.token = json.loads(req.text)['token']
        return


    def get_folder(self):
        """
        get_folder() checks if a folder named "Red Team Arsenal" exists in the folder list where
        automatted scan will go (the ones launched by this script)
        """
        url = self.nessus_url + "/folders"
        headers = {"X-Cookie":"token=" + self.token}

        req = requests.get(url, headers=headers, verify=False)
        return


    def get_custom_uuid(self):
        """
        get_custom_uuid() function gets the UUID of custom scans using which we launch a custom
        policy based scan.

        self.policy_uuid    ->    Custom Policy UUID
        """
        url = self.nessus_url + "/editor/policy/templates"
        headers = {"X-Cookie":"token=" + self.token}

        req = requests.get(url, headers=headers, verify=False)
        policies = json.loads(req.text)
        
        for policy in policies["templates"]:
            if(policy["title"] == "Custom Scan"):
                self.policy_uuid = policy["uuid"]
                break
        return



    def get_policy_id(self):
        """
        get_policy() function gets the user defined policies of Nessus using which we can run custom 
        scans.

        self.policy_id    ->    Custom policy ID that we have created
        """
        url = self.nessus_url + "/policies"
        headers = {"X-Cookie":"token=" + self.token}

        req = requests.get(url, headers=headers, verify=False)
        scans = json.loads(req.text)

        for policy in scans["policies"]:
            if(policy["name"] == "RTA"):
                self.policy_id = policy["id"]
                break
        return


    def add_scan(self, target):
        """
        add_scan() functions add a new scan in to the list of scans which can be laucnched at a later
        point of time (or can be scheduled also).

        self.scan_id    ->    Scan ID name which is needed for scan launch
        """
        url = self.nessus_url + "/scans"
        headers = {"X-Cookie":"token=" + self.token, "Content-Type": "application/json"}
        
        targets = ", ".join(target)

        settings = {"name":"RTA_" + str(datetime.now()), "description":"Red Team Arsenal weekly Auto scan"}
        settings["text_targets"] = targets
        settings["policy_id"] = self.policy_id
        
        params = {"uuid":self.policy_uuid, "settings":settings}

        req = requests.post(url, headers=headers, data=json.dumps(params), verify=False)
        self.scan_id = json.loads(req.text)["scan"]["id"]
        return


    def launch_scan(self):
        """
        launch_scan() launches a scan which is already added via add_scan().
        """
        url = self.nessus_url + "/scans/" + str(self.scan_id) + "/launch"
        headers = {"X-Cookie":"token=" + self.token}

        req = requests.post(url, headers=headers, verify=False)
        self.scan_uuid = json.loads(req.text)["scan_uuid"]
        return


    def check_status(self):
        """
        check_status() returns the the status of the scans 
        """
        url = self.nessus_url + "/scans/"
        headers = {"X-Cookie":"token=" + self.token}

        req = requests.get(url, headers=headers, verify=False)
        response = json.loads(req.text)
        if "Invalid Credentials" in req.text:
            self.login()
            return "running"
        for scan in response["scans"]:
            if(scan["uuid"] == self.scan_uuid):
                status = scan["status"]
        return status


    def scan_results(self, filename, format='pdf'):
        """
        scan_result() returns the list of scan's overall result

        3 parts:

        1) initiate the report download
        2) Check the report status
        3) Download the report if the status is ready
        """
        # Part 1: Initiating report download
        url = self.nessus_url + "/scans/" + str(self.scan_id) + "/export"
        headers = {"X-Cookie":"token=" + self.token, "Content-Type": "application/json"}

        params = {"format": format, "chapters": "vuln_hosts_summary"}
        req = requests.post(url, headers=headers, data=json.dumps(params), verify=False)
        response = json.loads(req.text)
        export_file_id = response["file"]


        # Part 2: Checking export status
        while True:
            url = self.nessus_url + "/scans/" + str(self.scan_id) + "/export/" + str(export_file_id) + "/status"
            req = requests.get(url, headers=headers, verify=False)
            response = json.loads(req.text)
            if response["status"] == "ready":
                break

        # Part 3: Downloading the CSV report if status is ready:
        url = self.nessus_url + "/scans/" + str(self.scan_id) + "/export/" + str(export_file_id) + "/download"
        filename = filename + "." + str(format)
        req = requests.get(url, headers=headers, verify=False, stream=True)
        
        # Writing the output to a file

        with open(filename, 'wb') as fd:
            for chunk in req.iter_content(chunk_size=2000):
                fd.write(chunk)
    
        fd.close()
        return

    def slack_notify(self):
        self.scan_results('Nessus_report_file', 'csv')
        csvfile = open('Nessus_report_file.csv', 'r')
        fieldnames = ('Plugin ID', 'CVE', 'CVSS', 'Risk', 'Host', 'Protocol', 'Port', 'Name', 'Synopsis', 'Description', 'Solution', 'See Also', 'Plugin Output')
        
        # Parsing the CSV to dict
        reader = csv.DictReader( csvfile, fieldnames)

        # Consolidated report to slack
        critical = high = medium = low = ""

        for row in reader:
            if row['Risk'] == 'Critical':
                critical += row['Name'] + " (" + row['Host'] + ":" + row['Port'] + ")\n"

            if row['Risk'] == 'High':
                high += row['Name'] + " (" + row['Host'] + ":" + row['Port'] + ")\n"
                #high += "Output: " + row['Plugin Output'] + "\n"

            if row['Risk'] == 'Medium':
                medium += row['Name'] + " (" + row['Host'] + ":" + row['Port'] + ")\n"
                #medium += "Output: " + row['Plugin Output'] + "\n"

            if row['Risk'] == 'Low':
                low += row['Name'] + " (" + row['Host'] + ":" + row['Port'] + ")\n"
                #low += "Output: " + row['Plugin Output'] + "\n"


        if critical or high or medium or low:
            self.message = "[+] Nessus consolidated report: \n"

        if critical:
            print(self.R + "Critical:\n" + critical)
            self.message += "*Critical*:\n```\n" + critical + "```\n"
            self.slack.notify_slack(self.message)
            self.message = ""
        if high:
            print(self.R + "High:\n" + high)
            self.message += "*High*:\n```\n" + high + "```\n"
            self.slack.notify_slack(self.message)
            self.message = ""
        if medium:
            print(self.Y + "Medium:\n" + medium)
            self.message += "*Medium*:\n```\n" + medium + "```\n"
            self.slack.notify_slack(self.message)
            self.message = ""
        if low:
            print(self.G + "Low:\n" + low)
            self.message += "*Low*:\n```\n" + low + "```\n"
            self.slack.notify_slack(self.message)
            self.message = ""

        # cleaning up files
        os.remove('Nessus_report_file.csv')