from user_app.userstore import UserStore
from user_app.models import random_string_generator


def test_userstore():
    store = UserStore()
    password = random_string_generator(32)
    user = store.register_user("test", password)
    print(store.get_user_by_name("test"))
    assert store.get_user(user.id).name == "test"

    assert store.login_user("test", password) == user
    assert store.login_user("test", "wrong password") is None


if __name__ == "__main__":
    test_userstore()
