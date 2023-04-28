import csv
from datetime import date
import subprocess
import os
import socket
import pandas as pd
from constants import res,sta_res

from re import sub
import xml.etree.ElementTree as ET
import pandas as pd
from utilities.csv_to_pie import pie_chart_maker

from utilities.make_domains_list import domain_list
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import gspread
import pandas as pd


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
    sh=gc.create('port_scan'+domain+d1)
    content = open('./'+domain+'/tools/Port_scan/csv_file.csv', "r").read().encode("utf8")
    gc.import_csv(sh.id,data=content)
    sh.share('REDACTED', perm_type='user', role='writer',notify=False)
    res[domain]['Port Scan']=sh.id

def misc_csv_uploader():
    gc = gspread.service_account('./client_secret.json')
    today=date.today()
    d1 = today.strftime("%d/%m/%Y")
    sh=gc.create('port_scan_misc'+d1)
    content = open('./miscellaneous_portscan.csv', "r").read().encode("utf8")
    gc.import_csv(sh.id,data=content)
    sh.share('REDACTED', perm_type='user', role='writer',notify=False)
    sta_res['Port Scan']=sh.id

def port_scan(domain,flag,frames):
    var=[]
    cols=['subdomain','open port','service name']
    rows=[]
    df=pd.DataFrame(rows,columns=cols)
    if(flag==1):
       
        try:
            fols = domain + "/tools/Port_scan"
            path1 = os.path.join("./",fols)
            os.makedirs(path1)
        except:
            pass
        subdomains = domain_list("./"+domain+"/tools/subdomains/resolved.txt")
        for i in subdomains:
            print(i.split('/'))
            var.append(i.split('/')[-1])
            # print(type(var))
    else:
        var.append(domain)
        # print(type(var))
    
    for i in var:
        print(i)
        subprocess.run("echo "+ i +"| ./binaries/naabu -nmap-cli \'nmap -sV -oX nmap-output.xml\'", shell=True)
        print('ny')
        xmlparse=ET.parse('nmap-output.xml')
        myroot=xmlparse.getroot()
        myroot1=xmlparse.getroot()

        subdomain=""
        for element in myroot1:
            if(element.tag=='host'):
                for child in element:
                    if(child.tag=='address'):
                        subdomain=child.get('addr')
                        
        for element in myroot[4][3]:
            port_id=element.get("portid")
            for each_element in element:
                if(each_element.tag=='service'):
                    service=each_element.get("name")
            rows=[]
            rows.append({"subdomain":subdomain,"open port":port_id,"service name":service})
            df1=pd.DataFrame(rows)
            frames.append(df1)

    if(flag==1):
        df=pd.concat(frames)
        df.to_csv("./"+domain+"/tools/Port_scan/csv_file.csv")
        csv_uploader(domain)
        pie_chart_maker("./"+domain+"/tools/Port_scan/csv_file.csv", "./"+domain+"/tools/Port_scan/pie_chart.png", "./input_files/vulnerable_ports.csv")
    else:
        return frames

def port_scan_main():
    try:
        domains = domain_list("./input_files/domains.txt")
        
        flag=1
        for domain in domains:
            print(domain)
            frames=[]
            port_scan(domain,flag,frames)

        f = open("./input_files/port_scan_inp.txt", 'r')
        flag=2
        frames=[]
        cols=['subdomain','open port','service name']
        final_df=pd.DataFrame(columns=cols)
        for lines in f:
            flag=2    
            miscellaneous_df=port_scan(lines,flag,frames)
        final_df=pd.concat(frames)
        final_df.to_csv("./miscellaneous_portscan.csv")
        misc_csv_uploader()
    except Exception as e:
        print("EXCEPTION IN PORT SCAN FUNCTION:- ", str(e))
        pass
#port_scan_main()
#misc_csv_uploader()
