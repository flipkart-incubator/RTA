import json
import os
from httplib2 import Http
from rsa import verify

import yaml

import ssl

from utilities.make_domains_list import domain_list
ssl._create_default_https_context = ssl._create_unverified_context


# this function returns the difference between the contents of two files. 
# Will be mostly used for comparing the older and newer verions of files.
def diff(old_file, new_file):
    # assuming that the new_file_path always exists
    ifExist = os.path.exists(old_file)
    if(ifExist):
        print("old files exists")
        old_set = set(domain_list(old_file))
        new_set = set(domain_list(new_file))
        return list(new_set - old_set)
    else:
        print("old file does not exist")
        return set(domain_list(new_file))

#    from sets 
def message_maker(diff_set):
    message = ''
    for i in diff_set:
        message += i+ '\n'
    return message

# from file
def make_mg_from_file(file_path):
    message = ''
    f = open(file_path, "r")
    lines = f.readlines()
    for line in lines:
        message += line
    return message

def notify_gchat(message):
    path = os.path.dirname(os.path.abspath(__file__))
    print(path)
    with open(path + "/../config", "r") as ymlfile:
        config = yaml.safe_load(ymlfile)
    try:
        gchat_url = config['googlechat']['url']
    except:
        pass
    try:
        http_obj = Http(".cache", disable_ssl_certificate_validation=True)
        message_headers = {'Content-Type': 'application/json; charset=UTF-8'}
        data = {'text': message}
        response = http_obj.request(
            uri=gchat_url,
            method='POST',
            headers=message_headers,
            body=json.dumps(data),
        )
        print(response)
    except Exception as e:
        print(e)
        pass
        
    return