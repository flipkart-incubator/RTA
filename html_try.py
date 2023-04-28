from utilities.make_domains_list import domain_list


attribs = ["master", "resolved", "Email-ids", "Typosquatting", "Shodan", "Port Scan", "Gau", "FFUF", "SSL scan vul", "SSL scan proto"]
domains_list = domain_list("./input_files/domains.txt")
standalones = ["Github", "Twitter","Port_Scan_Misc"]

from gcp_enum import cloud_res
from github_search import sta_res
from sslyze_run import res
def domain_info(domains_list,attribs):
    print(res)
    HTML_string = "<ul>\n"
    # HTML_string = ""
    for item in domains_list:
        HTML_string += "<br><li><h2>" + item.capitalize() + "</h2>"
        # HTML_string += "<p>{}\n".format(item)
        smal_str ='''   <table id="customers">\n'''
        for i in range(0,len(attribs)):
            if(attribs[i] in res[item]):
                my_link='https://docs.google.com/spreadsheets/d/'+res[item][attribs[i]]
                smal_str +='''      <tr>
                <th>''' + attribs[i].capitalize() + '''</th>
                <td> <a href = "'''+ my_link + '''"> ''' +my_link+'''</a></td>
                </tr>\n'''
        my_link='https://docs.google.com/spreadsheets/d/'+cloud_res[item.split('.')[0]]
        smal_str +='''      <tr>
            <th> Cloud Enum </th>
            <td> <a href = "'''+ my_link + '''"> ''' +my_link+'''</a></td>
        </tr>\n'''
        my_link = "http://172.31.1.7:8000/subdomains/"+item+"/aquatone_report.html#/"
        smal_str +='''      <tr>
            <th> Subdomain screenshots link </th>
            <td> <a href = "'''+ my_link + '''"> ''' +my_link+'''</a></td>
        </tr>\n'''
        my_link = "http://172.31.1.7:8000/typosquating/"+item+"/aquatone_report.html#/"
        smal_str +='''      <tr>
            <th> Typosquatting screenshots link </th>
            <td> <a href = "'''+ my_link + '''"> ''' +my_link+'''</a></td>
        </tr>\n'''
        smal_str += ''' </table>\n'''
        smal_str += '''<br><br><img src="cid:./''' +item+ '''/tools/Port_scan/pie_chart.png" alt = "./''' +item+ '''/tools/Port_scan/pie_chart.png" class="center" width= "800" height= "600"><br><br>'''
        HTML_string += smal_str
        HTML_string += "</li>\n"
        # HTML_string += "</p>\n"
        HTML_string += "<hr>\n"
    HTML_string += "</ul>"
    return HTML_string

def standalone_info(standalones):
    smal_str ='''<br><br>   <table id="customers">\n'''
    for i in range(0,len(standalones)):
        smal_str +='''      <tr>'''
        smal_str += '''<th>''' + standalones[i] + '''</th>'''
        my_link='https://docs.google.com/spreadsheets/d/'+sta_res[standalones[i]]
        # if(sta_res[standalones[i]]):
        #     print("hi")
        if(sta_res[standalones[i]] != "None"):
            smal_str += '''<td> <a href = "'''+ my_link + '''"> ''' +my_link+'''</a></td>'''
        else:
            smal_str += '''<td> None </td>'''
        # if(sta_res[standalones[i]] == None):
        #     print("bye")
#        smal_str +='''<td>'None'</td>'''
            
        smal_str +='''</tr>\n'''
        
    smal_str += ''' </table>\n'''
    return smal_str

def msg_main():
    HTML_msg = ""
    HTML_msg += '''<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="html.css">
</head>
<body>

<h1><u>RTA Report</u></h1><br><br>
<hr>'''
    HTML_msg += domain_info(domains_list,attribs)
    HTML_msg += standalone_info(standalones)
    HTML_msg += '''</body>
</html>'''

    f = open("html.html", "w")
    f.write(HTML_msg)
    f.close()


    return HTML_msg
    
#print(msg_main())
