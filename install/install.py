import os
import sys


class Install():
    """ Install all dependencies for the RTA to run"""

    def __init__(self):
        self.location = os.path.dirname(os.path.realpath(__file__))
        try:
            os.system("pip install -r " + self.location + "/py_dependencies.txt")
        except Exception as e:
            print("Error Occured: " + str(e))
        return

    def os_dependencies_linux(self):
        try:
            brew_dependencies = open(self.location + "/os_dependencies.txt", "r").readlines()
            for dependencies in brew_dependencies:
                os.system("sudo apt-get -y install " + dependencies)
        
        except Exception as e:
            print("Error occured: " + str(e))
        return

    def sublister(self):
        try:
            os.system("git clone https://github.com/aboul3la/Sublist3r " + self.location + "/../recon/Sublist3r")
            os.system("touch " + self.location + "/../recon/Sublist3r/__init__.py")

        except Exception as e:
            print("Sublister installation failed. Please download Sublist3r into recon directory")


def main():
    install = Install()
    
    # linux installation
    if sys.platform == "linux" or sys.platform == "linux2":
        install.os_dependencies()
    
    install.sublister()
    return


if __name__ == '__main__':
    main()