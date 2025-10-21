from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from datetime import datetime

# -----------------------------
# Flask app setup
# -----------------------------
app = Flask(__name__)
app.secret_key = 'abella_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes

# -----------------------------
# SQLite Database configuration
# -----------------------------
DATABASE = 'abella_travel.db'


# Function to get database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This allows dictionary-like access
    return conn


# Simple email validation (no regex)
def is_valid_email(email):
    return '@' in email and '.' in email


# Initialize database
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create contact_messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


# -----------------------------
# Home page
# -----------------------------
@app.route('/')
def index():
    if 'loggedin' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))


# -----------------------------
# Login
# -----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Please fill in both email and password!', 'error')
            return render_template('login.html')

        conn = get_db_connection()
        account = conn.execute(
            'SELECT * FROM users WHERE email = ? AND password = ?',
            (email, password)
        ).fetchone()
        conn.close()

        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Incorrect email or password.', 'error')

    return render_template('login.html')


# -----------------------------
# Signup / Register
# -----------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        # Basic validation
        if not all([username, email, password]):
            flash('Please fill out all fields!', 'error')
            return render_template('signup.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            return render_template('signup.html')

        # Simple email validation (no regex)
        if not is_valid_email(email):
            flash('Please enter a valid email address!', 'error')
            return render_template('signup.html')

        # Check if user already exists
        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if existing_user:
            flash('Account already exists with this email!', 'error')
            conn.close()
            return render_template('signup.html')

        # Insert new user
        try:
            conn.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                (username, email, password)
            )
            conn.commit()
            conn.close()
            flash('You have successfully registered! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Registration failed. Email already exists.', 'error')
            conn.close()

    return render_template('signup.html')


# -----------------------------
# Logout
# -----------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


# -----------------------------
# About Page
# -----------------------------
@app.route('/about')
def about():
    return render_template('about.html')


# -----------------------------
# Contact Page
# -----------------------------
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()

        if not all([name, email, message]):
            flash('Please fill out all fields!', 'error')
            return render_template('contact.html')

        if not is_valid_email(email):
            flash('Please enter a valid email address!', 'error')
            return render_template('contact.html')

        # Save contact message to database
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO contact_messages (name, email, message) VALUES (?, ?, ?)',
            (name, email, message)
        )
        conn.commit()
        conn.close()

        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')


# -----------------------------
# Destinations Page
# -----------------------------
@app.route('/destinations')
def destinations():
    if 'loggedin' in session:
        return render_template('destinations.html', username=session['username'])
    flash('Please log in to view this page.', 'error')
    return redirect(url_for('login'))


# -----------------------------
# Local Destinations Page
# -----------------------------
@app.route('/local')
def local():
    if 'loggedin' in session:
        return render_template('local.html', username=session['username'])
    flash('Please log in to view this page.', 'error')
    return redirect(url_for('login'))


# -----------------------------
# Guide Page
# -----------------------------
@app.route('/guide')
def guide():
    if 'loggedin' in session:
        return render_template('guide.html', username=session['username'])
    flash('Please log in to view this page.', 'error')
    return redirect(url_for('login'))


# -----------------------------
# Try Page
# -----------------------------
@app.route('/try')
def try_page():
    if 'loggedin' in session:
        return render_template('try.html', username=session['username'])
    flash('Please log in to view this page.', 'error')
    return redirect(url_for('login'))


# -----------------------------
# Error Handlers
# -----------------------------
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


# -----------------------------
# Initialize database on first run
# -----------------------------
if __name__ == '__main__':
    init_db()  # Create database and tables
    app.run(debug=True, host='0.0.0.0', port=5000)