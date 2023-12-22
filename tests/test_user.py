
from user_app.models import Permissions, User


def test_userperms():
    user = User("", "", "", "")
    user.set_perms([Permissions.USER, Permissions.ADMIN, Permissions.BANNED])
    perms = user.get_perms()
    assert Permissions.BANNED in perms
    assert Permissions.USER in perms
    assert Permissions.ADMIN in perms
    assert len(perms) == 3


def test_userperm():
    user = User("", "", "", "")
    user.set_perms([Permissions.USER, Permissions.ADMIN, Permissions.BANNED])

    perms = user.get_perms()
    assert Permissions.BANNED in perms
    assert Permissions.USER in perms
    assert Permissions.ADMIN in perms
    assert len(perms) == 3

    user.set_perm(Permissions.BANNED, False)

    perms = user.get_perms()
    assert Permissions.USER in perms
    assert Permissions.ADMIN in perms
    assert len(perms) == 2

    user.set_perm(Permissions.BANNED, True)

    perms = user.get_perms()
    assert Permissions.BANNED in perms
    assert Permissions.USER in perms
    assert Permissions.ADMIN in perms
    assert len(perms) == 3


if __name__ == "__main__":
    test_userperm()
