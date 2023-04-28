import csv
from datetime import date
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys  # gives access to submit key
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from utilities.make_domains_list import domain_list
from sub_lister import res
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
    

def csv_uploader(domain):
    gc = gspread.service_account('./client_secret.json')
    today=date.today()
    d1 = today.strftime("%d/%m/%Y")
    sh=gc.create('phonebook'+domain+d1)
    content = open('./'+domain+'/tools/email_ids/'+domain+'.csv', "r").read().encode("utf8")
    gc.import_csv(sh.id,data=content)
    sh.share('REDACTED', perm_type='user', role='writer',notify=False)
    res[domain]["Email-ids"]=sh.id
    print("made google sheet of " + domain + " for email ids")
    print(res)

def to_csv(domain):
    cols=['Domain','Email Id']
    rows=[]
    df=pd.DataFrame(rows,columns=cols)
    f=open("./"+domain+"/tools/email_ids/" + domain + ".txt")
    for line in f:
        rows=[]
        rows.append({'Domain':domain,'Email Id':line})
        df1=pd.DataFrame(rows)
        df=pd.concat([df,df1], ignore_index = True)
    df.to_csv("./"+domain+"/tools/email_ids/"+domain+'.csv')
    print("made csv of " + domain + "for emailids")
    csv_uploader(domain)


def phonebook_run(domains):
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    driver = webdriver.Chrome('./binaries/chromedriver', options=option)
#    driver.manage().timeouts().implicitlyWait(10, TimeUnit.SECONDS);
    driver.implicitly_wait(10)
    driver.get('https://phonebook.cz/')

    for i in domains:
        try:
            fols = i + "/tools/email_ids"
            path1 = os.path.join("./",fols)
            os.makedirs(path1)
        except:
            pass
        search = driver.find_element(By.ID, "domain")
        search.clear()
        search.send_keys(i)
        search.send_keys(Keys.RETURN)
        try:
            time.sleep(10)
            result = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "result")))
        except:
            driver.quit()
        f = open("./"+i+"/tools/email_ids/" + i + ".txt", "w")
        f.write(result.text)
        f.close()
        to_csv(i)
        print("done Phonebook")
    driver.quit()


def phonebook_main():
    try:
        domains = domain_list("./input_files/domains.txt")
        phonebook_run(domains=domains)    
    except Exception as e:
        print("EXCEPTION IN PHONEBOOK MAIN : - ", str(e))
        pass
#phonebook_main()
