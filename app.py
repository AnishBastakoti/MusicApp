from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request
from flask import jsonify
from session_management import set_user_session, clear_user_session
import os

app = Flask(__name__, template_folder='public', static_folder='public')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music_app.db'  # SQLite URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    artist = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('songs', lazy=True))

# Generate a random secret key with 24 bytes
secret_key = os.urandom(24)

# Convert the bytes to a string (for example, in hexadecimal format)
secret_key_hex = secret_key.hex()

# Use a secret key for session management
app.secret_key = secret_key_hex


# Create the 'uploads' folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')

    # Perform the search in your database and get results as a list
    results = perform_search(query)

    # Assuming results is a list of dictionaries
    return jsonify(results)

def perform_search(query):
    # Perform the search in your database
    results = db.session.query(Song).filter(Song.title.ilike(f'%{query}%')).all()

    # Convert the results to a list of dictionaries or any format suitable for our needs
    formatted_results = [{'title': song.title, 'artist': song.artist} for song in results]

    return formatted_results

# Registration route
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the username or email already exists
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return 'Username or email already exists!'

        hashed_password = generate_password_hash(password)

        # Insert user into the SQLite database
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # Use the session management function to set the user session
        set_user_session(new_user)

        return 'Registration successful!'

    return redirect(url_for('index'))


# Login route
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the email exists in the database
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            # Store user information in the session
            set_user_session(user)

            return redirect(url_for('dashboard'))
        else:
            return 'Invalid email or password!'

    return redirect(url_for('index'))

# Upload route
@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if file:
            # Save the file to the 'uploads' folder
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)

            # Save song information to the database
            new_song = Song(
                title=request.form['title'],
                artist=request.form['artist'],
                file_path=filename,
                user_id=session['user']['id']
            )

            db.session.add(new_song)
            db.session.commit()

            flash('Song uploaded successfully', 'success')
            return redirect(url_for('dashboard'))

# Read (Display) route
# Dashboard route
@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in
    if 'user' in session:
        # Fetch the user's songs from the database
        user_songs = Song.query.filter_by(user_id=session['user']['id']).all()
        user_info = session['user']
        return render_template('dashboard.html', user=user_info, user_songs=user_songs)
    else:
        flash('You need to login first.', 'error')
        return redirect(url_for('index'))


# Logout route
@app.route('/logout')
def logout():
    # Clear the session to log out the user
    clear_user_session()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Example index route
@app.route('/')
def index():
    print(session.get('user'))
    return render_template('index.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
