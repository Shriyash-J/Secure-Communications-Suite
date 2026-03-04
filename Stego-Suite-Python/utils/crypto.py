import logging
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256  # <-- THIS LINE IS CHANGED

# --- Constants ---
KEY_SIZE_BYTES = 32  # 32 bytes = 256 bits
NONCE_SIZE_BYTES = 16 # AES-GCM recommended nonce size
TAG_SIZE_BYTES = 16  # AES-GCM recommended tag size
SALT_SIZE_BYTES = 16
PBKDF2_ITERATIONS = 100000  # Standard number of iterations

def get_key_from_password(password: str, salt: bytes) -> bytes:
    """
    Derives a 32-byte key from a password using PBKDF2.
    """
    key = PBKDF2(
        password,
        salt,
        dkLen=KEY_SIZE_BYTES,
        count=PBKDF2_ITERATIONS,
        hmac_hash_module=SHA256  # <-- THIS LINE IS CHANGED
    )
    return key

def encrypt(data: bytes, password: str) -> bytes:
    """
    Encrypts data using AES-GCM.
    Returns a single bytestring: [salt][nonce][tag][ciphertext]
    """
    if not password:
        raise ValueError("A password is required for encryption.")

    # 1. Generate a random salt for password key derivation
    salt = get_random_bytes(SALT_SIZE_BYTES)
    
    # 2. Derive the encryption key
    key = get_key_from_password(password, salt)
    
    # 3. Create a new AES-GCM cipher
    cipher = AES.new(key, AES.MODE_GCM)
    
    # 4. Encrypt the data and get the authentication tag
    ciphertext, tag = cipher.encrypt_and_digest(data)
    
    # 5. Get the nonce (it's generated automatically)
    nonce = cipher.nonce
    
    # 6. Return all parts concatenated together.
    # [ 16-byte salt | 16-byte nonce | 16-byte tag | variable-ciphertext ]
    logging.info("Encryption successful.")
    return salt + nonce + tag + ciphertext

def decrypt(payload: bytes, password: str) -> bytes:
    """
    Decrypts data using AES-GCM.
    Expects the bytestring: [salt][nonce][tag][ciphertext]
    """
    if not password:
        raise ValueError("A password is required for decryption.")
        
    try:
        # 1. Split the payload into its parts
        salt = payload[:SALT_SIZE_BYTES]
        nonce = payload[SALT_SIZE_BYTES:SALT_SIZE_BYTES + NONCE_SIZE_BYTES]
        tag = payload[SALT_SIZE_BYTES + NONCE_SIZE_BYTES : SALT_SIZE_BYTES + NONCE_SIZE_BYTES + TAG_SIZE_BYTES]
        ciphertext = payload[SALT_SIZE_BYTES + NONCE_SIZE_BYTES + TAG_SIZE_BYTES:]
        
        # 2. Derive the key using the same salt and password
        key = get_key_from_password(password, salt)
        
        # 3. Create the AES-GCM cipher
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        
        # 4. Decrypt and verify
        # This step is crucial. It checks the tag.
        # If the tag is wrong, it means:
        #    a) The password was wrong
        #    b) The data is corrupt
        # It will raise a ValueError if verification fails.
        decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
        
        logging.info("Decryption successful.")
        return decrypted_data
        
    except (ValueError, KeyError) as e:
        logging.error(f"Decryption failed: {e}. Wrong password or corrupt data.")
        raise ValueError("Decryption failed. Wrong password or corrupt data.")
    except Exception as e:
        logging.error(f"An unexpected error occurred during decryption: {e}")
        raise