# All router to professor pages
from flask import Blueprint, render_template,request, flash, session, redirect, url_for
from CreateUserDatabase import * 
import random

professor_bp = Blueprint('professor_bp', __name__,
    template_folder='templates',
    static_folder='static')

@professor_bp.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        flash('You have registered', 'info')
        # Get username from the form
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')

        if username and password and repassword:
            # Passwords should match
            if str(password) == str(repassword):
                user = User(username, password)
                databaseConnection.add(user)
                databaseConnection.commit()
                flash('You are registered. Please login to continue.')
                return render_template('login.html', title="login")

        else:
            flash('Password doesn\'t match.')
    else:
        flash('Cannot be empty.')
    return render_template('register.html')


@professor_bp.route('/professor', methods=["POST", "GET"])
def instructor():
    if not session.get('logged_in'):
        flash('Please log in to gain access to the website.', 'info')
        return render_template('login.html', title='submit')
    else:
        return render_template('professor.html')

@professor_bp.route("/professor/delete/<string:id>", methods=['GET', 'POST'])
def deleteClass(id):
    databaseConnection.query(Account).filter(Account.entryId == id).delete()
    databaseConnection.commit()

    flash('Class Deleted', 'success')
    return redirect(url_for('auth_bp.login'))

@professor_bp.route("/professor/edit/<string:id>", methods=['GET', 'POST'])
def editClass(id):
    
    query = databaseConnection.query(Account).filter(
                Account.entryId == id)

    result = query.first()

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