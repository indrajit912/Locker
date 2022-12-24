# This script is meant for user authentication for a project.
#
# Author: Indrajit Ghosh
#
# Created on: Dec 23, 2022
#

import os, sys
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

SECRET_KEY = os.environ.get("HASHED_PASSWORD")
SALT = os.environ.get("SALT")

import hashlib
from pathlib import Path
DOT_ENV_FILE = Path(__file__).parent.resolve() / '.env'

PWINPUT = True
try:
    import pwinput
except ModuleNotFoundError:
    PWINPUT = False
    import getpass

INDENT = "    "
SUBHEADING = '\033[1m' + '\x1b[38;2;255;127;80m'
RESET = '\033[0m'


def sha256_hash(raw_text):
    """Return the hex hash value"""
    hashed = hashlib.sha256(raw_text.encode()).hexdigest()

    return hashed


def input_secret_key():
    """
    Ask user for the secret key
    Return: True or False
    """
    if PWINPUT:
        res = pwinput.pwinput(prompt=f"\n{INDENT}{SUBHEADING}Kindly enter the `password`{RESET}: ", mask="*")
    else:
        res = getpass.getpass(f"\n{INDENT}{SUBHEADING}Kindly enter the `password`{RESET}: ")

    return sha256_hash(res + SALT) == SECRET_KEY


def save_password(filepath:Path=DOT_ENV_FILE):
    """
    Take password from user and then saves the sha256().hex of that password
    into `.env` together with a random salt.
    """
    if PWINPUT:
        passwd = pwinput.pwinput(prompt=f"\n{INDENT}{SUBHEADING}Kindly enter a new `password`{RESET}: ", mask="*")
    else:
        passwd = getpass.getpass(f"\n{INDENT}{SUBHEADING}Kindly enter a new `password`{RESET}: ")

    
    passwd2 = input(f"\n{INDENT}{SUBHEADING}Kindly re-enter that `password`{RESET}: ")

    if passwd == passwd2:
        # Save password
        salt = "sHIi2348@$sdfJK8923$9dfl" # TODO: make it random every time
        with open(filepath, 'w') as f:
            hashed_passwd = sha256_hash(passwd + salt)
            f.write(f"HASHED_PASSWORD={hashed_passwd}\nSALT={salt}")

        print("\nThe password saved successfully!\n")

    else:
        print("\nERROR: Sorry password didn't match!\n")
        sys.exit()

    

def main():
    save_password()


if __name__ == '__main__':
    main()