# All router to professor pages
from flask import Blueprint, render_template,request, flash, session, redirect, url_for
from CreateUserDatabase import * 
import random
import re

professor_bp = Blueprint('professor_bp', __name__,
    template_folder='templates',
    static_folder='static')

@professor_bp.route('/register', methods=['GET', 'POST'])
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


@professor_bp.route('/professor', methods=["POST", "GET"])
def instructor():
    if not session.get('logged_in'):
        flash('Please log in to gain access to the website.', 'info')
        return render_template('login.html', title='submit')
    else:
        return render_template('professor.html')

@professor_bp.route("/professor/delete/<string:id>/<string:ccode>", methods=['GET', 'POST'])
def deleteClass(id, ccode):
    databaseConnection.query(Account).filter(Account.entryId == id).delete()
    databaseConnection.commit()
    databaseConnection.query(Feedback).filter(Feedback.classCode == ccode).delete()
    databaseConnection.commit()

    flash('Class Deleted', 'success')
    return redirect(url_for('auth_bp.login'))

@professor_bp.route("/professor/edit/<string:id>", methods=['GET', 'POST'])
def editClass(id):
    
    query = databaseConnection.query(Account).filter(
                Account.entryId == id)
    result = query.first()

    # Query feedback table for class code
    queryFeedBack = databaseConnection.query(Feedback).filter(Feedback.classCode == result.classCode)
    resultFeedback = queryFeedBack.first()

    # Parse for section in Feedback table
    parsingClassCode = resultFeedback.classCode.split("-")
    sectionFeedBack = parsingClassCode[1]

    # Populate article form fields
    schoolName = result.schoolName
    departmentName = result.departmentName
    className = result.className
    print('class name :', className)
    start = result.start 
    end = result.end
    days = result.days
    parsingClassCode = result.classCode.split("-")
    mode = result.mode
    size = result.size

    # Parse for section
    sectionName = parsingClassCode[1]

    if request.method == 'POST':
        schoolName = request.form['schoolName']
        departmentName = request.form['departmentName']
        className = request.form['className']
        sectionName = request.form['sectionName']
        
        days = request.form.getlist('days')
        saveDays = ''

        start = request.form['start']
        end = request.form['end']
        mode = request.form['mode']
        size = request.form['size']
        
        result.schoolName = schoolName
        result.departmentName = departmentName
        result.className = className
        result.start = start
        result.days = saveDays.join(days)
        result.end = end
        result.mode = mode
        result.size = size

        # Parse for class code
        parsingClassCode = result.classCode.split("-")
        classCode = parsingClassCode[0]

        result.classCode = str(classCode) + '-' + sectionName
        databaseConnection.commit()

        # Update class code in feedback table if the section got changed
        if sectionName != sectionFeedBack:
            for results in queryFeedBack.all():
                results.classCode = result.classCode
        
        databaseConnection.commit()

        flash('Class Updated', 'success')

        return redirect(url_for('auth_bp.login'))

    return render_template('editClass.html', entryId=id, schoolName=schoolName, departmentName=departmentName, className=className,
                                                    sectionName=sectionName, days=days, start=start, end=end, size=size, classMode=mode)
@professor_bp.route('/professor/create', methods=["POST", "GET"])
def professor():
    inData = True

    if request.method == 'POST':

        # While loops until a random number is generated that is not already in the database
        while(inData):
            # Professors unique class code (Randomly generated between x, and y with z being the amount generated)
            classCode = random.randrange(1, 3000, 1)
            print(classCode)

            query = databaseConnection.query(Account).filter(
                Account.classCode == classCode)
            # Creates a cursor that checks if classCodes value exists at all
            result = query.first()
            if result == None:
                inData = False

        # Schools Name
        schoolName = request.form.get('schoolName')
        print(schoolName)
        
        # Departments Name
        departmentName = request.form.get('departmentName')
        
        # Class' Id
        className = request.form.get('className')
    
        # Sections Name
        sectionName = request.form.get('sectionName')

        # Mode
        mode = request.form.get('classMode')
        # Start Time
        start = request.form.get('start')

        # End Time
        end = request.form.get('end')

        # Class size
        classSize = str(request.form.get('size'))
        
        #days
        days = request.form.getlist('day')
        saveDays = ''
        print('Days picked: ', days)

        # Combined section and class code
        classAndSection = str(classCode) + '-' + sectionName
        
        # adds data to database
        newClass = Account(schoolName, departmentName,
                           className, classAndSection, start, end, saveDays.join(days), classSize, mode, session['username'])
        databaseConnection.add(newClass)

        try:
            databaseConnection.commit()
        except:
            databaseConnection.rollback()
            
        return redirect(url_for('auth_bp.login'))

    return render_template('addClass.html', title='professor')