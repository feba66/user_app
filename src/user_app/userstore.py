from user_app.classes import random_string_generator
from pyargon2 import hash
from user_app.models import User

# class which stores users in a dictionary with the id as key, with a function to add a new user and generate the salt. Store the pepper in the class as well. auto increment the user ids


class UserStore:
    pepper: str
    __parralelism: int = 1
    __memory_cost: int = 8192
    __hash_len: int = 64
    __time_cost: int = 128
    db_session = None

    def __init__(self, pepper=None, db_session=None):
        self.pepper = random_string_generator(64) if pepper is None else pepper
        self.db_session = db_session

    def register_user(self, name, password, email):
        if User.query.filter(User.name == name).first():
            return "User already exists"
        if User.query.filter(User.email == email).first():
            return "Email already exists"
        salt = random_string_generator(64)
        password_hash = hash(password, salt, self.pepper, self.__hash_len,
                             self.__time_cost, self.__memory_cost, self.__parralelism, encoding='b64')
        user = User(name, email, password_hash, salt)
        self.db_session.add(user)
        self.db_session.commit()
        return user

    def login_user(self, name, password):
        user: User = self.get_user_by_name(name)
        if user is None:
            return "No such user"
        password_hash = hash(password, user.password_salt, self.pepper, self.__hash_len,
                             self.__time_cost, self.__memory_cost, self.__parralelism, encoding='b64')
        if password_hash == user.password_hash:
            return user
        return "Wrong password"

    def delete_user(self, id):
        user = self.get_user(id)
        if user:
            self.db_session.delete(user)
            self.db_session.commit()
            return "User deleted successfully"
        return "User not found"

    def get_user(self, id):
        return User.query.filter(User.id == id).first()

    def get_user_by_name(self, name):
        return User.query.filter(User.name == name).first()

    def __iter__(self):
        return iter(self.users.values())
