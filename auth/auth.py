# All imports done
from flask import Blueprint, render_template,request,session,Markup,flash ,redirect, url_for
from CreateUserDatabase import * 
from encryption import *
import re
import bcrypt
from cache import cache


auth_bp = Blueprint('auth_bp', __name__,
    template_folder='templates',
    static_folder='static')

# Register students
@auth_bp.route('/student/registration', methods=["POST", "GET"])
def studentRegistration():
    '''Register student code'''
    if request.method == "POST":
        # Generate a unique code here
        studentCode = request.form.get('studentCode')

        # hash student code
        myCode = studentCode.encode('utf-8')  # Convert code to binary
        # bcrypt.gensalt(rounds=16)   # used for hashing
        salt = b'$2b$16$MTSQ7iU1kQ/bz6tdBgjrqu'
       
        hashed = bcrypt.hashpw(myCode, salt)  # hashing the code

        # Connect to the database
        query = databaseConnection.query(StudentCodes).filter(
            StudentCodes.code == hashed.decode())

        # Searching for the code
        result = query.first()

        # Code exists
        if result:
            flash('The code is already in use ', 'error')
            return redirect(url_for('student_bp.student'))
            # Returning user

        else:
            flash(f"Your student code is {studentCode}.", 'info')
            # Add new user to the database
            newStudent = StudentCodes(hashed.decode())
            databaseConnection.add(newStudent)
            databaseConnection.commit()

            return render_template('student_sign_up.html')

    elif request.method == "GET":
        return render_template('student_sign_in.html')

# Register an admin  
@auth_bp.route('/newAdmin', methods=['POST', 'GET'])
def newadmin():
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
                    # Passwords should match
                    if str(password) == str(repassword):
                        user = Admin(username, password)
                        databaseConnection.add(user)
                        databaseConnection.commit()
                        flash('You have registered. Please login to continue.', 'success')
                        return render_template('admin_sign_in.html', title="login")

                    else:
                        flash('Passwords doesn\'t match.', 'error')
                        return render_template('admin_sign_up.html')
    return render_template('admin_sign_up.html')

# Admin login
@auth_bp.route('/loginAdmin', methods=['POST','GET'])
def adminlogin():
        # Sumbitting login form
    if request.method == 'POST':
        send_username = request.form.get('username')
        send_password = request.form.get('password')

        # If the password and username is provided
        if send_password and len(send_username) <= 10:
            # Compare admin credentials with the records in the databse
            query = databaseConnection.query(Admin).filter(Admin.username.in_(
                [send_username]), Admin.password.in_([send_password]))
            # Store result of the query
            result = query.first()

            # Match found in the database
            if result:
                # Here we can login
                session['logged_in'] = True
                session['username'] = send_username
                flash('You have successfully logged in.', 'success')

                # Show dashboard
                return redirect(url_for('admin_bp.adminindex'))
            else:
                flash('Check your username and password', 'error')
                return redirect(url_for('auth_bp.adminlogin'))
    else:
        return render_template('admin_sign_in.html')

@auth_bp.route('/newstudent', methods=['POST', 'GET'])
def newstudent():
    if request.method == "POST":
        # Get class code
        classCode = request.form.get('classCode')

        # Generate a unique code here
        studentCode = request.form.get('studentCode')
        # hash student code
        myCode = studentCode.encode('utf-8')  # Convert code to binary
        # bcrypt.gensalt(rounds=16)   # used for hashing
        salt = b'$2b$16$MTSQ7iU1kQ/bz6tdBgjrqu'
       
        hashed = bcrypt.hashpw(myCode, salt)  # hashing the code
        # Connect to the database

        query = databaseConnection.query(StudentCodes).filter(StudentCodes.code == hashed.decode())
        queryClass = databaseConnection.query(Account).filter(Account.classCode == classCode)
        # Searching for the code
        
        # Returning user
        if query.first() and queryClass.first():
            resultClass = queryClass.first()
            result = query.first()
            size = resultClass.size
            alreadyIn = get_distinct_voters(classCode, studentCode)
            if alreadyIn >= int(size):
                queryStudent = databaseConnection.query(Feedback).filter(Feedback.classCode == classCode)
                for results in queryStudent.all():
                    if results.studentCode != studentCode:
                        flash('The class is full. Please let your professor know and have him/her update the class size accordingly.', 'error')
                        return redirect(url_for('auth_bp.newstudent'))
                    else:
                        # Go to feedback page
                        return redirect(url_for('student_bp.student'))
            else:
                flash('Welcome! Remember your code for the future use','success')
                flash(myCode.decode(),'info')
                session['classCode'] = classCode
                session['studentCode'] = studentCode
                session['logged_in'] = True
                # Go to feedback page
                return redirect(url_for('student_bp.student'))

        # No records found
        elif query.first() == None:
            flash(Markup('The student code does not exist. Do you want to <a href="/student/registration">register</a>?'), 'error')
            return redirect(url_for('auth_bp.newstudent'))
        elif queryClass.first() == None:
            flash(Markup('The class code does not exist. Please check in with your professor.'), 'error')
            return redirect(url_for('auth_bp.newstudent'))

    elif request.method == "GET":
        return render_template('student_sign_up.html')

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
        if send_password and len(send_username) <= 10:
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
    session.clear()
    # Feedback message
    flash('You have successfully logged out', 'success')
    return render_template('index.html')