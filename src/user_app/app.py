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
session_storage = {}
clients = {"client_id": {"name": "Sample App", "secret": "client_secret", "grants": []}}
tokens = {}

# region functions


def login(request):
    name = request.form.get('username')
    password = request.form.get('password')

    user = userstore.login_user(name, password)
    if isinstance(user, Error):
        return False, user.message
    return True, user


def register(request):
    name = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    user = userstore.register_user(name, password, email)
    if isinstance(user, Error):
        return False, user.message
    return True, user


def get_session_data():
    test_cookie = request.cookies.get(SESSION_COOKIE_NAME, None)
    if test_cookie and test_cookie in session_storage:
        return session_storage[test_cookie], test_cookie
    else:
        return None, None


def make_session_cookie(data: dict = {}):
    while (key := random_string_generator(64)) in session_storage:
        pass
    session_storage[key] = data
    return key


def response_with_cookie(response, cookie_key=None):
    if not cookie_key or cookie_key not in session_storage:
        cookie_key = make_session_cookie()
    resp = make_response(response)
    resp.set_cookie(SESSION_COOKIE_NAME, cookie_key, expires=datetime.datetime.now() +
                    datetime.timedelta(hours=1), httponly=True, samesite="Strict", secure=False)
    return resp

# endregion


# region routes
@app.route('/register', methods=['GET', 'POST'])
def register_route():
    """register page which should return a form to register"""
    session_data, session_cookie = get_session_data()
    # already logged in
    if session_data and "id" in session_data:
        return redirect(url_for('index'))

    # not logged in
    if request.method == 'POST':
        success, user = register(request)
        # valid registration
        if success:
            if session_cookie:
                session_data["id"] = user.id
                session_data["name"] = user.name
            else:
                session_cookie = make_session_cookie({"id": user.id, "name": user.name})
            if "state" in session_data and not "code" in session_data and "client_id" in session_data and "scope" in session_data:
                session_data["code"] = random_string_generator(32)
                clients[session_data["client_id"]]["grants"].append({"code": session_data["code"], "scope": session_data["scope"], "user_id": user.id})
                return response_with_cookie(redirect(f"{session_data['redirect_uri']}?code={session_data['code']}&state={session_data['state']}"), session_cookie)

            return response_with_cookie(redirect(url_for('index')), session_cookie)
        # invalid registration
        return render_template('register.html', error=user)
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login_route():
    """login page which should return a form to login"""
    session_data, session_cookie = get_session_data()
    # already logged in
    if session_data and "id" in session_data:
        return redirect(url_for('index'))

    # not logged in
    if request.method == 'POST':
        success, obj = login(request)
        if success:
            if session_cookie:
                session_data["id"] = obj.id
                session_data["name"] = obj.name
            else:
                session_cookie = make_session_cookie({"id": obj.id, "name": obj.name})
            if "state" in session_data and not "code" in session_data and "client_id" in session_data and "scope" in session_data and "redirect_uri" in session_data:
                session_data["code"] = random_string_generator(32)
                clients[session_data["client_id"]]["grants"].append(
                    {"code": session_data["code"], "scope": session_data["scope"], "user_id": session_data["id"]})
                return response_with_cookie(redirect(f"{session_data["redirect_uri"]}?code={session_data['code']}&state={session_data['state']}"), session_cookie)
            return response_with_cookie(redirect(url_for('index')), session_cookie)
        else:
            return render_template('login.html', error=obj)
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    """logout route which should clear the session and redirect to the index page"""
    session_data, session_cookie = get_session_data()
    if not session_cookie or not session_cookie in session_storage:
        return redirect(url_for('index'))

    del session_storage[session_cookie]

    resp = make_response(redirect(url_for('index')))
    resp.set_cookie(SESSION_COOKIE_NAME, "", expires=0)
    return resp


@app.route("/delete")
def delete():
    """ delete user route which should delete the user from the userstore and redirect to the index page"""
    session_data, session_cookie = get_session_data()
    if not session_cookie or not session_cookie in session_storage or not "id" in session_data:
        return redirect(url_for('index'))

    user_id = session_data['id']
    userstore.delete_user(user_id)
    return logout()


@app.route('/user')
def user():
    """user page which should return the name and email of the user if logged in"""
    session_data, session_cookie = get_session_data()
    if session_data and "id" in session_data:
        user = userstore.get_user(session_data["id"])
        return response_with_cookie(render_template('user.html', username=user.name, email=user.email), session_cookie)
    else:
        return redirect(url_for('login_route'))


@app.route('/')
def index():
    session_data, session_cookie = get_session_data()
    if session_data and "name" in session_data:
        return response_with_cookie(render_template('index.html', username=session_data["name"]), session_cookie)
    return render_template('index.html')


@app.route('/auth', methods=['GET'])
def auth():
    session_data, session_cookie = get_session_data()
    rt, cid, ruri = request.args.get("response_type"), request.args.get("client_id"), request.args.get("redirect_uri")
    sc, st = request.args.get("scope"), request.args.get("state")
    if cid and not cid in clients:
        return "Invalid client id."
    if rt != None and cid != None and ruri != None and sc != None and st != None:
        if session_data and "id" in session_data:
            session_data["state"] = st
            session_data["client_id"] = cid
            session_data["scope"] = sc
            session_data["code"] = random_string_generator(32)
            clients[session_data["client_id"]]["grants"].append({"code": session_data["code"], "scope": session_data["scope"], "user_id": session_data["id"]})
            return response_with_cookie(redirect(f"{ruri}?code={session_data["code"]}&state={st}"), session_cookie)
        else:
            if not session_cookie:
                session_cookie = make_session_cookie({"state": st, "client_id": cid, "scope": sc, "redirect_uri": ruri})
            else:
                session_data["state"] = st
                session_data["client_id"] = cid
                session_data["scope"] = sc
                session_data["redirect_uri"] = ruri
            return response_with_cookie(redirect(url_for('login_route')), session_cookie)
    return "You are missing a required argument."  # redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ", code=302)


@app.route('/token', methods=['POST'])
def token_route():
    gt, cid, csec = request.form.get("grant_type"), request.form.get("client_id"), request.form.get("client_secret")
    ruri, code = request.form.get("redirect_uri"), request.form.get("code")
    if gt != None and cid != None and csec != None and ruri != None and code != None:
        if gt == "authorization_code":
            if cid in clients and clients[cid]["secret"] == csec:
                for grant in clients[cid]["grants"]:
                    if grant["code"] == code:
                        token = random_string_generator(32)
                        tokens[token] = {}
                        tokens[token]["user_id"] = grant["user_id"]
                        tokens[token]["client"] = cid
                        tokens[token]["scope"] = grant["scope"]
                        tokens[token]["expires"] = datetime.datetime.now()+datetime.timedelta(hours=1)

                        return json.dumps({"access_token": token, "token_type": "bearer", "expires_in": 3600, "scope": grant["scope"]})
                return "Invalid code."
            return "Invalid client id or secret."
        return "Invalid grant type."
    return "You are missing a required argument."
# endregion


@app.route("/api/user")
def api_user():
    token = request.headers.get("Authorization").removeprefix("Bearer ")
    if token != None and token in tokens:
        return json.dumps({"name": userstore.get_user(tokens[token]["user_id"]).name})
    return "Invalid token."

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == '__main__':
    app.run()
