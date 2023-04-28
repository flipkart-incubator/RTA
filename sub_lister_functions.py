from io import BytesIO
import subprocess
import os
import zipfile
import requests
import httpx
from utilities.difference import diff, message_maker, notify_gchat

from utilities.make_domains_list import domain_list

# run the amass tool for subdomain enumeration
def amass_run(domains):
    for domain in domains:
        f = open("./subdomains/" + domain + "/amass_list.txt", "w")
        subprocess.run("./binaries/amass enum -passive -d " + domain, shell=True, stdout=f)
        cleaner("./subdomains/" + domain + "/amass_list.txt",
                "./" + domain + "/tools/subdomains/amass.txt", domain)
        f.close()

# run the findomain tool for subdomain enumeration
def findomain_run(domains):
    for domain in domains:
        f = open("./subdomains/" + domain + "/findomain_list.txt", "w")
        subprocess.run("./binaries/findomain-linux -t " + domain, shell=True, stdout=f)
        cleaner("./subdomains/" + domain + "/findomain_list.txt",
                "./" + domain + "/tools/subdomains/findomain.txt", domain)
        f.close()

# run the subfinder tool for subdomain enumeration
def subfinder_run(domains):
    for domain in domains:
        f = open("./subdomains/" + domain + "/subfinder_list.txt", "w")
        subprocess.run("./binaries/subfinder -d " + domain, shell=True, stdout=f)
        cleaner("./subdomains/" + domain + "/subfinder_list.txt",
                "./" + domain + "/tools/subdomains/subfinder.txt", domain)
        f.close()

# run the assetfinder tool for subdomain enumeration
def assetfinder_run(domains):
    for domain in domains:
        f = open("./subdomains/" + domain + "/assetfinder_list.txt", "w")
        subprocess.run("./binaries/assetfinder " + domain, shell=True, stdout=f)
        cleaner("./subdomains/" + domain + "/assetfinder_list.txt",
                "./" + domain + "/tools/subdomains/assetfinder.txt", domain)
        f.close()

# use chaos to download and unzip the files containing subdomains
def chaos_run(domains):
    for domain in domains:
        name = domain
        url = 'https://chaos-data.projectdiscovery.io/' + name + '.zip'
        print(url)
        try:
            req = requests.get(url, stream=True, verify=False)
            zip_file = zipfile.ZipFile(BytesIO(req.content))
            zip_file.extractall("./subdomains/" + domain)
            zip_file.extractall("./" + domain + "/tools/subdomains")
        except:
            pass

# function to clean the output obtained so that the final list only contains subdomains (and nothing like run time execution etc..)
def cleaner(unclean_file_path, clean_file_path, domain):
    f = open(clean_file_path, "w")
    subprocess.run("grep -i \".*\." + domain + "\" " + unclean_file_path, shell=True, stdout=f)
    f.close()

# takes the path of the directory and finds the union of all the lists and stores it in the union_file_path
def union_func(dir_path, union_file_path):
    # subprocess.run("cat " + dir_path + "/*.txt | sort > ./union/no_union.txt", shell=True)    #this is the line for
    # no union list, i.e. plain concatenation
    print("cat " + dir_path + "/*.txt | sort -u > " + union_file_path)
    subprocess.run("cat " + dir_path + "/*.txt | sort -u > " + union_file_path, shell=True)

# this function is to check if the subdomain enumerated is alive or not
def http_res(resolved_path, union_path, domain):
    temp_path = "./" + domain + "/tools/subdomains/temp_resolved.txt"
    temp_cursor = open(temp_path, "w")
    count = 0
    with open(union_path) as f:
        for line in f:
            count = count + 1
            # requesting with .get method with http protocol
            try:
                response = httpx.get("http://" + line.strip())
                if response.status_code == 200:
                    temp_cursor.write("http://" + line)
                    print(count)
            except Exception as e:
                pass
            # requesting with .get method with https protocol
            try:
                response = httpx.get("https://" + line.strip(), verify=False, )
                if response.status_code == 200:
                    temp_cursor.write("https://" + line)
                    print(count)
            except Exception as e:
                pass
    f.close()
    # run the httpx binary on the mater file and append its output tothe temporary file
    subprocess.run("./binaries/httpx -list " + union_path + " -silent >> " + temp_path, shell=True)
    
    # check the difference between the new output and the old data.
    msg = message_maker(diff(resolved_path, temp_path))
    # send the difference as a google chat notification
    notify_gchat(msg)
    
    # this part is to append the old version to the new version and sort it. The final output remains in the resolved_path file.
    subprocess.run("cat "+resolved_path+" >> " + temp_path, shell=True)
    subprocess.run("sort -u " + temp_path + " > " + resolved_path, shell=True)
    
    # delete the temporary file
    os.remove(temp_path)
