from flask import Blueprint, render_template,request, flash, session,redirect, url_for
import bcrypt
from datetime import date, datetime, timedelta  # get date and time
from encryption import *
from CreateUserDatabase import *
from sqlalchemy.sql import text
from globalTime import utc2local

student_bp = Blueprint('student_bp', __name__,
    template_folder='templates',
    static_folder='static')

# Ask to login for any routes in student
@student_bp.before_request
def before_request():
    session.permanent = True
    student_bp.permanent_session_lifetime = timedelta(minutes=95)
    if not session.get('studentCode'):
        flash('Please log in to gain access to the website.', 'info')
        return render_template('student_sign_up.html')


def is_ascii(s):
    return all(ord(c)<128 for c in s)

@student_bp.route('/student/', methods=["POST", "GET"])
def student():
    if request.method == 'GET':
        classCode = str(session.get('classCode'))
        query = databaseConnection.query(Categories).filter(Categories.classCode == classCode)
        categories = query.all()

        # Show incentive data
        return render_template('student.html', categories=categories,
                                                you=you_voted(session.get('classCode'),session.get('studentCode')), 
                                                notYou = get_total_voters(session.get('classCode')), 
                                                size=get_class_size(session.get('classCode')), 
                                                voted = voted_times(session.get('classCode'), session.get('studentCode')), 
                                                total=not_your_votes(session.get('classCode'),session.get('studentCode')))

    if request.method == 'POST':
       
        dateNow = date.today()
        # save as UTC
        currentTime = datetime.utcnow()
        timeNow = utc2local(currentTime).strftime("%H:%M")
        print('Time: ', timeNow)
        
        # Emoji number and encrypt it
        emoji = request.form.get('emoji')
        emoji = mysql_aes_encrypt(emoji, random_key)

        # Elaborate number and encrypt it
        elaborateNumber = request.form.get('elaborateNumber')
        elaborateNumber = mysql_aes_encrypt(elaborateNumber, random_key)

        # Elaborate text and encrypt it
        elaborateText = request.form.get('elaborateText')
        
        # ------------Accept-only-english-characters---------------
        if is_ascii(elaborateText): 
            elaborateText = mysql_aes_encrypt(elaborateText + ' ', random_key)
            #create data in database
            newFeedback = Feedback(dateNow, timeNow, session['classCode'], session['studentCode'], emoji, elaborateNumber, elaborateText, check_date_voted(session.get('classCode')))
            databaseConnection.add(newFeedback)
            databaseConnection.commit()
            flash('Thank you for your feedback', 'success')
        else:
            flash('Should be in english ...','error')
        
        #----------------Avoid-any-utf-8-utf-16--------------------
        classCode = str(session.get('classCode'))
        query = databaseConnection.query(Categories).filter(Categories.classCode == classCode)
        categories = query.all()

        # Message
        return render_template('student.html', title="student", 
                                categories=categories,
                                you=you_voted(session.get('classCode'), session.get('studentCode')), 
                                notYou = get_total_voters(session.get('classCode')), 
                                size=get_class_size(session.get('classCode')), 
                                voted = voted_times(session.get('classCode'),session.get('studentCode')),
                                total=not_your_votes(session.get('classCode'),session.get('studentCode')))

    return render_template('student.html', title='student')