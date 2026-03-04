import struct
import os
from dynes.utils import Padding
from dynes.engines import CryptoEngine
from dynes.key_manager import KeyManager

class DynesCipher:
    def __init__(self, password, rounds=16, engine_type='standard'):
        self.rounds = rounds
        self.engine_type = engine_type
        self.subkeys = KeyManager.generate_subkeys(password, rounds)
        
        # Select the function based on configuration
        if engine_type == 'chaos':
            self.f_function = CryptoEngine.chaos_math
        else:
            self.f_function = CryptoEngine.standard_math

    def _feistel_block(self, data_block, mode='encrypt'):
        """
        Processes a single 64-bit (8-byte) block.
        """
        # Unpack 8 bytes into two 32-bit integers (Left and Right)
        L, R = struct.unpack('>II', data_block)

        keys = self.subkeys
        if mode == 'decrypt':
            keys = keys[::-1] # Reverse keys for decryption

        for i in range(self.rounds):
            prev_L, prev_R = L, R
            
            # Feistel Operation: L_new = R_old; R_new = L_old XOR F(R_old, K)
            L = prev_R
            f_result = self.f_function(prev_R, keys[i])
            R = prev_L ^ f_result

        # Final swap is usually undone in standard Feistel (or simply swap L,R at output)
        # We pack them back as (R, L) effectively swapping them.
        return struct.pack('>II', R, L)

    def process_file(self, input_path, output_path, mode='encrypt'):
        if not os.path.exists(input_path):
            raise FileNotFoundError("Input file not found.")

        # Read all data
        with open(input_path, 'rb') as f:
            data = f.read()

        if mode == 'encrypt':
            data = Padding.pad(data)
        
        processed_data = bytearray()

        # Process in 8-byte chunks
        block_size = 8
        total_blocks = len(data) // block_size

        for i in range(total_blocks):
            chunk = data[i*block_size : (i+1)*block_size]
            processed_block = self._feistel_block(chunk, mode)
            processed_data.extend(processed_block)

        if mode == 'decrypt':
            processed_data = Padding.unpad(processed_data)

        with open(output_path, 'wb') as f:
            f.write(processed_data)
            
        return True