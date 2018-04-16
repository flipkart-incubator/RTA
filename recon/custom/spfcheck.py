import sys
import dns.resolver

# Source: https://gist.github.com/mzupan/7202254    

resolves = 0

def doResolve(host):
    global resolves

    answers = dns.resolver.query(host, 'TXT')
    resolves += 1
    for rdata in answers:
        for part in str(rdata).split():
            if "include" in part:
                doResolve(part.split(":")[1])
            elif part in ["a", "mx", "ptr", "exists"]:
                resolves += 1

def spflookups(host):
    global resolves
    try:
        answers = dns.resolver.query(str(host), 'TXT')
        for rdata in answers:
            for part in str(rdata).split():
                if "include" in part:
                    doResolve(part.split(":")[1])
                elif part in ["a", "mx", "ptr", "exists"]:
                    resolves += 1
    except Exception as e:
        pass
    return resolves