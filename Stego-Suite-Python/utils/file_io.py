import logging

def read_bytes(filename: str) -> bytes:
    """
    Reads the entire content of a file as bytes.
    """
    try:
        with open(filename, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"File not found: {filename}")
        raise
    except Exception as e:
        logging.error(f"Error reading file {filename}: {e}")
        raise

def write_bytes(filename: str, data: bytes):
    """
    Writes a bytestring to a file, overwriting any existing file.
    """
    try:
        with open(filename, 'wb') as f:
            f.write(data)
    except Exception as e:
        logging.error(f"Error writing to file {filename}: {e}")
        raise