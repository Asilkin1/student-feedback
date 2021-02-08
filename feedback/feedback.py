from flask import Blueprint, render_template,request, flash, session,Markup,redirect, url_for
import bcrypt
from datetime import date, datetime, timedelta  # get date and time
from encryption import *
from CreateUserDatabase import *

student_bp = Blueprint('student_bp', __name__,
    template_folder='templates',
    static_folder='static')

@student_bp.route('/newstudent', methods=['POST', 'GET'])
def newstudent():
    if request.method == "POST":
        # Get class code
        classCode = request.form.get('classCode')
        # Generate a unique code here
        studentCode = request.form.get('studentCode')
        # hash student code
        myCode = studentCode.encode('ascii')  # Convert code to binary
        # bcrypt.gensalt(rounds=16)   # used for hashing
        salt = b'$2b$16$MTSQ7iU1kQ/bz6tdBgjrqu'
       
        hashed = bcrypt.hashpw(myCode, salt)  # hashing the code
        # Connect to the database

        query = databaseConnection.query(StudentCodes).filter(StudentCodes.code == hashed.decode())
        queryClass = databaseConnection.query(Account).filter(Account.classCode == classCode)
        # Searching for the code
      
        result = query.first()
        resultClass = queryClass.first()
        
        # Returning user
        if result and resultClass:
            flash('Welcome! Remember your code for the future use','success')
            flash(myCode.decode(),'info')
            session['classCode'] = classCode
            session['studentCode'] = studentCode
            session['logged_in'] = True

            return render_template('student.html', you=you_voted(session.get('classCode'),session.get('studentCode')), 
                                    notYou = get_total_voters(session.get('classCode'), session.get('studentCode')), 
                                    size=get_class_size(session.get('classCode')), 
                                    voted = you_voted(session.get('classCode'), session.get('studentCode')), 
                                    total=not_your_votes(session.get('classCode'),session.get('studentCode')))

        # No records found
        elif result == None:
            flash(Markup('The student code does not exist. Do you want to <a href="/student/registration">register</a>?'), 'error')
            return redirect(url_for('student_bp.newstudent'))
        elif resultClass == None:
            flash(Markup('The class code does not exist. Please check in with your professor.'), 'error')
            return redirect(url_for('student_bp.newstudent'))

    elif request.method == "GET":
        return render_template('student_sign_up.html')
        
@student_bp.route('/student/registration', methods=["POST", "GET"])
def studentRegistration():

    if request.method == "POST":
        # Generate a unique code here
        studentCode = request.form.get('studentCode')

        # hash student code
        myCode = studentCode.encode('ascii')  # Convert code to binary
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
            return redirect(url_for('student_bp.newstudent'))
            # Returning user

        else:
            flash(f"Your student code {studentCode}", 'info')
            # Add new user to the database
            newStudent = StudentCodes(hashed.decode())
            databaseConnection.add(newStudent)
            databaseConnection.commit()

            return render_template('student_sign_up.html')

    elif request.method == "GET":
        return render_template('student_sign_in.html')

@student_bp.route('/student/', methods=["POST", "GET"])
def student():

    if request.method == 'GET':
        pass

    if request.method == 'POST':
       
        dateNow = date.today()
        currentTime = datetime.now()
        timeNow = currentTime.strftime("%H:%M")
        
        # Emoji number and encrypt it
        emoji = request.form.get('emoji')
        emoji = mysql_aes_encrypt(emoji, random_key)

        # Elaborate number and encrypt it
        elaborateNumber = request.form.get('elaborateNumber')
        elaborateNumber = mysql_aes_encrypt(elaborateNumber, random_key)

        # Elaborate text and encrypt it
        elaborateText = request.form.get('elaborateText')
        if elaborateText != "":
            elaborateText = mysql_aes_encrypt(elaborateText, random_key)

        #create data in database
        newFeedback = Feedback(dateNow, timeNow, session['classCode'], session['studentCode'], emoji, elaborateNumber, elaborateText, check_date_voted(session.get('classCode')))
        databaseConnection.add(newFeedback)
        databaseConnection.commit()

        # Message
        flash('Thank you for your feedback', 'info')
        return render_template('student.html', title="student", 
                                you=you_voted(session.get('classCode'), session.get('studentCode')), 
                                notYou = not_your_votes(session.get('classCode'), session.get('studentCode')), 
                                size=get_class_size(session.get('classCode')), 
                                voted = voted_times(session.get('classCode'),session.get('studentCode')),
                                total=not_your_votes(session.get('classCode'),session.get('studentCode')))

    return render_template('student.html', title='student')