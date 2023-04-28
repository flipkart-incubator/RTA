from utilities.make_domains_list import domain_list

res={}
sta_res={'Github':"None",'Twitter':"None","Port_Scan_Misc":"None"}
cloud_res={}
def lists_creator():
    print("hyyyyy")
    domains = domain_list("./input_files/domains.txt")
    for domain in domains:
        res[domain]={}
    mp={}
    for company in domains:
        cloud_res[company.split('.')[0]]= "None"
