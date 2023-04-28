from datetime import date
import os
import subprocess

import pandas as pd
from utilities.make_domains_list import domain_list
from port_scan import res

import gspread
# import pygsheets
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

def csv_uploader(domain):
    gc = gspread.service_account('./client_secret.json')
    today=date.today()
    d1 = today.strftime("%d/%m/%Y")
    sh=gc.create('gau'+domain+d1)
    content = open("./gau_op/" + domain + ".csv", "r").read().encode("utf8")
    gc.import_csv(sh.id,data=content)
    sh.share('REDACTED', perm_type='user', role='writer',notify=False)
    res[domain]["Gau"]=sh.id
    print(res)
    print("-------------------------------------------------- uploaded csv of port scan function")

def to_csv(domain):
    cols=['Domain','URLS']
    rows=[]
    df=pd.DataFrame(rows,columns=cols)
    f=open("./gau_op/" + domain + ".txt")
    for line in f:
        rows=[]
        rows.append({'Domain':domain,'URLS':line})
        df1=pd.DataFrame(rows)
        df=pd.concat([df,df1], ignore_index = True)
    df.to_csv("./gau_op/" + domain + ".csv")
    print("-------------------------------------------------- made csv of gau function")
    csv_uploader(domain)

# this function is to be run upon the various subdomains extracted. NOT ON THE DOMAINS!
def gau_main():
    try:
        domains = domain_list("./input_files/domains.txt")
        # Making a folder to keep the gau data
        try:
            path_dir5 = os.path.join("./", "gau_op/")
            os.mkdir(path_dir5)
        except:
            pass
        # run for all the domains in the list
        for domain in domains:
            subdomains = domain_list("./"+domain+"/tools/subdomains/master.txt")
            # run gau only on the subdomains of a domain
            flag = 0
            for subdomain in subdomains:
                if(flag == 0):
                    flag = 1
                    subprocess.run("./binaries/gau " + subdomain + "| tee ./gau_op/" + domain + ".txt", shell=True)
                else:
                    subprocess.run("./binaries/gau " + subdomain + "| tee -a ./gau_op/" + domain + ".txt", shell=True)
                
            to_csv(domain)
    except Exception as e:
        print("EXCEPTION IN GAU FUNCTION:- ", str(e))
        pass
