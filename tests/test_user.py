
from user_app.models import Permissions, User


def test_userperms():
    user = User("", "", "", "")
    user.set_perms([Permissions.USER, Permissions.ADMIN, Permissions.BANNED])

    assert user.get_perms() == [Permissions.USER, Permissions.ADMIN, Permissions.BANNED]


if __name__ == "__main__":
    test_userperms()
