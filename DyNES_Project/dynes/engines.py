class CryptoEngine:
    """
    The Round Function F(R, K) implementation.
    Input: 32-bit Integer Data, 32-bit Integer Key
    Output: 32-bit Integer
    """

    @staticmethod
    def standard_math(right_block: int, sub_key: int) -> int:
        """
        Uses classic bitwise operations: XOR and Circular Shift (Rotate).
        """
        # XOR with key
        mixed = right_block ^ sub_key
        
        # Circular Left Rotate by 5 bits (on 32-bit int)
        # ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF
        rotated = ((mixed << 5) | (mixed >> 27)) & 0xFFFFFFFF
        
        return rotated

    @staticmethod
    def chaos_math(right_block: int, sub_key: int) -> int:
        """
        Uses the Logistic Map: x_new = r * x * (1 - x)
        We normalize the integer to a float (0-1), apply chaos, and map back.
        """
        # Combine data and key to seed the chaos
        seed = (right_block ^ sub_key) & 0xFFFFFFFF
        
        # Normalize to 0.0 < x < 1.0 (avoid 0 and 1 exactly)
        x = (seed / (2**32)) 
        if x == 0: x = 0.1
        if x == 1: x = 0.9

        # Logistic Map Parameter (Chaos usually happens > 3.57)
        r = 3.99 

        # Iterate chaos map 5 times to diverge
        for _ in range(5):
            x = r * x * (1 - x)

        # Convert back to 32-bit integer
        return int(x * (2**32)) & 0xFFFFFFFF