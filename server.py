"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template('homepage.html')


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template('user_list.html', users=users)


@app.route('/registration-form')
def show_reg_form():
    """Displays registration form."""

    return render_template('registration_form.html')


@app.route('/new-user', methods=["POST"])
def validate_user():
    """Checks if user is already registered, if not, register new user."""

    email = request.form.get("new_user_email")
    password = request.form.get("new_user_password")

    validation_entry = User.query.filter(User.email == email).first()

    if validation_entry is None:
        email = User(email=email, password=password)
        db.session.add(email)
        db.session.commit()

        flash("Successfully registered!")
        return redirect('/')

    else:
        flash("Sorry, that email is already in use.")
        return redirect('/registration-form')


@app.route('/login')
def show_login():
    """Shows user the login form."""

    return render_template("login_form.html")


@app.route('/login', methods=["POST"])
def login():
    """Checks if user enters valid login info."""

    email = request.form.get('user_email')
    password = request.form.get('user_password')

    valid_info = User.query.filter(User.email == email).first()

    if valid_info.email == email and valid_info.password == password:
        session['user_id'] = request.form.get('user_email')
        flash("Successfully logged in.")
        return redirect('/')

    else:
        flash("Sorry, incorrect login info.")
        return redirect('/login')


@app.route('/logout')
def logout():
    """Logs user out of website."""

    session.clear()
    flash("You have logged out.")
    return redirect('/')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
