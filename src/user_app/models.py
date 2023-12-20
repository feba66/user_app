from sqlalchemy import Column, Integer, String
from user_app.db import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    password_hash = Column(String(96))
    password_salt = Column(String(64))

    def __init__(self, name=None, email=None, password_hash=None, password_salt=None):
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.password_salt = password_salt

    def __repr__(self):
        return f'<User {self.name!r}>'
