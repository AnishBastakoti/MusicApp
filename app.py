from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/music_app'
mongo = PyMongo(app)

# Use a secret key for session management
app.secret_key = 'your_secret_key'

# Registration route
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the username or email already exists
        if mongo.db.users.find_one({'$or': [{'username': username}, {'email': email}]}):
            return 'Username or email already exists!'

        hashed_password = generate_password_hash(password, method='sha256')

        # Insert user into the MongoDB database
        mongo.db.users.insert_one({
            'username': username,
            'email': email,
            'password': hashed_password
        })

        return 'Registration successful!'

    return redirect(url_for('index'))

# Login route
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the email exists in the database
        user = mongo.db.users.find_one({'email': email})

        if user and check_password_hash(user['password'], password):
            # Store user information in the session
            session['user'] = {
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email']
            }

            return 'Login successful!'
        else:
            return 'Invalid email or password!'

    return redirect(url_for('index'))

# Example index route
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
