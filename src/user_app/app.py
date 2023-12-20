from flask import Flask, redirect, render_template, request, session, url_for
from user_app.userstore import UserStore
from user_app.classes import random_string_generator
from user_app.db import db_session, init_db
from user_app.models import User
# flask app that uses the userstore to register and login users, and stores the user id in the session
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


# register page which should return a form to register


@app.route('/register', methods=['GET', 'POST'])
def register():
    # check the request method
    if request.method == 'POST':
        # get the name and password from the request
        name = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        # register the user
        user = userstore.register_user(name, password, email)
        if isinstance(user, str):
            # return an error message
            return render_template('register.html', error=user)
        # store user id in session
        session['user_id'] = user.id
        session['user_name'] = user.name
        # redirect to the login page
        return redirect(url_for('index'))
    else:
        # return the register form
        return render_template('register.html')

# login page which should return a form to login


@app.route('/login', methods=['GET', 'POST'])
def login():
    # check the request method
    if request.method == 'POST':
        # get the name and password from the request
        name = request.form.get('username')
        password = request.form.get('password')
        # login the user
        user = userstore.login_user(name, password)
        if isinstance(user, str):
            # return an error message
            return render_template('login.html', error=user)
        # store user id in session
        session['user_id'] = user.id
        session['user_name'] = user.name
        # redirect to the index page
        return redirect(url_for('index'))
    else:
        # return the login form
        return render_template('login.html')

# logout route which should clear the session and redirect to the index page


@app.route('/logout')
def logout():
    # clear the session
    session.clear()
    # redirect to the index page
    return redirect(url_for('index'))
# delete user route which should delete the user from the userstore and redirect to the index page


@app.route("/delete")
def delete():
    # get the user id from the session
    user_id = session['user_id']
    if user_id is None:
        return redirect(url_for('index'))
    # delete the user from the userstore
    userstore.delete_user(user_id)
    # clear the session
    session.clear()
    # redirect to the index page
    return redirect(url_for('index'))
# user page which should return the name and email of the user


@app.route('/user')
def user():
    # get the user id from the session
    user_id = session.get('user_id')
    # get the user from the userstore
    user = userstore.get_user(user_id)
    # return the user page with the user

    return render_template('user.html', username=user.name if user else None, email=user.email if user else None)


@app.route('/')
def index():
    return render_template('index.html')


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == '__main__':
    app.run()
