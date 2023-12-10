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


# # pw = random_string_generator(30)
# # st = random_string_generator(30)
# pepper = random_string_generator(64)
# pw = "3HJ7JYml0HCu1PuxOTzUu39mbO3k9V"
# st = "9ZEu6PJfaBIgKCxlOMgz2LXkOnokal"

# # p=1 avg: 1.84021938520018, min: 1.6767337420023978, max: 1.959805957012577
# print(pw)
# print(st)
# print(pepper)
# times = []
# for _ in range(10):
#     before = time.perf_counter()
#     h = hash(pw, st, parallelism=1, memory_cost=8192,
#              hash_len=64, time_cost=128, pepper=pepper)

#     after = time.perf_counter()
#     print(after - before)
#     times.append(after - before)

# print(f"avg: {sum(times)/len(times)}, min: {min(times)}, max: {max(times)}")
