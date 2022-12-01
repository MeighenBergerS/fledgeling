# standard_generator.py
# Authors: Stephan Meighen-Berger
# Script to generate the standard used

# sloth
import sys
sys.path.append("../")
from fledgeling import Fledgeling, config


def main():
    """ Generation script
    """
    print("Welcome to fledgeling!")
    print("I'll be generating the standard tables.")
    print("This may take a while")
    config["general"]["enable logging"] = True
    config["experimental data"]["pre-computed"] = False
    config["advanced"]["store conversion tables"] = True

    fledge = Fledgeling()
    fledge.close()

if __name__ == "__main__":
    main()
