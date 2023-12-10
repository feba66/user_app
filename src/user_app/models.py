from dataclasses import dataclass
import time
from pyargon2 import hash


@dataclass
class User:
    id: int
    name: str
    email: str
    password_hash: str
    password_salt: str


# a random string generator using alphanumeric characters where you can give the lenth as argument


def random_string_generator(length):
    import random
    import string
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))
