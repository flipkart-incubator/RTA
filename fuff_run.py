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
from gau_run import res
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
    gc = gspread.service_account('./client_secret.json')
    today=date.today()
    d1 = today.strftime("%d/%m/%Y")
    sh=gc.create('FFUF'+domain+d1)
    content = open('./'+domain+'/tools/FFUF/csv_file.csv', "r").read().encode("utf8")
    gc.import_csv(sh.id,data=content)
    sh.share('REDACTED', perm_type='user', role='writer',notify=False)
    print("-------------------------------------------------- Uploaded csv of ffuf function for ", domain)
    res[domain]['FFUF']=sh.id
    print(res)

def to_csv(dir_name):
    cols=['Subdomain','Text','Status','Size','Words','Lines','Duration']
    rows=[]
    df=pd.DataFrame(rows,columns=cols)
    subdomain=""
    f=open('./'+dir_name+'/tools/FFUF/clean_master.txt','r')
    flag=1
    for line in f:
        if(line=='\n'):
            flag=2
        elif(flag==2):
            subdomain=line
            flag=1
        else:
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
    print("-------------------------------------------------- made csv of port scan function for ", dir_name)
    
# this function prints only one output if the number of "Lines: " clause is more thn 20 lines. Else, we print all the results in the clean_master file. 
def func(dir_name):
    print("hi5")
    f=open("./"+dir_name+"/tools/FFUF/regex_patterns.txt",'r')
    lines = f.readlines()
    count = 0
    print("hi6")
    for line in lines:
        print("hi7")
        line = line.strip()
        if(count == 0):
            subprocess.run("a=25; search=$(grep -c \""+ line + "\" "+"./"+dir_name+"/tools/FFUF/dirty_subdomain_temp.txt); if [ $search -gt $a ]; then grep -m1 \""+ line + "\" "+"./"+dir_name+"/tools/FFUF/dirty_subdomain_temp.txt > ./" +dir_name+"/tools/FFUF/clean_subdomain_temp.txt; else grep \""+ line + "\" "+"./"+ dir_name+"/tools/FFUF/dirty_subdomain_temp.txt > ./"+dir_name+"/tools/FFUF/clean_subdomain_temp.txt; fi", shell=True)
            count = 1
        else:
            subprocess.run("a=25; search=$(grep -c \""+ line + "\" "+"./"+dir_name+"/tools/FFUF/dirty_subdomain_temp.txt); if [ $search -gt $a ]; then grep -m1 \""+ line + "\" "+"./"+dir_name+"/tools/FFUF/dirty_subdomain_temp.txt >> ./" +dir_name+"/tools/FFUF/clean_subdomain_temp.txt; else grep \""+ line + "\" "+"./"+dir_name+"/tools/FFUF/dirty_subdomain_temp.txt >> ./"+dir_name+"/tools/FFUF/clean_subdomain_temp.txt; fi", shell=True)


def fuff_run(subdomains, dir_name):
    print("hi")
    # subdomains from the resolved.txt file only. (as there is https/https prefix already present)
    count = 0
    for subdomain in subdomains:
        print("hi1")
        subprocess.run("./binaries/ffuf -w ./input_files/common.txt -u " + subdomain  +"/FUZZ -r -maxtime 300 > ./"+dir_name+"/tools/FFUF/dirty_subdomain_temp1.txt", shell = True)
        # cleaning the dirty subdomin
        f2=open("./"+dir_name+"/tools/FFUF/dirty_subdomain_temp1.txt",'r')
        f1=open("./"+dir_name+"/tools/FFUF/dirty_subdomain_temp.txt",'w')
        lines = f2.readlines()
        c=0
        for line in lines:
            f1.write(line[4:-5])
            if(c%2):
                f1.write("\n")
            c+=1
        f2.close()
        f1.close()
        # subprocess.run("grep -E \"....(.+)....\" ./FFUF/dirty_subdomain_temp1.txt > ./FFUF/dirty_subdomain_temp.txt", shell=True)
        subprocess.run("grep -oE \"Lines: [0-9].*,\" ./"+dir_name+"/tools/FFUF/dirty_subdomain_temp.txt | sort -u > ./"+dir_name+"/tools/FFUF/regex_patterns.txt", shell = True)
        
        ###############
        f=open("./"+dir_name+"/tools/FFUF/dirty_subdomain_temp.txt",'r')
        lines = f.readlines()
        for line in lines:
            print(line)
            
        f=open("./"+dir_name+"/tools/FFUF/regex_patterns.txt",'r')
        lines = f.readlines()
        for line in lines:
            print(line)
        
        ###############
        
        if(count == 0):
            print("hi2")
            f = open("./"+dir_name+"/tools/FFUF/clean_master.txt", "w")
            f.write('\n')
            f.write(subdomain)
            f.write("\n")
            f.close()
            func(dir_name)
            count = 1
        else:
            print("hi3")
            f = open("./"+dir_name+"/tools/FFUF/clean_master.txt", "a")
            f.write("\n")
            f.write(subdomain)
            f.write("\n")
            f.close()
            func(dir_name)
        print("hi4")
        subprocess.run("cat "+"./"+dir_name+"/tools/FFUF/clean_subdomain_temp.txt >> ./"+dir_name+"/tools/FFUF/clean_master.txt", shell = True)


def ffuf_main():
    try:
        domains = domain_list("./input_files/domains.txt")
        for domain in domains:
            dir_name = domain
            try:
                fols = dir_name + "/tools/FFUF"
                path1 = os.path.join("./",fols)
                os.makedirs(path1)
            except:
                pass
            subdomains = domain_list("./"+dir_name+"/tools/subdomains/resolved.txt")
            fuff_run(subdomains, dir_name)
            to_csv(dir_name)
            csv_uploader(domain)
            # remove all the temporary files
            os.remove("./"+dir_name+"/tools/FFUF/clean_subdomain_temp.txt")
            os.remove("./"+dir_name+"/tools/FFUF/dirty_subdomain_temp.txt")
            os.remove("./"+dir_name+"/tools/FFUF/dirty_subdomain_temp1.txt")
            os.remove("./"+dir_name+"/tools/FFUF/regex_patterns.txt")
    except Exception as e:
        print("EXCEPTION IN FFUF FUNCTION:- ", str(e))
        pass
