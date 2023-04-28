import csv
from datetime import date
import os
import subprocess

import pandas as pd
from utilities.make_domains_list import domain_list
from constants import cloud_res

import gspread
import pandas as pd
import ssl
import requests
from constants import cloud_res
context = ssl.create_default_context()
Context=ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
from urllib3.exceptions import InsecureRequestWarning

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

def csv_uploader(company):
    gc = gspread.service_account('./client_secret.json')
    today=date.today()
    d1 = today.strftime("%d/%m/%Y")
    sh=gc.create('cloud_enum'+company+d1)
    content = './gcp_ip/'+company+'/'+company+'.csv'
    gc.import_csv(sh.id,data=content)
    sh.share('REDACTED', perm_type='user', role='writer',notify=False)
    cloud_res[company]=sh.id
    print(cloud_res)
    
def gcp_ip_enumeration(company,keyword):
    cols=[]
    rows=[]
    df=pd.DataFrame(rows,columns=cols)
    try:
        fols = "gcp_ip/"+company
        path1 = os.path.join("./",fols)
        os.makedirs(path1)
    except:
        pass
    subprocess.run("./cloud_enum/cloud_enum.py -t 25 -k "+keyword+" > "+"./gcp_ip/"+company+"/temp1.txt", shell=True)
    f=open('./gcp_ip/'+company+"/temp1.txt",'r')
    open_g_bucket="OPEN GOOGLE BUCKET"
    open_az_bucket="OPEN AZURE CONTAINER"
    open_am_bucket="OPEN S3 BUCKET"

    prt_g_bucket="Protected Google Bucket"
    prt_am_bucket="Protected S3 Bucket"
    col=""
    for line in f:
        if open_g_bucket in line:
            col=open_g_bucket
        if open_az_bucket in line:
            col=open_az_bucket
        if open_am_bucket in line:
            col=open_am_bucket
        if prt_g_bucket in line:
            col=prt_g_bucket
        if prt_am_bucket in line:
            col=prt_am_bucket

        if open_g_bucket in line or open_az_bucket  in line or open_am_bucket  in line or prt_g_bucket  in line or prt_am_bucket in line:
            print(line)
            res=line.split(':',1)[1]
            res1=""
            for elem in res:
                res1+=elem
            print(res1[:-3])
            rows.append({col:res1[:-5]})
            df1=pd.DataFrame(rows)
            df=pd.concat([df,df1], ignore_index = True)
    df.to_csv('./gcp_ip/'+company+'/'+company+'.csv')
    csv_uploader(company)
    print('----------csv for cloud enum--------')

def cloud_enum_main():
    try:
        domains = domain_list("./input_files/domains.txt")
        mp={}
        for company in domains:
            mp.setdefault(company.split('.')[0], []).append(company)

        for key,values in mp.items():
            count=len(values)
            input_val=key
            for values in mp[key]:
                input_val+=" -k "+values
            gcp_ip_enumeration(key,input_val)
    except Exception as e:
        print("EXCEPTION IN Cloud enum FUNCTION:- ", str(e))
        pass
#cloud_enum_main()
