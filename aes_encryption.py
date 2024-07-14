# AES Encryption/Decryption script
# Author: Indrajit Ghosh
# Created On: Jul 14, 2024
# 
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import sys
import hashlib
from pathlib import Path

# Constants
ENCRYPTION_HEADER = b'---  BEGIN ENCRYPTED DATA  ---\n\n'
ENCRYPTION_FOOTER = b'\n\n---  END ENCRYPTED DATA  ---'
DELIMITER = b'---END---'

# Lambda function for base64 encoding of bytes data
base64_encode = lambda data: base64.b64encode(data).decode('utf-8')

# Lambda function for base64 decoding of encoded data. This will return bytes
base64_decode = lambda encoded_data: base64.b64decode(encoded_data.encode('utf-8'))

# Lambda function for sha256 hash
sha256_hash = lambda data: hashlib.sha256(data).hexdigest()

# Derive an AES key from a password
def derive_aes_key(password, salt=None, length=32, iterations=100000):
    if salt is None:
        salt = os.urandom(16)  # Generate a random 16-byte salt if not provided

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )

    key = kdf.derive(password.encode())
    return key, salt
    

def aes_encrypt(data, key):
    # Generate a random IV (Initialization Vector)
    iv = os.urandom(16)
    
    # Create a Cipher object
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    # If input is a string, convert to bytes
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    # Perform padding
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data) + padder.finalize()
    
    # Encrypt the data
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    # Get the sha256 hash of the key
    aes_key_hash = sha256_hash(key)

    return {
        'encrypted_data': encrypted_data,
        'iv': iv,
        'aes_key_hash': aes_key_hash.encode()
    }

def aes_decrypt(encrypted_data, key, iv):
    
    # Create a Cipher object
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    # Decrypt the data
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    
    # Remove padding
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
    
    return unpadded_data

def _get_formatted_encrypted_data(data:dict, armor=False):
    encrypted_data = data.get('encrypted_data')
    iv = data.get('iv')
    salt = data.get('salt')
    old_keyhash = data.get('aes_key_hash')
    if armor:
        # Encode binary data to Base64
        encrypted_data = base64_encode(encrypted_data)
        iv = base64_encode(iv)
        salt = base64_encode(salt)
        formatted_data = f"{ENCRYPTION_HEADER.decode()}{encrypted_data}{DELIMITER.decode()}{iv}{DELIMITER.decode()}{salt}{DELIMITER.decode()}{old_keyhash.decode()}{ENCRYPTION_FOOTER.decode()}"
        formatted_data = formatted_data.encode()
    else:
        formatted_data = ENCRYPTION_HEADER + encrypted_data + DELIMITER + iv + DELIMITER + salt + DELIMITER + old_keyhash + ENCRYPTION_FOOTER

    return formatted_data


def _parse_formatted_encrypted_data(formatted_data, armor=False):
    if armor:
        formatted_data = formatted_data.decode()  # convert bytes to string
        header_index = formatted_data.find(ENCRYPTION_HEADER.decode())
        footer_index = formatted_data.find(ENCRYPTION_FOOTER.decode())
        
        if header_index == -1 or footer_index == -1:
            raise ValueError("Invalid formatted data format")
        
        encrypted_part = formatted_data[header_index + len(ENCRYPTION_HEADER):footer_index]
        parts = encrypted_part.split(DELIMITER.decode())
        if len(parts) != 4:
            raise ValueError("Invalid formatted data format")
        
        encrypted_data = base64_decode(parts[0])
        iv = base64_decode(parts[1])
        salt = base64_decode(parts[2])
        old_keyhash = parts[3].encode()
        
    else:
        header_index = formatted_data.find(ENCRYPTION_HEADER)
        footer_index = formatted_data.find(ENCRYPTION_FOOTER)
        
        if header_index == -1 or footer_index == -1:
            raise ValueError("Invalid formatted data format")
        
        encrypted_part = formatted_data[header_index + len(ENCRYPTION_HEADER):footer_index]
        parts = encrypted_part.split(DELIMITER)
        if len(parts) != 4:
            raise ValueError("Invalid formatted data format")
        
        encrypted_data = parts[0]
        iv = parts[1]
        salt = parts[2]
        old_keyhash = parts[3]
    
    return {
        'encrypted_data': encrypted_data,
        'iv': iv,
        'salt': salt,
        'old_keyhash': old_keyhash,
    }

def store_encrypted_data(file_path:Path, data_dict, armor=False, replace=False):
    file_path = file_path.absolute()
    parent_dir = file_path.parent
    filename = file_path.name

    formatted_data = _get_formatted_encrypted_data(data=data_dict, armor=armor)

    # Determine the new file extension
    add_extension = '.asc' if armor else '.bin'
    
    # Create the new file path by appending the new extension
    new_file_path = parent_dir / (filename + add_extension)

    # If replace is true, delete the old file
    if replace and file_path.exists():
        file_path.unlink()
    
    # Write to file
    with open(new_file_path, 'wb') as file:
        file.write(formatted_data)
   

def load_encrypted_data(file_path):
    with open(file_path, 'rb') as f:
        return f.read()
    
def aes_encrypt_file(filepath:Path, aes_key, salt=None, armor=False, replace=False):
    with open(filepath, 'rb') as f:
        data = f.read()
    enc_dict = aes_encrypt(data=data, key=aes_key)
    enc_dict['salt'] = salt
    store_encrypted_data(file_path=filepath, data_dict=enc_dict, armor=armor, replace=replace)

def aes_decrypt_file(filepath:Path, password, armor=False, replace=False):
    data = load_encrypted_data(file_path=filepath)
    
    data_dict = _parse_formatted_encrypted_data(data, armor=armor)

    # Derive the AES key
    aes_key, _ = derive_aes_key(password=password, salt=data_dict['salt'])

    # Match the key hash
    if sha256_hash(aes_key) != data_dict['old_keyhash'].decode():
        return False
    
    encrypted_data = data_dict['encrypted_data']
    iv = data_dict['iv']

    original_data = aes_decrypt(encrypted_data=encrypted_data, key=aes_key, iv=iv)

    filepath = Path(filepath).absolute()
    parent_dir = filepath.parent
    
    decrypted_file = parent_dir / filepath.stem

    # If replace is true, delete the old file
    if replace and filepath.exists():
        filepath.unlink()
    
    with open(decrypted_file, 'wb') as f:
        f.write(original_data)


# Example usage
def main():
    file = Path(sys.argv[1]).absolute()

    # AES Encryption
    aes_key, salt = derive_aes_key(password="nicebook")
    aes_encrypt_file(filepath=file, aes_key=aes_key, salt=salt, armor=False, replace=False)

    # AES Decryption
    # aes_decrypt_file(filepath=file, password='nicebook', armor=False, replace=False)


if __name__ == "__main__":
    main()
