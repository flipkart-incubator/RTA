import schedule
import time
from datetime import date
from email_try import send_alert_mail
from port_scan import port_scan_main
from constants import lists_creator
from dnstwist import dnswist_main
from fuff_run import ffuf_main
from gau_run import gau_main
from gcp_enum import cloud_enum_main
from github_search import github_main
from phonebook_run import phonebook_main
from shodan import shodan_main
from sslyze_run import sslyse_main
from sub_lister import subdomain_run
from twitter import tweet

def main():
    # eyeryday run these functions
    scheduled_time = "04:48"
    try:
        schedule.every().day.at(scheduled_time).do(lists_creator)
    except Exception as e:
        print(str(e))
        pass
    
    try:
        schedule.every().day.at(scheduled_time).do(subdomain_run)
    except Exception as e:
        print(str(e))
        pass
    
    try:
        schedule.every().day.at(scheduled_time).do(phonebook_main)
    except Exception as e:
        print(str(e))
        pass
    
    try:
        schedule.every().day.at(scheduled_time).do(dnswist_main)
    except Exception as e:
        print(str(e))
        pass
    
    # try\
    try:
        schedule.every().day.at(scheduled_time).do(tweet)
    except Exception as e:
        print(str(e))
        pass
    

    # alternate day
    if date.today().day%2 == 0:
	
        try:
           schedule.every().day.at(scheduled_time).do(port_scan_main)
           print("port scan")
        except Exception as e:
            print(str(e))
            pass
    
    # monthly 
    print(date.today().day)
    if date.today().day ==15:
        try:
            schedule.every().day.at(scheduled_time).do(gau_main)
        except Exception as e:
            print(str(e))
            pass
    

    # every week at sunday run these.
    try:
        schedule.every().thursday.at(scheduled_time).do(ffuf_main)
    except Exception as e:
        print(str(e))
        pass
    
    try:
        schedule.every().thursday.at(scheduled_time).do(sslyse_main)
    except Exception as e:
        print(str(e))
        pass
    
    try:
        schedule.every().thursday.at(scheduled_time).do(github_main)
    except Exception as e:
        print(str(e))
        pass
    

    try:
        schedule.every().day.at(scheduled_time).do(cloud_enum_main)
    except Exception as e:
        print(str(e))
        pass
    
    try:
        schedule.every().day.at(scheduled_time).do(send_alert_mail)
    except Exception as e:
        print(str(e))
        pass
    

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
