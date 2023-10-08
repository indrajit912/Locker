# Codes for decryption
#
# Author: Indrajit Ghosh
#
# Created on: Dec 24, 2022
#

from encryption import *
from encryption import _get_files_in

def decrypt_file(encrypted_file:Path, fernet_file:Path, print_status=True):
    """
    NOTE: This function should not be given to target user
    """
    encrypted_file = Path(encrypted_file)

    # Check if the file is encrypted
    if not is_file_encrypted(encrypted_file):
        print(f"The file {encrypted_file} is not encrypted or encrypted with a different marker.")
        return

    # Getting the encrypted message without the marker
    with open(encrypted_file, 'rb') as f:
        encrypted_message = f.read()[len(MARKER):]


    fernet_key = open(fernet_file, 'rb').read()

    # Getting original message
    fer = Fernet(fernet_key)
    try:
        original_message = fer.decrypt(encrypted_message)
    
        # print(original_message.decode())
        with open(encrypted_file, 'wb') as f:
            f.write(original_message)

        if print_status:
            print("File Decrypted!")
    
    except InvalidToken:
        print(f"\nERROR: The following file might be non-encrypted or encrypted with different Fernet key:\n - {encrypted_file}\n")


def decrypt_dir(root_dir:Path, fernet_file:Path):
    """
    Decrypt all files of the dir and of all its sub dir.
    """
    root_dir = Path(root_dir)
    dot_encrypted_file = root_dir / DOT_ENCRYPTED_FILENAME

    # Check the value in `.encrypted` file
    if int(open(dot_encrypted_file).read()) == True:
        # Decrypt this dir.

        _ignore = [dot_encrypted_file]
        file_count = 0
        data_size = 0
        t1 = time.time()

        for file in _get_files_in(root_dir, ignore=_ignore):
            print(f"Decrypting: '{file}'")
            file_count += 1
            data_size += file.stat().st_size
            decrypt_file(
                encrypted_file=file,
                fernet_file=fernet_file,
                print_status=False
            )
        
        t2 = time.time()
        time_taken = format_time(t2-t1)
        data_size = ByteSize(data_size)

        print(f"\n\nThe directory `{root_dir}` is decrypted successfully.\nTotal file decrypted: {file_count}.\n")
        print(f"Total size of data decrypted: {data_size:.3f}\n")
        print(f"Total time taken: {time_taken}\n")

        # Change the `.encrypted` file value
        with open(dot_encrypted_file, 'w') as f:
            f.write("0")
    else:
        # Not encrypted
        print(f"\nCAN'T DECRYPT since the directory is not encrypted: {root_dir}\n")



def main():
    print('Python Script for Decryption!')
    from main import INDRAJIT_FERNET_KEY_FILE
    decrypt_file(encrypted_file='spam.mkv', fernet_file=INDRAJIT_FERNET_KEY_FILE)


if __name__ == '__main__':
    main()