import csv
from datetime import date
import datetime
# from .constants import sta_res
import pandas as pd
from Scweet.Scweet.scweet import scrape


import gspread
# import pygsheets
import pandas as pd
import ssl

import requests
from shodan import sta_res

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
    sh=gc.create('twitter'+d1)
    content = open("final_twitter_output.csv", "r").read().encode("utf8")
    gc.import_csv(sh.id,data=content)
    sh.share('REDACTED', perm_type='user', role='writer',notify=False)
    print("-------------------------------------------------- Uploaded google sheet of tweet function")
    sta_res['Twitter']=sh.id
    print(sta_res)

def tweet():
    try:
        with open("input_files/keywords_twitter.txt") as f:
            keywords = [i.strip() for i in f.read().splitlines() if i.strip()]
        print(keywords)
        today=date.today()
        d1=today.strftime("%Y-%m-%d")
        d2=date.today()+datetime.timedelta(days=1)
        d3=today.strftime("%Y-%m-%d")
        data = scrape(words=keywords, since=d1, until=d3, from_account = None, interval=1, headless=True, display_type="Top", save_images=False, lang="en",
        resume=False, filter_replies=False, proximity=False, geocode="20.5937,78.9629,1000km")
        data.to_csv('twitter_output.csv',mode='w')

        df=pd.DataFrame(columns=['UserScreenName','UserName','Timestamp','Text','Embedded_text','Emojis','Comments','Likes','Retweets','Image link','Tweet URL'])
        
        for index, row in data.iterrows():
            entry=row['Embedded_text'].lower()
            if(entry.find('order id')==-1 and entry.find('order')==-1 and entry.find('orderid')==-1):
                ls=[]
                rows=[]
                for items in row.iteritems():
                    ls.append(items[1])
                rows.append({'UserScreenName':ls[0],'UserName':ls[1],'Timestamp':ls[2],'Text':ls[3],'Embedded_text':ls[4],'Emojis':ls[5],'Comments':ls[6],'Likes':ls[7],'Retweets':ls[8],'Image link':ls[9],'Tweet URL':ls[10]})
                df1=pd.DataFrame(rows)
                df=pd.concat([df,df1], ignore_index = True)
        df.to_csv('final_twitter_output.csv',mode='w')
        print("-------------------------------------------------- made csv of tweet function")
        csv_uploader()
    except Exception as e:
        print("EXCEPTION IN TWEET FUNCTION:- ", str(e))
        pass

