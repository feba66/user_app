from sqlalchemy import Column, Integer, String
from user_app.db import Base
from enum import Enum


class Permissions(Enum):
    BANNED = 1
    USER = 2
    ADMIN = 3


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    password_hash = Column(String(96))
    password_salt = Column(String(64))
    permissions = Column(Integer)
    # last_login = Column(Integer)

    def __init__(self, name=None, email=None, password_hash=None, password_salt=None):
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.password_salt = password_salt
        self.permissions = Permissions.USER.value

    def set_perms(self, perm: list[Permissions]):
        self.permissions = sum([2**p.value for p in perm])

    def get_perms(self):
        return [p for p in Permissions if self.permissions & 2**p.value]

    def set_perm(self, perm: Permissions, value: bool):
        if value:
            self.permissions |= 2**perm.value
        else:
            self.permissions &= ~2**perm.value

    def has_perm(self, perm: Permissions):
        return self.permissions & 2**perm.value

    def __repr__(self):
        return f'<User {self.name!r}>'
