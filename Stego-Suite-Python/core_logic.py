import os
import logging
import struct  # <-- ADDED THIS
from utils import compression, crypto, file_io
from technique import lsb_hider, append_hider

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Define our file groups ---

# Techniques that hide data in the LSBs (invisible, but fragile)
LSB_TYPES = ['.png', '.bmp', '.wav']

# Techniques that append data (robust, but less stealthy)
APPEND_TYPES = [
    '.jpg', '.jpeg', '.gif',  # Images
    '.mp3', '.m4a',          # Audio
    '.mp4', '.mkv', '.avi',  # Video
    '.pdf', '.docx'          # Documents
]

def hide_data(secret_file: str, cover_file: str, output_file: str, password: str):
    """
    The main "HIDE" function.
    1. Reads secret file
    2. Compresses data
    3. Encrypts data
    4. Selects the correct hiding technique
    5. Saves the new stego file
    """
    logging.info("--- Starting Encode Process ---")
    try:
        # 1. Read
        logging.info(f"Reading secret file: {secret_file}")
        data = file_io.read_bytes(secret_file)
        
        # 2. Compress
        logging.info("Compressing data...")
        compressed_data = compression.compress(data)
        
        # --- 3. Create Payload (NEW) ---
        # We now store the filename *with* the data
        # Format: [2-byte Filename Length][Filename][Compressed Data]
        
        filename = os.path.basename(secret_file)
        filename_bytes = filename.encode('utf-8')
        
        # 'H' is unsigned short (2 bytes), for filename length
        filename_len_bytes = struct.pack('>H', len(filename_bytes))
        
        # This is the final payload that will be encrypted
        payload_to_encrypt = filename_len_bytes + filename_bytes + compressed_data
        
        # 4. Encrypt
        logging.info("Encrypting payload...")
        encrypted_payload = crypto.encrypt(payload_to_encrypt, password)
        
        # 5. Select Technique
        ext = os.path.splitext(cover_file)[1].lower()
        logging.info(f"Cover file type detected: {ext}")
        
        if ext in LSB_TYPES:
            logging.info("Using LSB (invisible) technique.")
            lsb_hider.encode(encrypted_payload, cover_file, output_file)
        elif ext in APPEND_TYPES:
            logging.info("Using Append (robust) technique.")
            append_hider.encode(encrypted_payload, cover_file, output_file)
        else:
            raise ValueError(f"Unsupported cover file type: {ext}. Cannot hide data.")
            
        logging.info(f"--- Encode Process Successful. File saved to {output_file} ---")
        
    except Exception as e:
        logging.error(f"Encode process failed: {e}")
        raise # Re-raise the exception so the GUI can catch it

def extract_data(stego_file: str, password: str): # <-- MODIFIED
    """
    The main "EXTRACT" function.
    1. Selects the correct extraction technique
    2. Decrypts data (fails if password is wrong)
    3. Decompresses data
    4. Returns the ORIGINAL FILENAME and the raw secret file bytes
    """
    logging.info("--- Starting Decode Process ---")
    try:
        # 1. Select Technique
        ext = os.path.splitext(stego_file)[1].lower()
        logging.info(f"Stego file type detected: {ext}")
        
        if ext in LSB_TYPES:
            logging.info("Using LSB (invisible) technique.")
            encrypted_payload = lsb_hider.decode(stego_file)
        elif ext in APPEND_TYPES:
            logging.info("Using Append (robust) technique.")
            encrypted_payload = append_hider.decode(stego_file)
        else:
            raise ValueError(f"Unsupported file type: {ext}. Cannot extract data.")
            
        # 2. Decrypt
        logging.info("Decrypting data...")
        # This will fail with a ValueError if password is wrong
        decrypted_payload = crypto.decrypt(encrypted_payload, password) 
        
        # --- 3. Parse Payload (NEW) ---
        # Format: [2-byte Filename Length][Filename][Compressed Data]
        
        # Get filename length
        filename_len = struct.unpack('>H', decrypted_payload[:2])[0]
        
        # Get filename
        filename_start = 2
        filename_end = 2 + filename_len
        filename = decrypted_payload[filename_start:filename_end].decode('utf-8')
        
        # Get the rest of the data (the compressed file)
        compressed_data = decrypted_payload[filename_end:]

        # 4. Decompress
        logging.info("Decompressing data...")
        decompressed_data = compression.decompress(compressed_data)
        
        logging.info("--- Decode Process Successful ---")
        return filename, decompressed_data # <-- RETURN FILENAME AND DATA
        
    except Exception as e:
        logging.error(f"Decode process failed: {e}")
        raise # Re-raise for the GUI