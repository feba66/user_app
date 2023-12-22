import datetime
import json
from flask import Flask, make_response, redirect, render_template, request, session, url_for
from user_app.userstore import UserStore, Error
from user_app.classes import random_string_generator
from user_app.db import db_session, init_db
from user_app.models import User


"""flask app that uses the userstore to register and login users, and stores the user id in the session"""

SESSION_COOKIE_NAME = "test"

app = Flask(__name__)
app.secret_key = random_string_generator(64)
init_db()
try:
    with open('pepper.txt', 'r') as f:
        pepper = f.read()
except FileNotFoundError:
    pepper = random_string_generator(64)
    with open('pepper.txt', 'w') as f:
        f.write(pepper)


userstore = UserStore(db_session=db_session, pepper=pepper)


# region functions
def login(request, session):
    name = request.form.get('username')
    password = request.form.get('password')

    user = userstore.login_user(name, password)
    if isinstance(user, Error):
        return False, user.message
    return True, user


def register(request, session):
    name = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    user = userstore.register_user(name, password, email)
    if isinstance(user, Error):
        return False, user.message
    return True, user


def get_session_cookie():
    test_cookie = request.cookies.get(SESSION_COOKIE_NAME, None)
    return json.loads(test_cookie) if test_cookie else None


def make_session_cookie(obj: User):
    return json.dumps({"name": obj.name, "id": obj.id})
# endregion


# region routes
@app.route('/register', methods=['GET', 'POST'])
def register_route():
    """register page which should return a form to register"""
    if request.method == 'POST':
        success, user = register(request, session)
        if success:
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie(SESSION_COOKIE_NAME, make_session_cookie(user), expires=datetime.datetime.now() +
                            datetime.timedelta(hours=1), httponly=True, samesite="Strict", secure=False)
            return resp
        # hier weiter refactorn
        return render_template('register.html', error=user)
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login_route():
    """login page which should return a form to login"""
    if request.method == 'POST':
        success, obj = login(request, session)
        if success:
            resp = make_response(redirect(url_for('index', username=obj.name)))
            resp.set_cookie(SESSION_COOKIE_NAME, make_session_cookie(obj), expires=datetime.datetime.now() +
                            datetime.timedelta(hours=1), httponly=True, samesite="Strict", secure=False)
            return resp
        else:
            return render_template('login.html', error=obj)
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    """logout route which should clear the session and redirect to the index page"""
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie(SESSION_COOKIE_NAME, "", expires=0)
    return resp


@app.route("/delete")
def delete():
    """ delete user route which should delete the user from the userstore and redirect to the index page"""
    session_cookie = get_session_cookie()
    user_id = session_cookie['id']
    if user_id is None:
        return redirect(url_for('index'))
    userstore.delete_user(user_id)
    return logout()


@app.route('/user')
def user():
    """user page which should return the name and email of the user if logged in"""
    test_cookie = get_session_cookie()
    if test_cookie:
        user = userstore.get_user(test_cookie["id"])
        return render_template('user.html', username=user.name, email=user.email)
    else:
        return redirect(url_for('login_route'))


@app.route('/')
def index():
    session_cookie = get_session_cookie()
    if session_cookie:
        return render_template('index.html', username=session_cookie["name"])
    return render_template('index.html')


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        name = request.form.get('username')
        password = request.form.get('password')

        user = userstore.login_user(name, password)
        if isinstance(user, str):
            return render_template('login.html', error=user)
        session['user_id'] = user.id
        session['user_name'] = user.name

        if "redirect_uri" in session and "state" in session:
            ruri = session["redirect_uri"]
            session.pop("redirect_uri")
            return redirect(f"{ruri}?code=1234&state={session['state']}")
        else:
            return redirect(url_for('index'))
    else:
        rt, cid, ruri = request.args.get("response_type"), request.args.get("client_id"), request.args.get("redirect_uri")
        sc, st = request.args.get("scope"), request.args.get("state")
        if rt != None and cid != None and ruri != None and sc != None and st != None:
            print(session)
            if "user_id" in session:
                test_cookie = request.cookies.get(SESSION_COOKIE_NAME, None)
                # success
                return redirect(f"{ruri}?code=1234")
            else:
                session["state"] = st
                session["response_type"] = rt
                session["client_id"] = cid
                session["redirect_uri"] = ruri
                session["scope"] = sc

            return render_template("login.html")
        return "hello,world"  # redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ", code=302)
# endregion


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == '__main__':
    app.run()
