import hashlib

class KeyManager:
    @staticmethod
    def generate_subkeys(password: str, rounds: int) -> list:
        """
        Expands a string password into a list of 32-bit integer subkeys.
        """
        subkeys = []
        password_bytes = password.encode('utf-8')

        for i in range(rounds):
            # Create a unique hash for each round using the password + round index
            # We use SHA-256
            hasher = hashlib.sha256()
            hasher.update(password_bytes)
            hasher.update(str(i).encode('utf-8'))
            digest = hasher.digest()

            # Take the first 4 bytes of the hash to make a 32-bit integer
            # We use big-endian byte order
            key_int = int.from_bytes(digest[:4], byteorder='big')
            subkeys.append(key_int)

        return subkeys