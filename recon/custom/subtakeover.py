import os
import inspect
import argparse
import dns.resolver


def check_takeover(domain, target):
    dnsResolver = dns.resolver.Resolver()
    dnsResolver.nameservers = ['8.8.8.8', '8.8.4.4']
    try:
        # Query the DNS resolver to check if subdomain is a CNAME
        answers = dnsResolver.query(target, 'CNAME')
        # Query whois
        for rdata in answers:
            output = '{:s}'.format(rdata.target)
            # If scope is/not in output splash some crap out
            if not domain in output:
                return output
    # To solve those "BLAH SUBDOMAIN IS NO CNAME" errors
    except dns.resolver.NoAnswer:
        pass
    except dns.resolver.NXDOMAIN:
        pass
    return 0
