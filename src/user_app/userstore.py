from user_app.models import User, random_string_generator
from pyargon2 import hash

# class which stores users in a dictionary with the id as key, with a function to add a new user and generate the salt. Store the pepper in the class as well. auto increment the user ids


class UserStore:
    users: dict[int, User]
    pepper: str
    next_id: int
    __parralelism: int = 1
    __memory_cost: int = 8192
    __hash_len: int = 64
    __time_cost: int = 128

    def __init__(self, user=None, pepper=None, next_id=None):
        self.users = {} if user is None else user
        self.pepper = random_string_generator(64) if pepper is None else pepper
        self.next_id = 1 if next_id is None else next_id

    def register_user(self, name, password, email):
        salt = random_string_generator(64)
        password_hash = hash(password, salt, self.pepper, self.__hash_len,
                             self.__time_cost, self.__memory_cost, self.__parralelism, encoding='b64')
        user = User(self.next_id, name, email, password_hash, salt)
        self.users[self.next_id] = user
        self.next_id += 1
        return user

    def login_user(self, name, password):
        user: User = self.get_user_by_name(name)
        if user is None:
            return None
        password_hash = hash(password, user.password_salt, self.pepper, self.__hash_len,
                             self.__time_cost, self.__memory_cost, self.__parralelism, encoding='b64')
        if password_hash == user.password_hash:
            return user
        return None

    def get_user(self, id):
        return self.users[id]

    def get_user_by_name(self, name):
        for user in self.users.values():
            if user.name == name:
                return user
        return None

    def __iter__(self):
        return iter(self.users.values())
