import csv
from datetime import date
import multiprocessing
import shutil
import time
from itertools import count
import os

import pandas as pd
from constants import res
from sub_lister_functions import union_func, amass_run, findomain_run, assetfinder_run, subfinder_run, chaos_run, http_res
from utilities.aquatone_screenshotter import aquatone_run
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

def csv_uploader(domain,file_type):
    gc = gspread.service_account('./client_secret.json')

    today=date.today()
    d1 = today.strftime("%d/%m/%Y")
    sh=gc.create(file_type+domain+d1)
   
    content = open('./'+domain+'/tools/subdomains/'+file_type+'.csv', "r").read().encode("utf8")
    gc.import_csv(sh.id,data=content)
    sh.share('REDACTED', perm_type='user', role='writer', notify=False)    
    print(sh.id)
    res[domain][file_type]=sh.id
    print(res)

def to_csv(domain,file_type):
    cols=['Domain','Subdomain']
    rows=[]
    df=pd.DataFrame(rows,columns=cols)
    f=open("./"+domain+"/tools/subdomains/" + file_type + ".txt")
    for line in f:
        rows=[]
        rows.append({'Domain':domain,'Subdomain':line})
        df1=pd.DataFrame(rows)
        df=pd.concat([df,df1], ignore_index = True)
    df.to_csv("./"+domain+"/tools/subdomains/"+file_type+'.csv')
    csv_uploader(domain,file_type)

def subdomain_run():
    print('hy')
    try:
        max_time = 3000 #max time for which this code will run after which it will terminate subdomain enumeration

        domains = domain_list("./input_files/domains.txt")

        # this is a temporary folder to keep the unclean output obtained
        path_dir = os.path.join("./", "subdomains/")
        try:
            os.mkdir(path_dir)
        except:
            pass

        parent_directory = "./subdomains/"
        for i in domains:
            directory = i
            try:
                path = os.path.join(parent_directory, directory)
                os.mkdir(path)
            except:
                pass
            # this is the tools and the subdomains directoy inside individual domain names to keep their subdomain enumeration.
            try:
                fols = directory + "/tools/subdomains"
                path1 = os.path.join("./", fols)
                os.makedirs(path1)
            except:
                pass
        
        # we are running multiprocessing here to run all the tools together.
        p1 = multiprocessing.Process(target=amass_run, args=(domains,))
        p2 = multiprocessing.Process(target=findomain_run, args=(domains,))
        p3 = multiprocessing.Process(target=subfinder_run, args=(domains,))
        p4 = multiprocessing.Process(target=assetfinder_run, args=(domains,))
        p5 = multiprocessing.Process(target=chaos_run, args=(domains,))
        processes = [p1, p2, p3, p4, p5] 
        #processes=[]
        # start the timer (it is just to keep a track of time of execution)
        start_time = time.time()

        for i in processes:
            i.start()
        timer = 0

        # check in every 15 seconds if the time of execution has exceeded the max time limit
        while timer < max_time:
            time.sleep(15)
            timer += 15
            flag = 0
            for i in processes:
                if i.is_alive():
                    flag = 1
                    break
            if flag == 0:
                break
        
        # process termination in case of alive processes
        for i in processes:
            if i.is_alive():
                i.terminate()

        print("--- time of execution ---- ", time.time() - start_time)
        # remove the ./subdomains folder which kept the unclean files
        shutil.rmtree(parent_directory)

        # run the union, http_rec (func to check is the subdomain is alive) and screenshotter functions on all the subdomains retreived
        for domain in domains:
            union_func("./" + domain + "/tools/subdomains",
                    "./" + domain + "/tools/subdomains/master.txt")
            to_csv(domain,'master')
            http_res("./" + domain + "/tools/subdomains/resolved.txt",
                    "./" + domain + "/tools/subdomains/master.txt", domain)
            to_csv(domain,'resolved')
            aquatone_run("./" + domain + "/tools/subdomains/resolved.txt",
                        "./screenshot/subdomains/"+domain)

        print("--- time of execution ---- ", time.time() - start_time)
    except Exception as e:
        print("EXCEPTION IN SUBDOMAIN RUN:-", str(e))
        pass
    return
#csv_uploader('cleartrip.com','master')
#csv_uploader('cleartrip.com', 'resolved') 
