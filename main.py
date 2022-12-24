# Script to encrypt/decrypt a file (or dir)
#
# Author: Indrajit Ghosh
#
# Created on: Dec 24, 2022
#

from encryption import encrypt_file, encrypt_dir
from decryption import decrypt_file, decrypt_dir
from authentication import save_password, input_secret_key
from pathlib import Path
import sys

INDRAJIT_FERNET_KEY_FILE = Path(__file__).resolve().parent / "rsa_keys/fernet.key"
DOT_ENV_FILE = Path(__file__).parent.resolve() / '.env'
CWD = Path.cwd()


def _encrypt(fernet_file:Path, path:Path=CWD, **kwargs):
    """
    This checks whether `path` is a file or dir and according encrypt it.
    By default it will encrypt `Path.cwd()`.
    """
    path = Path(path)
    if path.is_file():
        encrypt_file(filepath=path, fernet_file=fernet_file, **kwargs)

    else:
        encrypt_dir(root_dir=path, fernet_file=fernet_file, **kwargs)


def _decrypt(fernet_file:Path, path:Path=CWD):
    """
    This checks whether `path` is a file or dir and according decrypt it.
    By default it will decrypt `Path.cwd()`.
    """
    path = Path(path)
    if path.is_file():
        decrypt_file(
            encrypted_file=path, 
            fernet_file=fernet_file
        )

    else:
        decrypt_dir(
            root_dir=path,
            fernet_file=fernet_file
        )


def main():
    
    fernet_key_file = INDRAJIT_FERNET_KEY_FILE

    # Take input properly
    crypto = sys.argv[1]

    p = ' '.join(sys.argv[2:])
    p = Path(p) if p is not None else CWD
    
    if not p.exists():
        print(f"\nERROR: no such file or dir exists > `{p}`\n")
        sys.exit()

    if crypto == 'enc':
        # Encryption
        if DOT_ENV_FILE.exists():
            if input_secret_key():
                _encrypt(path=p, fernet_file=fernet_key_file)
            else:
                print("\nSorry that didn't work!\n")
                sys.exit()
                
        else:
            save_password(filepath=DOT_ENV_FILE)
            print("\nPassword has been saved for future. You can try encrypting again with this new password!\n")

    
    elif crypto == 'dec':
        # Decryption
        if input_secret_key():
            _decrypt(path=p, fernet_file=fernet_key_file)
        else:
            print("\nSorry that didn't work!\n")
            sys.exit()



if __name__ == '__main__':
    main()