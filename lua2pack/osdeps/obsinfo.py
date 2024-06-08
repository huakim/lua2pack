import random
import string
import time

def generate_random_hex(length=40):
    """
    Generate a random hex string of the specified length.

    Args:
        length (int): The desired length of the hex string. Default is 40.

    Returns:
        str: A random hex string of the specified length.
    """
    # Define the characters to use for the hex string
    hex_chars = string.hexdigits

    # Generate a list of random hex characters
    random_chars = [random.choice(hex_chars) for _ in range(length)]

    # Join the random characters into a string
    random_hex = ''.join(random_chars)

    return random_hex.lower()

def lua_code(args):
    return """
mtime = __get_current_timestamp()
commit = __random_hex_numbers()
"""

def generate_timestamp():
    return int(time.time())

def update_globals():
    return {
       '__random_hex_numbers':generate_random_hex,
       '__get_current_timestamp':generate_timestamp
    }
