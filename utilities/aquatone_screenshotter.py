import shutil
import subprocess
import os

# input file must have only domain (or subdomain) names. Each in separate line (without the http/https prefix)
def aquatone_run(input_file, output_folder):
    # this try except is because aquatone appends to the files instead of rewriting on files
    # so we delete the folder if it exists and write to a new one
    if os.path.isdir(output_folder):
        try:
            shutil.rmtree(output_folder)
        except:
            print("folder exists but could not delete it")
    subprocess.run("cat "+ input_file +" | ./binaries/aquatone -out " + output_folder + " -silent -http-timeout 5000 -save-body=false", shell = True)
