import csv
from datetime import date
import os
import subprocess
import pandas as pd
import re
from utilities.make_domains_list import domain_list
from utilities.aquatone_screenshotter import aquatone_run

import gspread
# import pygsheets
import pandas as pd
import ssl
from constants import res
ssl._create_default_https_context = ssl._create_unverified_context

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
    print("work6")
    gc = gspread.service_account()
    today=date.today()
    d1 = today.strftime("%d/%m/%Y")
    sh=gc.create('FFUF'+domain+d1)
    print("work7")
    content = open('./'+domain+'/tools/FFUF/csv_file.csv', "r").read().encode("utf8")
    gc.import_csv(sh.id,data=content)
    res[domain]={'FFUF':sh.id}

def to_csv(dir_name):
    print("work")
    cols=['Subdomain','Text','Status','Size','Words','Lines','Duration']
    rows=[]
    df=pd.DataFrame(rows,columns=cols)
    subdomain=""
    f=open('./'+dir_name+'/tools/FFUF/clean_master.txt','r')
    flag=1
    print("work1")
    for line in f:
        if(line=='\n'):
            print("work3")
            flag=2
        elif(flag==2):
            print("work4")
            subdomain=line
            flag=1
        else:
            print("work5")
            text=(line.split(' ')[0])
            s_idx=line.find('[')
            e_idx=line.index(']')
            data=line[s_idx:e_idx]
            x=re.split(': |,',data)
            rows=[]
            rows.append({'Subdomain':subdomain,'Text':text,'Status':x[1],'Size':x[3],'Words':x[5],'Lines':x[7],'Duration':x[9]})
            df1=pd.DataFrame(rows)
            df=pd.concat([df,df1], ignore_index = True)
    df.to_csv("./"+dir_name+"/tools/FFUF/csv_file.csv")
    
to_csv("example.com")