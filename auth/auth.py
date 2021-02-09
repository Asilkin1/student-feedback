# All imports done
from flask import Blueprint, render_template,request,session, flash ,redirect, url_for
from CreateUserDatabase import * 
from encryption import *
import re

auth_bp = Blueprint('auth_bp', __name__,
    template_folder='templates',
    static_folder='static')

# Register professor
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        # Get username from the form
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')

        if password == "":
            flash('Password cannot be empty.', 'error')
        else: 
            for error, boolean in password_check(password).items():

                if error == 'length_error' and boolean:
                    flash('Password length must contain at least 8 characters.', 'error')
                    return render_template('register.html')
                
                if error == 'digit_error' and boolean:
                    flash('Password must contain at least one digit.', 'error')
                    return render_template('register.html')
                
                if error == 'uppercase_error' and boolean:
                    flash('Password must contain at least one upper case letter', 'error')
                    return render_template('register.html')
                
                if error == 'symbol_error' and boolean:
                    flash('Password must contain at least one symbol.', 'error')
                    return render_template('register.html')

                if error == 'password_ok' and boolean:
                    print(str(password) == str(repassword))
                    # Passwords should match
                    if str(password) == str(repassword):
                        user = User(username, password)
                        databaseConnection.add(user)
                        databaseConnection.commit()
                        flash('You have registered. Please login to continue.', 'success')
                        return render_template('login.html', title="login")

                    else:
                        flash('Passwords doesn\'t match.', 'error')
                        return render_template('register.html')
    return render_template('register.html')

def password_check(password):
    """
    Verify the strength of 'password'
    Returns a dictionary indicating the wrong criteria
    A password is considered strong if:
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
    """

    # calculating the length
    length_error = len(password) < 8

    # searching for digits
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for symbols
    symbol_error = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None

    # overall result
    password_ok = not ( length_error or digit_error or uppercase_error or symbol_error )

    return {
        'password_ok' : password_ok,
        'length_error' : length_error,
        'digit_error' : digit_error,
        'uppercase_error' : uppercase_error,
        'symbol_error' : symbol_error,
    }

# Login professor
@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
    # Sumbitting login form
    if request.method == 'POST':
        send_username = request.form.get('username')
        send_password = request.form.get('password')

        # If the password and username is provided
        if send_password and send_username:
            # Compare professor credentials with the records in the databse
            query = databaseConnection.query(User).filter(User.username.in_(
                [send_username]), User.password.in_([send_password]))
            # Store result of the query
            result = query.first()

            # Match found in the database
            if result:
                # Here we can login
                session['logged_in'] = True
                session['username'] = send_username
                flash('You have successfully logged in.', 'success')

                # Show dashboard
                return redirect(url_for('professor_bp.instructor'))
            else:
                flash('Check your username and password', 'error')
                return redirect(url_for('auth_bp.login'))
    else:
        return render_template('login.html')

@auth_bp.route('/signup', methods=["POST", "GET"])
def signup():
    return render_template('signup.html', title='signup')

@auth_bp.route('/logout')
def logout():
    # User is logged out
    session['logged_in'] = False
    # User is removed from the session
    session.pop('username', None)
    # Remove student codes and class code
    session.pop('classCode', None)
    session.pop('studentCode', None)

    # Feedback message
    flash('You have successfully logged out', 'success')
    return render_template('index.html')