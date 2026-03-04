import logging
import os
import wave
from PIL import Image

# --- Helper Functions for LSB ---

def _int_to_bytes(n):
    """Converts a 32-bit integer into 4 bytes (big-endian)."""
    return n.to_bytes(4, 'big')

def _bytes_to_int(b):
    """Converts 4 bytes (big-endian) into a 32-bit integer."""
    return int.from_bytes(b, 'big')

def _data_to_bits(data: bytes) -> str:
    """Converts a bytestring into a string of bits (e.g., '01010101')."""
    return ''.join(format(byte, '08b') for byte in data)

def _bits_to_bytes(bits: str) -> bytes:
    """Converts a string of bits into a bytestring."""
    if len(bits) % 8 != 0:
        bits = bits[:-(len(bits) % 8)] # Discard incomplete byte
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

def _set_lsb(value, bit):
    """Sets the LSB of a value (int) to 0 or 1."""
    return (value & 0xFE) | bit

# --- Image LSB ---

def _encode_image(data_to_hide: bytes, cover_image: str, output_image: str):
    """Hides data in the LSBs of a PNG image."""
    try:
        img = Image.open(cover_image)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        pixels = img.load()
        width, height = img.size
        
        # 1. Add 4-byte (32-bit) length header to the data
        data_length = _int_to_bytes(len(data_to_hide))
        full_data = data_length + data_to_hide
        
        # 2. Convert data to a bit string
        data_bits = _data_to_bits(full_data)
        data_len = len(data_bits)
        
        # 3. Check for capacity (3 bits per pixel: R, G, B)
        max_capacity = width * height * 3
        if data_len > max_capacity:
            raise ValueError(f"Message is too large. Max: {max_capacity} bits. Need: {data_len} bits.")
            
        bit_index = 0
        for y in range(height):
            for x in range(width):
                if bit_index < data_len:
                    r, g, b = pixels[x, y]
                    
                    # Embed 3 bits per pixel
                    if bit_index < data_len:
                        r = _set_lsb(r, int(data_bits[bit_index]))
                        bit_index += 1
                    if bit_index < data_len:
                        g = _set_lsb(g, int(data_bits[bit_index]))
                        bit_index += 1
                    if bit_index < data_len:
                        b = _set_lsb(b, int(data_bits[bit_index]))
                        bit_index += 1
                        
                    pixels[x, y] = (r, g, b)
                else:
                    break # All data embedded
            if bit_index >= data_len:
                break
        
        # Must save as PNG to be lossless
        img.save(output_image, "PNG")
        logging.info(f"Image LSB encode successful. Output: {output_image}")

    except Exception as e:
        logging.error(f"Image LSB encode failed: {e}")
        raise

def _decode_image(stego_image: str) -> bytes:
    """Extracts data from the LSBs of a PNG image."""
    try:
        img = Image.open(stego_image)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        pixels = img.load()
        width, height = img.size
        bits = ""
        
        # 1. First, extract the 32-bit length header
        header_bits_needed = 32
        bits_extracted = 0
        
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                
                if bits_extracted < header_bits_needed:
                    bits += str(r & 1); bits_extracted += 1
                if bits_extracted < header_bits_needed:
                    bits += str(g & 1); bits_extracted += 1
                if bits_extracted < header_bits_needed:
                    bits += str(b & 1); bits_extracted += 1
                
                if bits_extracted == header_bits_needed:
                    break
            if bits_extracted == header_bits_needed:
                break
        
        data_length_bytes = _bits_to_bytes(bits)
        data_length = _bytes_to_int(data_length_bytes)
        
        # 2. Now extract the rest of the data
        total_bits_to_read = header_bits_needed + (data_length * 8)
        bits = "" # Reset bits
        bits_extracted = 0

        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                
                if bits_extracted < total_bits_to_read:
                    bits += str(r & 1); bits_extracted += 1
                if bits_extracted < total_bits_to_read:
                    bits += str(g & 1); bits_extracted += 1
                if bits_extracted < total_bits_to_read:
                    bits += str(b & 1); bits_extracted += 1
                
                if bits_extracted == total_bits_to_read:
                    break
            if bits_extracted == total_bits_to_read:
                break
        
        # 3. Convert bits to data
        full_data_bytes = _bits_to_bytes(bits)
        # 4. Return data *without* the 4-byte header
        return full_data_bytes[4:]

    except Exception as e:
        logging.error(f"Image LSB decode failed: {e}")
        raise

