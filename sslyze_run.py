# the full output
# to the check TLS<1.3
# vulnerable or not

import csv
from datetime import date
import os
import subprocess
from fuff_run import res
from utilities.make_domains_list import domain_list
import time
import re
import pandas as pd


from utilities.make_domains_list import domain_list
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

def vulnerability_csv_uploader(domain):
    gc = gspread.service_account('./client_secret.json')
    today=date.today()
    d1 = today.strftime("%d/%m/%Y")
    sh=gc.create('ssl-vulnerability'+domain+d1)    
    content = open('./'+domain+'/tools/SSL/vulnerability.csv', "r").read().encode("utf8")
    gc.import_csv(sh.id,data=content)
    sh.share('REDACTED', perm_type='user', role='writer',notify=False)
    res[domain]['SSL scan vul']=sh.id
    print(res)
    
def protocols_csv_uploader(domain):
    gc = gspread.service_account('./client_secret.json')
    today=date.today()
    d1 = today.strftime("%d/%m/%Y")
    sh=gc.create('ssl-protocol-vul'+domain+d1)    
    content = open('./'+domain+'/tools/SSL/vulnerable_protocols.csv', "r").read().encode("utf8")
    gc.import_csv(sh.id,data=content)
    sh.share('REDACTED', perm_type='user', role='writer',notify=False)
    res[domain]['SSL scan proto']=sh.id
    print(res)

def check_protocols(subdomain, checker,domain):
    text_file=open('./'+domain+'/tools/SSL/temp.txt','r')
    if(checker == 0):
        f = open('./'+domain+'/tools/SSL/vulnerable_protocols.txt','w')
    else:
        f = open('./'+domain+'/tools/SSL/vulnerable_protocols.txt','a')
    f.write(subdomain+'\n')
    data=text_file.read()
    flag=0
    result = re.finditer(r"\*( SSL | TLS )(.)*[\n](.)*\.",data)
    for m in result:
        res=m.group()
        if((res.find('the server rejected')==-1) and (res.find('1.0')!=-1 or res.find('1.1')!=-1 or res.find('SSL')!=-1)):
                if(flag==0):
                    flag=1
                #         
                f.write('       '+res[2:9]+'\n')
    if(flag==0):
        f.write('       '+'No protocol error.\n')
    f.close()
    text_file.close()


def sslyze_run(subdomains,domain):
    start_time = time.time()
    flag =0
    for subdomain in subdomains:
        subprocess.run("python3 -m sslyze " + subdomain + " > "+"./"+domain+"/tools/SSL/temp.txt", shell=True)
        if(flag == 0):
            subprocess.run("cat ./"+domain+"/tools/SSL/temp.txt > ./"+domain+"/tools/SSL/full_output.txt", shell=True)
            subprocess.run("echo \"" + subdomain + "\" > ./"+domain+"/tools/SSL/vulnerability.txt", shell=True)
            subprocess.run("if search=$(grep \"VULNERABLE - \" ./"+domain+"/tools/SSL/temp.txt); then echo \"$search\" >> ./"+domain+"/tools/SSL/vulnerability.txt; else echo \"       No vulnerabilities found!\" >> ./"+domain+"/tools/SSL/vulnerability.txt; fi", shell=True)            
            check_protocols(subdomain,flag,domain)
            flag = 1
        else:
            subprocess.run("cat ./"+domain+"/tools/SSL/temp.txt >> ./"+domain+"/tools/SSL/full_output.txt", shell=True)
            subprocess.run("echo \"" + subdomain + "\" >> ./"+domain+"/tools/SSL/vulnerability.txt", shell=True)
            subprocess.run("if search=$(grep \"VULNERABLE - \" ./"+domain+"/tools/SSL/temp.txt); then echo \"$search\" >> ./"+domain+"/tools/SSL/vulnerability.txt; else echo \"       No vulnerabilities found!\" >> ./"+domain+"/tools/SSL/vulnerability.txt; fi", shell=True)
            check_protocols(subdomain,flag,domain)
    os.remove("./"+domain+"/tools/SSL/temp.txt")
    print("---------------------- time of execution", time.time() - start_time, " seconds -------------------- ")
        

def vulnerability_to_csv(domain):
    rows=[]
    df=pd.DataFrame(rows)
    f = open('./'+domain+'/tools/SSL/vulnerability.txt','r')
    str='No vulnerabilities found!'
    for line in f:
        if(line[0:7]!='       '):
            url=line
        elif(str not in line):
            rows.append({'Subdomain':url,'Vulnerability':line})
            df1=pd.DataFrame(rows)
            df=pd.concat([df,df1], ignore_index = True)
    df.to_csv('./'+domain+'/tools/SSL/vulnerability.csv')
    print('---------------csv created for vul-----------')
    
def protocols_to_csv(domain):
    cols=[]
    rows=[]
    df=pd.DataFrame(rows,columns=cols)
    f = open('./'+domain+'/tools/SSL/vulnerable_protocols.txt','r')
    for line in f:
        if(line[0:7]!='       '):
            url=line
        elif(line[0:7]=='       ' and len(line)!=26):
            rows.append({line:url})
            df1=pd.DataFrame(rows)
            df=pd.concat([df,df1], ignore_index = True)
    df.to_csv('./'+domain+'/tools/SSL/vulnerable_protocols.csv')
    print('---------------csv created for vul proto-----------')
    
def sslyse_main():
    try:
        domains = domain_list("./input_files/domains.txt")

        for i in domains:
            directory=i
            subdomains = domain_list("./"+directory+"/tools/subdomains/master.txt")
            try:
                fols = directory + "/tools/SSL"
                path1 = os.path.join("./",fols)
                os.makedirs(path1)
            except:
                pass
            domain=i
            
            sslyze_run(subdomains = subdomains, domain = domain)
            protocols_to_csv(domain)
            protocols_csv_uploader(domain)
            vulnerability_to_csv(domain)
            vulnerability_csv_uploader(domain)
    except Exception as e:
        print("EXCEPTION IN SSLYSE FUNCTION:- ", str(e))
        pass
    
