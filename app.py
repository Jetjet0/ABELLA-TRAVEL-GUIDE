from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

# -----------------------------
# Flask app setup
# -----------------------------
app = Flask(__name__)
app.secret_key = 'abella_secret_key'

# -----------------------------
# MySQL Workbench configuration
# -----------------------------
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'          # your MySQL username
app.config['MYSQL_PASSWORD'] = '2006'      # your MySQL password
app.config['MYSQL_DB'] = 'abella_travel_db'

mysql = MySQL(app)

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
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password,))
        account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Incorrect email or password.', 'error')
    return render_template('login.html', msg=msg)

# -----------------------------
# Signup / Register
# -----------------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            flash('Account already exists with this email!', 'error')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!', 'error')
        elif not username or not password or not email:
            flash('Please fill out the form completely!', 'error')
        else:
            cursor.execute(
                'INSERT INTO users (username, email, password) VALUES (%s, %s, %s)',
                (username, email, password)
            )
            mysql.connection.commit()
            flash('You have successfully registered! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('signup.html', msg=msg)

# -----------------------------
# Logout
# -----------------------------
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
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
@app.route('/contact')
def contact():
    return render_template('contact.html')

# -----------------------------
# Destinations Page
# -----------------------------
@app.route('/destinations')
def destinations():
    if 'loggedin' in session:
        return render_template('destinations.html', username=session['username'])
    else:
        flash('Please log in to view this page.', 'error')
        return redirect(url_for('login'))

# -----------------------------
# Local Destinations Page
# -----------------------------
@app.route('/local')
def local():
    if 'loggedin' in session:
        return render_template('local.html', username=session['username'])
    else:
        flash('Please log in to view this page.', 'error')
        return redirect(url_for('login'))

# -----------------------------
# Guide Page
# -----------------------------
@app.route('/guide')
def guide():
    if 'loggedin' in session:
        return render_template('guide.html', username=session['username'])
    else:
        flash('Please log in to view this page.', 'error')
        return redirect(url_for('login'))

# -----------------------------
# Donate Page (Fixed Missing Route)
# -----------------------------
@app.route('/try_page')
def try_page():
    if 'loggedin' in session:
        return render_template('try.html', username=session['username'])
    else:
        flash('Please log in to view this page.', 'error')
        return redirect(url_for('login'))

# -----------------------------
# Run the app
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
