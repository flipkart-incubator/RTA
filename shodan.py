import csv
import datetime
import json
import os
import time
import ssl
import pandas as pd
import requests

from utilities.make_domains_list import domain_list
from constants import sta_res
from dnstwist import res
ssl._create_default_https_context = ssl._create_unverified_context

import gspread
import pandas as pd
import ssl

import requests
context = ssl.create_default_context()
Context=ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
from urllib3.exceptions import InsecureRequestWarning

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

def misc_csv_uploader():
    gc = gspread.service_account('./client_secret.json')
    today=datetime.date.today()
    d1 = today.strftime("%d/%m/%Y")
    sh=gc.create('shodan_misc'+d1)
    content = open('./miscellaneous.csv', "r").read().encode("utf8")
    gc.import_csv(sh.id,data=content)
    sh.share('REDACTED', perm_type='user', role='writer')
    sta_res['Shodan_Misc']=sh.id

def csv_uploader(domain):
    gc = gspread.service_account('./client_secret.json')
    today=datetime.date.today()
    d1 = today.strftime("%d/%m/%Y")
    sh=gc.create('shodan'+domain+d1)
    content = open('./'+domain+'/tools/shodan/csv_file.csv', "r").read().encode("utf8")
    gc.import_csv(sh.id,data=content)
    sh.share('REDACTED', perm_type='user', role='writer')
    res[domain]["Shodan"]=sh.id

def shodan(target,flag):
    """
        Search the shodan for results regarding "example.com" domain.

        This uses the query=hostname:example.com to get the subdomains and ports which are open

        """

    message = ""
    url = "https://api.shodan.io/shodan/host/search"
    payload = {"key": "REDACTED", "query": "hostname:" + target}

    req = requests.get(url, params=payload, verify=False)
    results = json.loads(req.text)
    count = 0
    cols=['port','ip_str','hostname']
    df=pd.DataFrame(columns=cols)
    for result in results['matches']:
        data = {}
        data['port'] = result['port']
        data['ip_str'] = result['ip_str']
        data['hostname'] = result['hostnames']
        print(data)
        count += 1
        rows=[]
        rows.append(data)
        df1=pd.DataFrame(rows)
        df=pd.concat([df,df1], ignore_index = True)
    if(flag==1):
        df.to_csv("./"+target+"/tools/shodan/csv_file.csv")
    else:
        return df


def shodan_main():
    domains = domain_list("./input_files/domains.txt")
    for domain in domains:
        
        try:
            fols = domain + "/tools/shodan"
            path1 = os.path.join("./",fols)
            os.makedirs(path1)
        except:
            pass
        flag=1
        shodan(domain,flag)
        csv_uploader(domain)

    f = open("./input_files/shodan_inp.txt", 'r')
    flag=2
    cols=['port','ip_str','hostname']
    final_df=pd.DataFrame(columns=cols)
    for lines in f:
        miscellaneous_df=shodan(lines,flag=2)
        final_df=pd.concat([final_df,miscellaneous_df],ignore_index=True)
    final_df.to_csv("./miscellaneous.csv")
    misc_csv_uploader()
"""Input acn be given from text file.
test this for IP
test for hostname also
Only company name as input
"""
