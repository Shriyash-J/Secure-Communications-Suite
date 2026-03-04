import logging
import struct # For packing the data length
from utils.file_io import read_bytes, write_bytes

# A unique "magic" bytestring to mark the start of our hidden data
# This is "STEGO-APPEND-V1" in bytes
MAGIC_MARKER = b'\x53\x54\x45\x47\x4F\x2D\x41\x50\x50\x45\x4E\x44\x2D\x56\x31'
# We will use 8 bytes to store the length of our data
# 'Q' means 8-byte unsigned long long
LENGTH_HEADER_FORMAT = '>Q' # Big-endian
LENGTH_HEADER_SIZE = struct.calcsize(LENGTH_HEADER_FORMAT)

def encode(data_to_hide: bytes, cover_file: str, output_file: str):
    """
    Hides data by appending it to the end of the cover file.
    Format: [CoverFileBytes][MagicMarker][DataLength][Data]
    """
    try:
        cover_data = read_bytes(cover_file)
        
        # 1. Create the 8-byte length header
        data_length_header = struct.pack(LENGTH_HEADER_FORMAT, len(data_to_hide))
        
        # 2. Assemble the full payload to write
        payload = cover_data + MAGIC_MARKER + data_length_header + data_to_hide
        
        # 3. Write to the new file
        write_bytes(output_file, payload)
        logging.info(f"Append-encode successful. Output: {output_file}")
        
    except Exception as e:
        logging.error(f"Append-encode failed: {e}")
        raise

def decode(stego_file: str) -> bytes:
    """
    Extracts data hidden with the append method.
    """
    try:
        stego_data = read_bytes(stego_file)
        
        # 1. Find the magic marker (search from the end)
        marker_index = stego_data.rfind(MAGIC_MARKER)
        
        if marker_index == -1:
            raise ValueError("Steganography marker not found. No hidden data.")
            
        # 2. Find the start of the length header
        header_start = marker_index + len(MAGIC_MARKER)
        
        # 3. Read the 8-byte length header
        header_end = header_start + LENGTH_HEADER_SIZE
        data_length_header = stego_data[header_start:header_end]
        
        # 4. Unpack the header to get the data length
        data_length = struct.unpack(LENGTH_HEADER_FORMAT, data_length_header)[0]
        
        # 5. Read the data
        data_start = header_end
        data_end = data_start + data_length
        hidden_data = stego_data[data_start:data_end]
        
        # 6. Final sanity check
        if len(hidden_data) != data_length:
            raise ValueError("Data corruption. Expected length does not match found length.")
            
        logging.info("Append-decode successful.")
        return hidden_data
        
    except Exception as e:
        logging.error(f"Append-decode failed: {e}")
        raise