from email.mime.application import MIMEApplication
from html_try import msg_main
import os
import yaml
import smtplib

from os.path import isfile, exists
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders

from utilities.make_domains_list import domain_list

def attach_file_to_email(email_message, filename, extra_headers=None):
    with open(filename, "rb") as f:
        file_attachment = MIMEApplication(f.read())
    file_attachment.add_header(

        "Content-Disposition",

        f"attachment; filename= {filename}",

    )

    if extra_headers is not None:

        for name, value in extra_headers.items():

            file_attachment.add_header(name, value)

    email_message.attach(file_attachment)

def send_alert_mail():
    subject = 'RTA Tool Results '
    msg = msg_main()
    #msg = "hi"
    path = os.path.dirname(os.path.abspath(__file__))
    with open(path + "/config_mail", "r") as ymlfile:
        config = yaml.safe_load(ymlfile)

    To = config['sendto']['email']
    #for email,value in config['sendto'].items():
        #To.append(str(value))
    #print(To)
    Username = config['email']['username']
    Password = config['email']['password']
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(Username, Password)

    date = str(datetime.now()).split('.')[0]

    mssg = MIMEMultipart('alternative')
    mssg['Subject'] = subject + " - " + date
    mssg['From'] = Username
    mssg['To'] = ", ".join(To)


    html = MIMEText(msg,'html')
    domains = domain_list("./input_files/domains.txt")
    mssg.attach(html)
    l = ["./"+domain+"/tools/Port_scan/pie_chart.png" for domain in domains]
    for i in l:
        attach_file_to_email(mssg, i, {'Content-ID':"<"+i+">"})
    try:
        sent = server.sendmail(Username, To, mssg.as_string())
        server.quit()
        print('[>] ['+date+'] Alert mail sent')
        return True
    except Exception as ae: 
        print(ae)
        print('[!] ['+date+'] Alert mail failed to send')
        return False
#send_alert_mail()
