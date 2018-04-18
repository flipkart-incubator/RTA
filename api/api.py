import os
import sys
import json
import yaml
import requests

from flask import abort
from flask import Flask
from flask import request
from flask import jsonify
from flask import Response
from flask import make_response
from flask import send_from_directory

from functools import wraps
from pymongo import MongoClient

sys.path.append('..')

from scanning.nessus import Nessus


app = Flask(__name__)

# Reading config
path = os.path.dirname(os.path.abspath(__file__))
with open(path + "/../config", "r") as ymlfile:
    config = yaml.load(ymlfile)

# MongoDB connection
mongocli = MongoClient('localhost', 27017)
dbname = mongocli['RTA']


# Nessus class initialization
nessus = Nessus()

# 401 Authorization handler
@app.errorhandler(401)
def not_found(error):
    return make_response(jsonify({'error': 'UnAuthorized'}), 404)

# Checking Authentication header
def auth_check():
    uuid = config["api"]["token"]
    try:
        user_uuid = request.headers.get('X-RTA-UUID')
    except:
        abort(401)

    if user_uuid != uuid:
        abort(401)
    return

################################### Welcome ###################################

# Returns a welcome message
@app.route('/api/', methods=['GET'])
def api_root():
    auth_check()
    message = {"message": "Welcome to Red Team Arsenal API!"}
    return jsonify(message)


################################### Subdomains ###################################

# Returns the list of all subdomains despite the parent
@app.route('/api/subdomains/', methods=['GET'])
def subdomains():
    auth_check()
    results = dbname.subdomains.find({})
    sub_domains = []
    for result in results:
        data = {}
        data['id'] = result['id']
        data['subdomain'] = result['domain']
        data['parent'] = result['parent']
        sub_domains.append(data)

    return jsonify(sub_domains)


# Returns the list of all subdomains of a particular domain
@app.route('/api/subdomains/<parent>/', methods=['GET'])
def parent_subdomains(parent):
    auth_check()
    print parent
    results = dbname.subdomains.find({ 'parent': parent })
    sub_domains = []
    for result in results:
        data = {}
        data['id'] = result['id']
        data['subdomain'] = result['domain']
        data['parent'] = result['parent']
        sub_domains.append(data)

    return jsonify(sub_domains)


# Returns the list of all verified subdomains
@app.route('/api/subdomains/<parent>/verified/', methods=['GET'])
def verified_subdomains(parent):
    auth_check()
    results = dbname.verified_subdomains.find({ 'parent': parent })
    sub_domains = []
    for result in results:
        data = {}
        data['domain'] = result['domain']
        data['id'] = result['id']
        sub_domains.append(data)

    return jsonify(sub_domains)


# Return the tech stack used by a particular domain
@app.route('/api/subdomains/techstack/<domain>/', methods=['GET'])
def techstack(domain):
    auth_check()
    results = dbname.tech_stack.find({ 'domain': domain })
    sub_domains = []
    for result in results:
        data = {}
        data['techstack'] = result['tech_stack']
        data['domain'] = result['domain']
        sub_domains.append(data)

    return jsonify(sub_domains)


################################### Exposed Files ###################################

# Returns the list of exposed files on a specific domain
@app.route('/api/exposedfiles/<domain>/', methods=['GET'])
def exposed_files(domain):
    auth_check()
    results = dbname.verified_subdomains.find({ 'domain': domain })
    sub_domains = []
    for result in results:
        data = {}
        data['exposedfiles'] = result['exposed_files']
        data['id'] = result['id']
        sub_domains.append(data)

    return jsonify(sub_domains)


# Returns the list of exposed files on all subdomains of a parent
@app.route('/api/exposedfiles/<parent>/all/', methods=['GET'])
def exposed_files_parent(parent):
    auth_check()
    results = dbname.verified_subdomains.find({ 'parent': parent })
    sub_domains = []
    for result in results:
        data = {}
        data['id'] = result['id']
        data['exposedfiles'] = result['exposed_files']
        
    sub_domains.append(data)

    return jsonify(sub_domains)


################################### Scrapper ###################################

# TODO: API's to return scraper results

################################### Nessus #####################################
@app.route('/api/nessus/report/<format>', methods=['GET'])
def nessus_report(format):
    """
    3 parts:

    1) Get the latest completed scan id
    2) initiate the report download
    3) Check the report status
    4) Download the report if the status is ready
    """
    auth_check()
    nessus.login()

    # Part 1: Get the latest completed scan id
    url = nessus.nessus_url + "/scans"
    headers = {"X-Cookie":"token=" + nessus.token, "Content-Type": "application/json"}

    req = requests.get(url, headers=headers, verify=False)
    status = json.loads(req.text)['scans'][0]['status']

    if(status == "running"):
        scan_id = json.loads(req.text)['scans'][1]['id']
    else:
        scan_id = json.loads(req.text)['scans'][0]['id']

    # Part 2: Initiate report download
    params = {"format": format, "chapters": "vuln_hosts_summary"}
    url = nessus.nessus_url + "/scans/" + str(scan_id) + "/export"
    
    req = requests.post(url, headers=headers, data=json.dumps(params), verify=False)
    response = json.loads(req.text)
    export_file_id = response["file"]


    # Part 3: Checking export status
    while True:
        url = nessus.nessus_url + "/scans/" + str(scan_id) + "/export/" + str(export_file_id) + "/status"
        req = requests.get(url, headers=headers, verify=False)
        response = json.loads(req.text)
        if response["status"] == "ready":
            break

    
    # Part 3: Downloading the CSV report if status is ready:
    url = nessus.nessus_url + "/scans/" + str(scan_id) + "/export/" + str(export_file_id) + "/download"
    filename = "downloads/nessus_report.pdf"
    req = requests.get(url, headers=headers, verify=False, stream=True)
    
    # Writing the output to a file
    with open(filename, 'wb') as fd:
        for chunk in req.iter_content(chunk_size=2000):
            fd.write(chunk)

    fd.close()

    return send_from_directory('downloads', 'nessus_report.pdf', as_attachment=True)
    


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8082, debug=False);

