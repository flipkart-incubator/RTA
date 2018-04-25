# Red Team Arsenal &nbsp; [![Tweet](https://img.shields.io/twitter/url/http/shields.io.svg?style=social)](https://twitter.com/intent/tweet?text=Red%20Team%20Arsenal%20(RTA)%20-%20An%20intelligent%20scanner%20to%20detect%20security%20vulnerabilities%20in%20company%27s%20layer%207%20assets&url=https://github.com/flipkart-incubator/RTA&via=a0xnirudh&hashtags=security,infosec,bugbounty)

<p align="center">
  <img src="https://raw.githubusercontent.com/flipkart-incubator/RTA/master/rta.svg?sanitize=true" alt="Red Team Arsenal"/>
</p>

[![Github Release Version](https://img.shields.io/badge/release-V1.0-green.svg)](https://github.com/flipkart-incubator/RTA)
[![Github Release Version](https://img.shields.io/badge/python-2.7-green.svg)](https://github.com/flipkart-incubator/RTA)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://github.com/flipkart-incubator/RTA/blob/master/LICENSE)
[![RTA loves Open source](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/flipkart-incubator/RTA)

**Red Team Arsenal** is a web/network security scanner which has the capability to scan all company's online facing assets and provide an **holistic security** view of any security anomalies. It's a closely linked collections of security engines to conduct/simulate attacks and monitor public facing assets for anomalies and leaks.

It's an intelligent scanner detecting security anomalies in all layer 7 assets and gives a detailed report with integration support with nessus.
As companies continue to expand their footprint on INTERNET via various acquisitions and geographical expansions, human driven security engineering is not scalable, hence, companies need feedback driven automated systems to stay put.

## Installation

### Supported Platforms

RTA has been tested both on **Ubuntu/Debian** (apt-get based distros) and as well as **Mac OS**. It should ideally work with any linux based distributions with mongo and python installed (install required python libraries from `install/py_dependencies` manually).

### Prerequisites:

There are a few packages which are necessary before proceeding with the installation:

* Git client: `sudo apt-get install git`
* Python 2.7, which is installed by default in most systems
* Python pip: `sudo apt-get install python-pip`
* MongoDB: Read the [official installation](https://docs.mongodb.com/manual/installation) guide to install it on your machine.

Finally run ``python install/install.py``

There are also optional packages/tools you can install (highly recommended):

### Integrating Nessus {OPTIONAL}:

Integrating Nessus into Red Team Arsenal can be done is simple 3 steps:

* Download and install [Nessus community edition](https://www.tenable.com/downloads/nessus) (if you don’t have a paid edition). If you already have an installation (it can be remote installation as well), then go to step (2).

* Update the `config` file (present on the root directory of RTA) with Nessus URL, username and password.

* Create a nessus policy where you can configure the type of scans and plugins to run and name it **RTA** (Case sensitive - use full uppercase).

* Once the config file has the correct Nessus information (url, username, password), use the flag `--nessus` while running RTA to launch nessus scan over the entire subdomains gathered by RTA (one single scan initiated with all the subdomains gathered).


## Usage

Short Form    | Long Form     | Description
------------- | ------------- |-------------
-u            | --url         | Domain URL to scan
-v            | --verbose     | Enable the verbose mode and display results in realtime
-n            | --nessus      | Launch a Nessus scan with all the subdomains
-s            | --scraper     | Run scraper based on config keywords
-h            | --help        | show the help message and exit

## Sample Output

```
a0xnirudh@exploitbox /RTA (master*) $ python rta.py --url "0daylabs.com" -v -s

              ____          _   _____                         _                              _
             |  _ \ ___  __| | |_   _|__  __ _ _ __ ___      / \   _ __ ___  ___ _ __   __ _| |
             | |_) / _ \/ _` |   | |/ _ \/ _` | '_ ` _ \    / _ \ | '__/ __|/ _ \ '_ \ / _` | |
             |  _ <  __/ (_| |   | |  __/ (_| | | | | | |  / ___ \| |  \__ \  __/ | | | (_| | |
             |_| \_\___|\__,_|   |_|\___|\__,_|_| |_| |_| /_/   \_\_|  |___/\___|_| |_|\__,_|_|


[i] Checking for Zonetransfer
[i] Zone Transfer is not enabled

[i] Checking for SPF records
[+] SPF record lookups is good. Current value is: 9

[-] Enumerating subdomains now for 0daylabs.com
[-] Searching now in Baidu..
[-] Searching now in Yahoo..
[-] Searching now in Google..
[-] Searching now in Bing..
[-] Searching now in Ask..
[-] Searching now in Netcraft..
[-] Searching now in DNSdumpster..
[-] Searching now in Virustotal..
[-] Searching now in ThreatCrowd..
[-] Searching now in SSL Certificates..
[-] Searching now in PassiveDNS..
[-] Total Unique Subdomains Found: 3
blog.0daylabs.com
www.0daylabs.com
test.0daylabs.com

[+] Verifying Subdomains and takeover options

[+] Possible subdomain takeovers (Manual verification required):
 
 test.0daylabs.com

[i] Verified and Analyzed Subdomains:

[i] URL: blog.0daylabs.com
[i] Wappalyzer: [u'jQuery', u'Varnish', u'Font Awesome', u'Twitter Bootstrap', u'Google Analytics', u'Google Font API', u'Disqus', u'Google AdSense']

[i] Scraper Results

[+] Shodan
Hostname: test.0daylabs.com                 IP: 139.59.63.111       Ports: 179
Hostname: test.0daylabs.com                 IP: 139.59.63.111       Ports: 179

[+] Twitter
URL: https://twitter.com/tweetrpersonal9/status/832624003751694340      search string: 0daylabs
URL: https://twitter.com/ratokeshi/status/823957535564644355            search string: 0daylabs

```


## Notifications

### Configuring Slack:

RTA can also do push notifications to `slack` which includes the main scan highlight along with Nessus and other integrated scanner reports divided on the basis of severity.

* In your slack, create an [incoming webhook](https://api.slack.com/incoming-webhooks) and point it to the channel where you need the RTA to send the report. You can read more about creating incoming webhooks on slack documentation.


* In the config file, update the **URL** in the slack section with full URL (including https://) for the incoming webhook.


Once slack is configured, you will automatically start getting reports on your configured slack channel


## Roadmap

Here are couple of ideas which we have in mind to do going ahead with RTA. If you have any ideas/feature requests which is not listed below, feel free to raise an [issue in github](https://github.com/flipkart-incubator/RTA/issues).

* Email the results once the scan is completed.

* Extend the current RTA API so that we can launch custom scans with required options via the API.

* Launch custom scans based on Wappalyzer results (eg: wpscan if wordpress is detected)

* Investigate and integrate more web security scanners including but not limited to Arachni, Wapiti, Skipfish and others !

* JSON/XML output formatting for the RTA scan result.

* Improving the logic for Subdomain takeover.

* Multi threading support for faster scan comple.


## Contributors

Awesome people who built this project:

##### Lead Developers:

Anirudh Anand ([@a0xnirudh](https://twitter.com/a0xnirudh))

##### Project Contributors:

Mohan KK ([@MohanKallepalli](https://twitter.com/MohanKallepalli))  
Ankur Bhargava ([@_AnkurB](https://twitter.com/_AnkurB))  
Prajal Kulkarni ([@prajalkulkarni](https://twitter.com/prajalkulkarni))  
Himanshu Kumar Das ([@mehimansu](https://twitter.com/mehimansu))

## Special Thanks

[Sublist3r](https://github.com/aboul3la/Sublist3r)
