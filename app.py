from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

import hashlib

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'prueba'

# Intialize MySQL
mysql = MySQL(app)


@app.route('/')
def main():
    if 'loggedin' in session:
        return render_template('home.html')
    else:
        return render_template('index.html')


# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']

        password = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()


        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM login WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        login = cursor.fetchone()
        # If account exists in accounts table in out database
        if login:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = login['id']
            session['username'] = login['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)


# http://localhost:5000/python/logout - this will be the logout page
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))


# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM login WHERE username = %s', (username,))
        login = cursor.fetchone()
        # If account exists show error and validation checks
        if login:
            msg = 'Account already exists!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO login VALUES (NULL , %s, %s)', (username, password,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM login')
        login = cursor.fetchall()
        # Show the profile page with account info
        return render_template('profile.html', account=login)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/edit/<id>')
def get_contact(id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM login WHERE id = {0}' .format(id))
    data = cursor.fetchall()
    return render_template('edit.html', account=data[0])

@app.route('/update/<id>', methods=['POST'])
def update_contact(id):
    if request.method == 'POST':
     usuario = request.form['username']
     password = hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest()
     cursor = mysql.connection.cursor()
     cursor.execute("""
      UPDATE login 
      SET username = %s,
          password = %s
      WHERE id = %s
     """, (usuario, password, id))
     mysql.connection.commit()
     return redirect(url_for('profile'))

@app.route('/delete/<string:id>')
def delete(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM login WHERE id = {0}'.format(id))
    mysql.connection.commit()
    return redirect(url_for('profile'))


if __name__ == '__main__':
    app.run(port=3000, debug=True)


