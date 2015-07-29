"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/login', methods=["POST"])
def login():
    """Allows user to log in."""

    email = request.form.get("email")
    password = request.form.get("password")

    # check if user is in database
    user = User.query.filter_by(email=email).first()
    if not user:
        # add to database
        # Later, let's add separate sign-up page to get info
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

    session['email'] = email
    flash("Now logged in as %s" % session['email'])

    return redirect('/')


@app.route('/logout')
def logout():
    """Logs user out."""

    del session['email']
    flash("Logged out")

    return redirect('/')


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route('/users/<int:user_id>')
def user_details(user_id):
    """Show user profile"""

    user = User.query.get(user_id)

    joint_movieratings = db.session.query(Movie.title, Movie.movie_id, Rating.score).join(Rating)
    
    # returns list of users' ratings in tuple format
    # [(u'River Wild', 3), (u'Rumble in the Bronx', 4)]
    users_ratings = joint_movieratings.filter_by(user_id=user_id).order_by(Movie.title).all()


    return render_template("user.html", user=user, users_ratings=users_ratings)

@app.route('/movies')
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by(Movie.title).all()
    return render_template("movie_list.html", movies=movies)


@app.route('/movies/<int:movie_id>')
def movie_details(movie_id):
    """Show movie details"""

    movie = Movie.query.get(movie_id)

    movie_ratings = db.session.query(Rating.score, Rating.user_id).filter_by(movie_id=movie_id).all()

    # joint_movieratings = db.session.query(Movie.title, Rating.score).join(Rating)
    
    # # returns list of users' ratings in tuple format
    # # [(u'River Wild', 3), (u'Rumble in the Bronx', 4)]
    # users_ratings = joint_movieratings.filter_by(user_id=user_id).all()


    return render_template("movie.html", movie=movie, movie_ratings=movie_ratings)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()