# --- WAV LSB ---

def _encode_wav(data_to_hide: bytes, cover_wav: str, output_wav: str):
    """Hides data in the LSBs of a WAV audio file."""
    try:
        with wave.open(cover_wav, 'rb') as wav_in:
            params = wav_in.getparams()
            n_frames = wav_in.getnframes()
            frames = wav_in.readframes(n_frames)
            
            # 1. Add 4-byte length header
            data_length = _int_to_bytes(len(data_to_hide))
            full_data = data_length + data_to_hide
            data_bits = _data_to_bits(full_data)
            data_len = len(data_bits)
            
            # 2. Check capacity (1 bit per frame byte)
            max_capacity = len(frames)
            if data_len > max_capacity:
                raise ValueError(f"Message is too large. Max: {max_capacity} bits. Need: {data_len} bits.")

            # 3. Embed data
            frames_list = bytearray(frames)
            for i in range(data_len):
                frames_list[i] = _set_lsb(frames_list[i], int(data_bits[i]))
            
            new_frames = bytes(frames_list)
            
            # 4. Write new WAV file
            with wave.open(output_wav, 'wb') as wav_out:
                wav_out.setparams(params)
                wav_out.writeframes(new_frames)
                
        logging.info(f"WAV LSB encode successful. Output: {output_wav}")

    except Exception as e:
        logging.error(f"WAV LSB encode failed: {e}")
        raise

def _decode_wav(stego_wav: str) -> bytes:
    """Extracts data from the LSBs of a WAV file."""
    try:
        with wave.open(stego_wav, 'rb') as wav_in:
            n_frames = wav_in.getnframes()
            frames = wav_in.readframes(n_frames)
            
            # 1. Extract 32-bit length header
            bits = ""
            for i in range(32):
                bits += str(frames[i] & 1)
            
            data_length = _bytes_to_int(_bits_to_bytes(bits))
            total_bits_to_read = 32 + (data_length * 8)
            
            if total_bits_to_read > len(frames):
                raise ValueError("Data corruption. Header indicates more data than available.")
                
            # 2. Extract data
            bits = ""
            for i in range(total_bits_to_read):
                bits += str(frames[i] & 1)
                
            # 3. Convert and return
            full_data_bytes = _bits_to_bytes(bits)
            return full_data_bytes[4:] # Return data without the 4-byte header

    except Exception as e:
        logging.error(f"WAV LSB decode failed: {e}")
        raise

# --- Public "Smart" Functions ---

LOSSLESS_IMAGE_EXT = ['.png', '.bmp']
LOSSLESS_AUDIO_EXT = ['.wav']

def encode(data_to_hide: bytes, cover_file: str, output_file: str):
    """
    Public function to LSB-encode data.
    Automatically chooses the right method based on file extension.
    """
    ext = os.path.splitext(cover_file)[1].lower()
    
    if ext in LOSSLESS_IMAGE_EXT:
        _encode_image(data_to_hide, cover_file, output_file)
    elif ext in LOSSLESS_AUDIO_EXT:
        _encode_wav(data_to_hide, cover_file, output_file)
    else:
        raise ValueError(f"Unsupported LSB file type: {ext}")

def decode(stego_file: str) -> bytes:
    """
    Public function to LSB-decode data.
    Automatically chooses the right method based on file extension.
    """
    ext = os.path.splitext(stego_file)[1].lower()
    
    if ext in LOSSLESS_IMAGE_EXT:
        return _decode_image(stego_file)
    elif ext in LOSSLESS_AUDIO_EXT:
        return _decode_wav(stego_file)
    else:
        raise ValueError(f"Unsupported LSB file type: {ext}")