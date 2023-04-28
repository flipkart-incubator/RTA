# Red Team Arsenal&nbsp; [![Tweet](https://img.shields.io/twitter/url/http/shields.io.svg?style=social)](https://twitter.com/intent/tweet?text=Red%20Team%20Arsenal%20(RTA)%20-%20An%20intelligent%20scanner%20to%20detect%20security%20vulnerabilities%20in%20company%27s%20layer%207%20assets&url=https://github.com/flipkart-incubator/RTA&via=a0xnirudh&hashtags=security,infosec,bugbounty)

<p align="center">
  <img src="https://raw.githubusercontent.com/flipkart-incubator/RTA/master/rta.svg?sanitize=true" alt="Red Team Arsenal"/>
</p>

[![Github Release Version](https://img.shields.io/badge/release-V2.0-green.svg)](https://github.com/flipkart-incubator/RTA)
[![Github Release Version](https://img.shields.io/badge/python-3.8-green.svg)](https://github.com/flipkart-incubator/RTA)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://github.com/flipkart-incubator/RTA/blob/master/LICENSE)
[![RTA loves Open source](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/flipkart-incubator/RTA)

**Red Team Arsenal** is a inhouse framework created by flipkart security team which monitors the external attack surface of the company's online assets and provide an **holistic security** view of any security anomalies. It's a closely linked collection of various security engines and tools to conduct/simulate attacks and monitor public facing assets for anomalies and leaks.

It's an intelligent framework that detects security anomalies in all layer 7 assets and reports the same. 

As companies continue to expand their footprint on INTERNET via various acquisitions and geographical expansions, human driven security engineering is not scalable, hence, companies need feedback driven automated systems to stay put.

## Installation



### Supported Platforms

RTA has been tested both on **Ubuntu/Debian** (apt-get based distros) distros, it will also work with Mac-OS (but do replace the binaries folder with the binaries of the programs that match with your system architecture if you are running it on Mac OS)

### Prerequisites:

There are a few packages which are necessary before proceeding with the installation:

* Python 3.8, which is installed by default in most systems
* Python pip: `sudo apt-get install python3-pip`

Also, you will need to update the config file and config_mail yml files with the following data

* Google Chat Webhook URL
* SMTP Credentials
* Github Token
* Mailing List 
* Custom Search Engine (API Key)


You can install all the requirements by running  ``sudo pip3 install -r requirements.txt``



## Usage

Mention the domains you want to monitor inside 'input_files/domains.txt'

```python3 scheduler.py```



### Configuring Google Chat:

You can receive notifications in  Google Chat, this can be configured by adding the webhook URL to config.yml file.


## Contributors

- Anirudh Anand ([@a0xnirudh](https://twitter.com/a0xnirudh))
- Mohan KK ([@MohanKallepalli](https://twitter.com/MohanKallepalli))  
- Ankur Bhargava ([@_AnkurB](https://twitter.com/_AnkurB))  
- Prajal Kulkarni ([@prajalkulkarni](https://twitter.com/prajalkulkarni))  
- Himanshu Kumar Das ([@mehimansu](https://twitter.com/mehimansu))
- Mandeep Jadon ([@1337tr0lls](https://twitter.com/1337tr0lls))
- Vivek Srivastav ([@vivek_15887](https://twitter.com/vivek_15887))
- Abhishek S ([@abhiabhi2306](https://twitter.com/abhiabhi2306))



