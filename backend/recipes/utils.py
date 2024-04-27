import random
import string


def generate_random_color():
    """
    Generate a random color in hex format.
    """
    return '#' + ''.join(random.choices(string.hexdigits[:-6], k=6))
