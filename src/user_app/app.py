from flask import Flask, redirect, render_template, request, session, url_for
from user_app.userstore import UserStore
from user_app.classes import random_string_generator
from user_app.db import db_session, init_db
from user_app.models import User
"""flask app that uses the userstore to register and login users, and stores the user id in the session"""
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


@app.route('/register', methods=['GET', 'POST'])
def register():
    """register page which should return a form to register"""
    if request.method == 'POST':
        name = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        user = userstore.register_user(name, password, email)
        if isinstance(user, str):
            return render_template('register.html', error=user)
        session['user_id'] = user.id
        session['user_name'] = user.name
        return redirect(url_for('index'))
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """login page which should return a form to login"""
    if request.method == 'POST':
        name = request.form.get('username')
        password = request.form.get('password')

        user = userstore.login_user(name, password)
        if isinstance(user, str):
            return render_template('login.html', error=user)
        session['user_id'] = user.id
        session['user_name'] = user.name
        return redirect(url_for('index'))
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    """logout route which should clear the session and redirect to the index page"""
    session.clear()
    return redirect(url_for('index'))


@app.route("/delete")
def delete():
    """ delete user route which should delete the user from the userstore and redirect to the index page"""
    user_id = session['user_id']
    if user_id is None:
        return redirect(url_for('index'))
    userstore.delete_user(user_id)
    session.clear()
    return redirect(url_for('index'))


@app.route('/user')
def user():
    """user page which should return the name and email of the user if logged in"""
    user_id = session.get('user_id')
    user = userstore.get_user(user_id)

    return render_template('user.html', username=user.name if user else None, email=user.email if user else None)


@app.route('/')
def index():
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
            if "user_id" in session:
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


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == '__main__':
    app.run()
