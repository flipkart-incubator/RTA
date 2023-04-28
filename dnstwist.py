import csv
import subprocess
import os
import time
import pandas as pd
import re 
from datetime import date


from phonebook_run import res
from utilities.make_domains_list import domain_list
from utilities.aquatone_screenshotter import aquatone_run

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
    sh=gc.create('Typosquating'+domain+d1)
    content = open('./'+domain+'/tools/typosquating/existing_ips.csv', "r").read().encode("utf8")
    gc.import_csv(sh.id,data=content)
    sh.share('REDACTED', perm_type='user', role='writer',notify=False)
    res[domain]["Typosquatting"]=sh.id
    
def to_csv(domain):
    cols=['Domain','Fake Domain','IP Address']
    rows=[]
    df=pd.DataFrame(rows,columns=cols)
    f=open("./" + domain + "/tools/typosquating/existing_ips.txt")
    for line in f:
        rows=[]
        line_domain=re.split(' |\n',line)
        # print(fake_domain)
        rows.append({'Domain':domain,'Fake Domain':line_domain[0],'IP Address':line_domain[-2]})
        df1=pd.DataFrame(rows)
        df=pd.concat([df,df1], ignore_index = True)
    df.to_csv("./" + domain + "/tools/typosquating/existing_ips.csv")
    # file_name=domain+'-exisiting_ips'
    csv_uploader(domain)
    # gc = gspread.service_account()
    # sh=gc.open('example.com-exisiting_ips')
    # worksheet_list = sh.worksheets()

# run the dnstwist tool on the domain
def dnswist_run(domain):
    start_time = time.time()
    subprocess.run("dnstwist " + domain + " > ./" + domain + "/tools/typosquating/all_urls.txt", shell=True)
    
    # get all the lines in the output that contain ips 
    subprocess.run("grep -Eo \"\S*\s*(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\" ./"  + domain + "/tools/typosquating/all_urls.txt > ./"  + domain + "/tools/typosquating/existing_ips.txt", shell=True) #this finds the ip and the domain
    
    # the domains which have an ip associated with them
    subprocess.run("cut -d\  -f1 ./"  + domain + "/tools/typosquating/existing_ips.txt > ./"  + domain + "/tools/typosquating/existing_domains.txt", shell=True) #this finds the domain
    print("--- time of execution ---- ", time.time() - start_time)

def dnswist_main():
    try:
        domains = domain_list("./input_files/domains.txt")
        for i in domains:
            print(i)
            directory = i
            try:
                fols = directory + "/tools/typosquating"
                path1 = os.path.join("./", fols)
                os.makedirs(path1)
            except:
                pass
            dnswist_run(i)
            
            # screentshot all the domains obtained
            aquatone_run("./"+directory+"/tools/typosquating/existing_domains.txt", "./screenshot/typosquating/"+directory)
            
            # make a csv of the output obtained which contains the ips and the domain name
            to_csv(i)
    except Exception as e:
        print("EXCEPTION IN DNSTWIST FUNCTION:- ", str(e))
        pass
