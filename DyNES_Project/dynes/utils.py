class Padding:
    BLOCK_SIZE = 8  # 64-bit block size

    @staticmethod
    def pad(data: bytes) -> bytes:
        """Appends PKCS7 padding."""
        padding_len = Padding.BLOCK_SIZE - (len(data) % Padding.BLOCK_SIZE)
        padding = bytes([padding_len] * padding_len)
        return data + padding

    @staticmethod
    def unpad(data: bytes) -> bytes:
        """Removes PKCS7 padding."""
        if not data:
            return data
        padding_len = data[-1]
        if padding_len < 1 or padding_len > Padding.BLOCK_SIZE:
            # In case of wrong key, padding might look garbage
            return data 
        return data[:-padding_len]