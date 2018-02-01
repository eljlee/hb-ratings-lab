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


@app.route('/users/<user_id>')
def show_profile(user_id):
    """Shows user's profile page."""

    user = User.query.filter(User.user_id == user_id).first()
    # optimize querying later with joinedload
    return render_template('user_profile.html',
                           user=user)


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
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("Successfully registered!")
        return redirect('/')

    else:
        flash("Sorry, that email is already in use.")
        return redirect('/registration-form')


@app.route('/movies')
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by(Movie.title).all()

    return render_template('movie_list.html',
                           movies=movies)


@app.route('/movies/<movie_id>')
def show_movie_profile(movie_id):
    """Shows detailed information about a movie."""

    movie = Movie.query.filter(Movie.movie_id == movie_id).first()

    return render_template('movie_profile.html',
                           movie=movie)


@app.route('/rate/<movie_id>', methods=["POST"])
def update_rating(movie_id):
    """Allows user to add or edit a rating for current movie."""

    # user's rating needs to check database by user_email if user has
    # rated this movie
    score = request.form.get('score')

    movie = Movie.query.filter(Movie.movie_id == movie_id).first()

    if 'user_id' in session:
        user_id = session['user_id']
        # Check if rating exists for this user and this movie
        rating = Rating.query.filter(Rating.user_id == user_id and
                                     Rating.movie_id == movie_id).first()

        if rating:
            rating.score = score
            db.session.commit()
            flash("Your movie rating has been updated.")

        else:
            new_rating = Rating(user_id=user_id,
                                movie_id=movie_id,
                                score=score)
            db.session.add(new_rating)
            db.session.commit()
            #New_rating object at movie table, grab title
            flash("Thanks for rating {}!".format(new_rating.movie.title))

    return render_template('movie_profile.html', movie=movie)


@app.route('/login')
def show_login():
    """Shows user the login form."""

    return render_template('login_form.html')


@app.route('/login', methods=["POST"])
def login():
    """Checks if user enters valid login info."""

    email = request.form.get('user_email')
    password = request.form.get('user_password')

    user = User.query.filter(User.email == email).first()  # returns a user obj

    if user is not None and user.password == password:

        #hold user_id in session
        session['user_id'] = user.user_id  # this works because user is an obj
        flash("Successfully logged in.")

        return redirect('/users/{id}'.format(id=user.user_id))

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
