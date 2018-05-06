import os
import json
from commands import getstatusoutput

class WpScan():
    """
    Class which deals with wpscan
    """
    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__))
        return

    def scan(self, target, parent):
        print("\033[93m" + "[i] Launching wpscan: " + target)
        command = 'wpscan --url="' + target +'" --enumerate --format=json --update'
        result = json.loads(list(getstatusoutput(command))[1])

        if 'scan_aborted' in result.keys():
            if "--wp-content-dir" in result['scan_aborted']:
                command += ' --wp-content-dir=wp-content'
                
                result = json.loads(list(getstatusoutput(command))[1])
                if 'scan_aborted' in result.keys():
                    print("\033[91m" + "[i] WpScan aborted with the following reason: " + result['scan_aborted'])
                    return False
                else:
                    return result

        else:
            return result