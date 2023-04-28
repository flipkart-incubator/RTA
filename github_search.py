import csv
from datetime import date
import json
import os
import sys
import time
import requests
from termcolor import colored
from port_scan import sta_res
import yaml
import pandas as pd

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

def csv_uploader():
    gc = gspread.service_account('./client_secret.json')
    today=date.today()
    d1 = today.strftime("%d/%m/%Y")
    sh=gc.create('github'+d1)
    content = open("./git.csv", "r").read().encode("utf8")
    gc.import_csv(sh.id,data=content)
    sh.share('REDACTED', perm_type='user', role='writer',notify=False)
    sta_res['Github']=sh.id
    print(sta_res)

def to_csv():
    cols=['source','search_string','url']
    rows=[]
    df=pd.DataFrame(rows,columns=cols)
    f=open("github_op.txt")
    for line in f:
        str=line.split(',')[1:4]
        src=str[0].split(':')[1][2:-1]
        search_str=str[1].split(':')[1][2:-1]
        url=str[2].split(':')[2][2:-2]
        rows=[]
        rows.append({'source':src,'search_string':search_str,'url':url})
        df1=pd.DataFrame(rows)
        df=pd.concat([df,df1], ignore_index = True)
    df.to_csv('git.csv')
    print('---------------csv created for git-----------')

    csv_uploader()
    

def github_main():
    # Search the github for results based on keywords. A Github token is needed. This runs search in commits.
    try:
        github_keywords = []

        # this file has all github keywords
        with open("./input_files/keywords_github.txt") as f:
            github_keywords = [i.strip() for i in f.read().splitlines() if i.strip()]

        github_url = "https://api.github.com"

        # for every keyword, we can get upto 1000 commits (github restricted)
        path1 = os.path.dirname(os.path.abspath(__file__))
        with open(path1 + "/config", "r") as ymlfile:
            config = yaml.safe_load(ymlfile)
        try:
            git_tok = config['github']['github_token']
        except:
            pass
        
        count = 0
        n_current = 0
        github_op = open('github_op.txt', 'w') #output file
        path = "/search/commits"
        url = github_url + path
        for search_string in github_keywords:
            sys.stdout.write("\033[0;32m")
            print("Requests for the keyword - ",search_string)
            sys.stdout.write("\033[0;0m")
            page_num = 0
            while(page_num<10):
                n_current = n_current + 1
                page_num = page_num + 1
                payload = {"q": search_string, "per_page": 1000, "page": page_num}
                headers = {"Authorization": "access_token " + git_tok, "Accept": "application/vnd.github.cloak-preview"}
                try:
                    req = requests.get(url, headers=headers, params=payload, verify=False)
                    print("request status code: ",req.status_code)
                    if req.status_code == 200:
                        results = json.loads(req.text)
                        a=0
                        for item in results['items']:
                            a = a+1
                            try:
                                data = {"id": count+1, "source": "github", "search_string": search_string, "url": item['html_url']}
                                github_op.write(json.dumps(data))
                                github_op.write("\n")
                                count += 1
                            except Exception as e: 
                                print("excpetion ", e)
                                pass
                        print("number of results for this request" , a)
                        if(a == 0):
                            break
                
                except Exception as e:
                    print(colored("[-] error occurred: %s" % e, 'red'))
                    pass
                    
                if n_current % 10 == 0:
                    for remaining in range(63, 0, -1):
                        sys.stdout.write("\r")
                        sys.stdout.write(colored(
                            "\r[#] (-_-)zzZZzzZZzzZZzzZZ sleeping to avoid rate limits. Code will resume soon (-_-)zzZZzzZZzzZZzzZZ | {:2d} seconds remaining.\r".format(
                                remaining), "blue"))
                        sys.stdout.flush()
                        time.sleep(1)
            sys.stdout.write("\033[1;36m")
            print("Done with", search_string, "keyword!")
            sys.stdout.write("\033[0;0m")
        github_op.close()
        to_csv()
        print("Output is written in the github_op.txt file")
    except Exception as e:
        print("EXCEPTION IN GITHUB FUNCTION:- ", str(e))
        pass
