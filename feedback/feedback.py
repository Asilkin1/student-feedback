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
        print(salt)
        hashed = bcrypt.hashpw(myCode, salt)  # hashing the code

        print('Hashed code', myCode.decode())
        # Connect to the database

        query = databaseConnection.query(StudentCodes).filter(StudentCodes.code == hashed.decode())
        queryClass = databaseConnection.query(Account).filter(Account.classCode == classCode)
        # Searching for the code
        print(hashed.decode())
        result = query.first()
        resultClass = queryClass.first()
        
        # Returning user
        if result and resultClass:
            flash('Welcome! Remember your code for the future use','success')
            flash(myCode.decode(),'info')
            session['classCode'] = classCode
            session['studentCode'] = studentCode
            session['logged_in'] = True

            # Get some data about class votes
            # Don't forget to get each row for current student code only once
            yourCodeVotes = databaseConnection.query(Feedback.studentCode).filter(Feedback.classCode == session.get('classCode'),Feedback.studentCode == session.get('studentCode')).distinct()
            yourVotedTimes = databaseConnection.query(Feedback.studentCode).filter(Feedback.classCode == session.get('classCode'),Feedback.studentCode == session.get('studentCode'))            
            
            distinctVoters = databaseConnection.query(Feedback.studentCode).filter(Feedback.classCode == session.get('classCode'),Feedback.studentCode != session.get('studentCode')).distinct()
            notYoursFeedbacks = databaseConnection.query(Feedback.studentCode).filter(Feedback.classCode == session.get('classCode'),Feedback.studentCode != session.get('studentCode'))
            classSize = databaseConnection.query(Account.size).filter(Account.classCode == session.get('classCode'))

            # Use the query as an iterable for more efficiency
            # Get all records without calling all() allow to interact with each object individually
            # for voted in getSomeReward:
            #     print('Resulttttttttt: ',voted)
            print('This many times you voted: ',yourCodeVotes.count())
            print('This many people voted: ',distinctVoters.count())
            print('Size of the class: ',classSize.one())

            return render_template('student.html', you=yourCodeVotes.count(), notYou = distinctVoters.count(), size=classSize.one()[0], voted = yourVotedTimes.count(), total=notYoursFeedbacks.count())

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
        print(salt)
        hashed = bcrypt.hashpw(myCode, salt)  # hashing the code

        print('Hashed code', myCode.decode())
        # Connect to the database
        query = databaseConnection.query(StudentCodes).filter(
            StudentCodes.code == hashed.decode())

        # Need redirect to login after signup

        # Searching for the code
        print(hashed.decode())
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
        # Date
        dateNow = date.today()

        # Time
        currentTime = datetime.now()
        timeNow = currentTime.strftime("%H:%M")
        
        currentDay = dateNow.weekday()

        day = ""

        # Monday
        if currentDay == 0:
            day = "M"
        # Tuesday
        if currentDay == 1:
            day = "T"
        # Wednesday
        if currentDay == 2:
            day = "W"
        # Thursday
        if currentDay == 3:
            day = "H"
        # Friday
        if currentDay == 4:
            day = "F"

        # Emoji number and encrypt it
        emoji = request.form.get('emoji')
        emoji = mysql_aes_encrypt(emoji, random_key)

        # Elaborate number and encrypt it
        elaborateNumber = request.form.get('elaborateNumber')
        elaborateNumber = mysql_aes_encrypt(elaborateNumber, random_key)

        # Elaborate text and encrypt it
        elaborateText = request.form.get('elaborateText')
        elaborateText = mysql_aes_encrypt(elaborateText, random_key)

        query = databaseConnection.query(Account).filter(Account.classCode == session['classCode'])
        result = query.first()
        classStart = result.start
        classEnd = result.end
        classDays = result.days

        if (timeNow > classStart) and (timeNow < classEnd) and (day in classDays):
            inClass = "Inside"
        else:
            inClass = "Outside"
        

        #create data in database
        newFeedback = Feedback(dateNow, timeNow, session['classCode'], session['studentCode'], emoji, elaborateNumber, elaborateText, inClass)
        databaseConnection.add(newFeedback)
        databaseConnection.commit()

        # Get some data about class votes
        # Don't forget to get each row for current student code only once
        yourCodeVotes = databaseConnection.query(Feedback.studentCode).filter(Feedback.classCode == session.get('classCode'),Feedback.studentCode == session.get('studentCode')).distinct()
        yourVotedTimes = databaseConnection.query(Feedback.studentCode).filter(Feedback.classCode == session.get('classCode'),Feedback.studentCode == session.get('studentCode'))            
        
        distinctVoters = databaseConnection.query(Feedback.studentCode).filter(Feedback.classCode == session.get('classCode'),Feedback.studentCode != session.get('studentCode')).distinct()
        classSize = databaseConnection.query(Account.size).filter(Account.classCode == session.get('classCode'))

        # Use the query as an iterable for more efficiency
        # Get all records without calling all() allow to interact with each object individually
        # for voted in getSomeReward:
        #     print('Resulttttttttt: ',voted)
        print('This many times you voted: ',yourCodeVotes.count())
        print('This many people voted: ',distinctVoters.count())
        print('Size of the class: ',classSize.one())

        # Message
        flash('Thank you for your feedback', 'info')
        return render_template('student.html', title="student", you=yourCodeVotes.count(), notYou = distinctVoters.count(), size=classSize.one()[0], voted = yourVotedTimes.count())
    return render_template('student.html', title='student')