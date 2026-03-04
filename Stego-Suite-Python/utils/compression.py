import zlib
import logging

def compress(data: bytes) -> bytes:
    """
    Compresses data using zlib with maximum compression.
    """
    try:
        # Level 9 provides the best compression
        return zlib.compress(data, level=9)
    except Exception as e:
        logging.error(f"Compression failed: {e}")
        raise

def decompress(data: bytes) -> bytes:
    """
    Decompresses data using zlib.
    """
    try:
        return zlib.decompress(data)
    except zlib.error as e:
        logging.error(f"Decompression failed: {e}")
        # This is a common error if the password was wrong,
        # leading to corrupt decrypted data.
        raise ValueError("Decompression failed. Data may be corrupt or wrong password.")
    except Exception as e:
        logging.error(f"Decompression failed: {e}")
        raise