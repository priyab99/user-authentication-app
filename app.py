# app.py (or main.py)
import os
from flask import Flask, request, redirect, url_for, flash, session, render_template_string
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask application
app = Flask(__name__)

# --- Configuration ---
# Set a secret key for session management and flash messages.
# In a production environment, this should be a strong, randomly generated string
# and stored securely (e.g., environment variable).
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_super_secret_key_here')

# Configure SQLAlchemy to connect to PostgreSQL.
# The DATABASE_URL environment variable will be set by Render.
# For local development, you might set it manually or use a default.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://user:password@localhost:5432/mydatabase' # Replace with your local PostgreSQL URI
).replace("postgres://", "postgresql://") # Fix for SQLAlchemy 1.4+ compatibility

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Disable tracking modifications for performance

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# --- Database Model ---
# Define the User model for the database.
# This table will store user information (username and hashed password).
class User(db.Model):
    __tablename__ = 'users' # Explicitly set table name

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False) # Store hashed password

    def __repr__(self):
        return f'<User {self.username}>'

# --- HTML Templates as Strings ---
# Base HTML structure
BASE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {
            font-family: 'Inter', sans-serif;
        }
        .rounded-box {
            border-radius: 0.75rem;
        }
        .btn {
            @apply inline-flex items-center justify-center px-4 py-2 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-200 ease-in-out;
        }
        .btn-secondary {
            @apply bg-gray-600 hover:bg-gray-700;
        }
        .flash-message {
            @apply p-3 mb-4 rounded-lg text-sm font-medium;
        }
        .flash-message.success {
            @apply bg-green-100 text-green-800;
        }
        .flash-message.error {
            @apply bg-red-100 text-red-800;
        }
        .flash-message.info {
            @apply bg-blue-100 text-blue-800;
        }
    </style>
</head>
<body class="bg-gray-100 min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 p-10 bg-white rounded-box shadow-lg">
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
            {{ heading }}
        </h2>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="space-y-3">
                    {% for category, message in messages %}
                        <div class="flash-message {{ category }}">
                            {{ message }}
                        </div>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}

        {{ content }}
    </div>
</body>
</html>
"""

# Register HTML template
REGISTER_HTML_CONTENT = """
<form class="mt-8 space-y-6" action="{{ url_for('register') }}" method="POST">
    <div class="rounded-md shadow-sm -space-y-px">
        <div>
            <label for="username" class="sr-only">Username</label>
            <input id="username" name="username" type="text" autocomplete="username" required
                   class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                   placeholder="Username">
        </div>
        <div>
            <label for="password" class="sr-only">Password</label>
            <input id="password" name="password" type="password" autocomplete="new-password" required
                   class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                   placeholder="Password">
        </div>
    </div>

    <div>
        <button type="submit" class="btn w-full">
            Register
        </button>
    </div>
</form>
<div class="mt-6 text-center text-sm text-gray-600">
    Already have an account?
    <a href="{{ url_for('login') }}" class="font-medium text-indigo-600 hover:text-indigo-500">
        Log in here
    </a>
</div>
"""

# Login HTML template
LOGIN_HTML_CONTENT = """
<form class="mt-8 space-y-6" action="{{ url_for('login') }}" method="POST">
    <div class="rounded-md shadow-sm -space-y-px">
        <div>
            <label for="username" class="sr-only">Username</label>
            <input id="username" name="username" type="text" autocomplete="username" required
                   class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                   placeholder="Username">
        </div>
        <div>
            <label for="password" class="sr-only">Password</label>
            <input id="password" name="password" type="password" autocomplete="current-password" required
                   class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                   placeholder="Password">
        </div>
    </div>

    <div>
        <button type="submit" class="btn w-full">
            Sign in
        </button>
    </div>
</form>
<div class="mt-6 text-center text-sm text-gray-600">
    Don't have an account?
    <a href="{{ url_for('register') }}" class="font-medium text-indigo-600 hover:text-indigo-500">
        Register here
    </a>
</div>
"""

# Dashboard HTML template
DASHBOARD_HTML_CONTENT = """
<div class="text-center">
    <p class="text-gray-700 mb-6">You have successfully logged in to your secure dashboard.</p>
    <a href="{{ url_for('logout') }}" class="btn btn-secondary">
        Logout
    </a>
</div>
"""

# --- Routes ---

@app.route('/')
def index():
    """
    Redirects to the login page if not logged in, otherwise to the dashboard.
    """
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles user registration.
    GET: Displays the registration form.
    POST: Processes the form submission, creates a new user, and saves to the database.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Basic validation
        if not username or not password:
            flash('Username and password are required.', 'error')
            # Re-render with flash message
            return render_template_string(BASE_HTML, title="Register", heading="Create Your Account", content=REGISTER_HTML_CONTENT)


        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
            # Re-render with flash message
            return render_template_string(BASE_HTML, title="Register", heading="Create Your Account", content=REGISTER_HTML_CONTENT)


        # Hash the password before storing it in the database for security.
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Create a new User object
        new_user = User(username=username, password=hashed_password)

        try:
            # Add the new user to the database session and commit.
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            # Rollback in case of an error (e.g., database connection issues)
            db.session.rollback()
            flash(f'An error occurred during registration: {e}', 'error')
            # Re-render with flash message
            return render_template_string(BASE_HTML, title="Register", heading="Create Your Account", content=REGISTER_HTML_CONTENT)


    # For GET requests, display the registration form.
    return render_template_string(BASE_HTML, title="Register", heading="Create Your Account", content=REGISTER_HTML_CONTENT)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login.
    GET: Displays the login form.
    POST: Processes the form submission, validates credentials, and logs the user in.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Basic validation
        if not username or not password:
            flash('Username and password are required.', 'error')
            # Re-render with flash message
            return render_template_string(BASE_HTML, title="Login", heading="Sign in to your account", content=LOGIN_HTML_CONTENT)

        # Find the user by username
        user = User.query.filter_by(username=username).first()

        # Check if user exists and password is correct
        if user and check_password_hash(user.password, password):
            # If credentials are valid, store username in session to mark user as logged in.
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
            # Re-render with flash message
            return render_template_string(BASE_HTML, title="Login", heading="Sign in to your account", content=LOGIN_HTML_CONTENT)

    # For GET requests, display the login form.
    return render_template_string(BASE_HTML, title="Login", heading="Sign in to your account", content=LOGIN_HTML_CONTENT)

@app.route('/dashboard')
def dashboard():
    """
    Displays the dashboard page. Requires user to be logged in.
    """
    # Check if user is logged in. If not, redirect to login page.
    if 'username' not in session:
        flash('Please log in to access the dashboard.', 'info')
        return redirect(url_for('login'))

    return render_template_string(BASE_HTML, title="Dashboard", heading=f"Welcome, {session['username']}!", content=DASHBOARD_HTML_CONTENT)

@app.route('/logout')
def logout():
    """
    Logs out the user by removing their username from the session.
    """
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# --- Database Initialization (IMPORTANT CHANGE HERE) ---
# This block ensures the database tables are created when the app runs.
# We're moving this into the __main__ block using an application context.
# This is the modern and correct way to handle one-time setup tasks in Flask.

# --- Run the Application ---
if __name__ == '__main__':
    # When running locally, set debug to True for development convenience.
    # For production, debug should be False.

    # Create application context to ensure database tables are created
    # This runs once when the app starts, for both local and Render deployments
    with app.app_context():
        print("Attempting to create database tables...")
        try:
            db.create_all()
            print("Database tables created successfully or already exist.")
        except Exception as e:
            print(f"Error creating database tables: {e}")
            # In a real app, you might want to log this error more robustly

    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))