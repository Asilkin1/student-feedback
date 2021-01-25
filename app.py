# Flask barebones
from flask import Flask, render_template, request, redirect, url_for,session, abort,flash
from models import create_post, get_posts, delete_posts
from datetime import date, datetime
from sqlalchemy.orm import sessionmaker
from CreateUserDatabase import *
import time
import os

# Helper functions from registration logic
from registration_logic import register

# Login engine
engine = create_engine('sqlite:///tutorial.db', echo=True)

app = Flask(__name__)


@app.route('/', methods=["POST", "GET"])
def index():
    # Go to student page, no need to be registered
    if request.path == '/student':
          return render_template('student_sign_up.html', title='student_page')
    
    return render_template('index.html', title='submit')
   

# -------------------------------------------------------------------- Log in
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        send_username = str(request.form['username'])
        send_password = str(request.form['password'])

        # If the password and username is provided
        if send_password and send_username:
            Session = sessionmaker(bind=engine)
            s = Session()

            query = s.query(User).filter(User.username.in_([send_username]), User.password.in_([send_password]))
            result = query.first()

            if result:
                session['logged_in'] = True
                session['studentCode'] = "2479YH"
                session['username'] = send_username
                flash('Your are successfully logged in','success')

                return render_template('index.html')
            
            else:
                flash('Wrong password or username','error')

        else:
            flash('Check your username and password','error')
            session['logged_in'] = False 

    return render_template('login.html')

# --------------------------------------------------------------------- Log out
@app.route('/logout')
def logout():
    # User is logged out
    session['logged_in'] = False
    # User is removed from the session
    session.pop('username', None)
    session.pop('studentCode', None)
    # Feedback message
    flash('You are successfully logged out','success')
    return render_template('login.html')

# --------------------------------------------------------------------- Registration
@app.route('/register', methods=['GET','POST'])
def register():
    flash('Please register to gain access to the website','info')
    if request.method == 'POST':
        
        # Get username from the form
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')

        if username and password and repassword:
            # Passwords should match
            if str(password) == str(repassword):
                Session = sessionmaker(bind=engine)
                s = Session()
                user = User(username,password)
                s.add(user)
                s.commit()
                flash('You are registered successfully','success')
            else:
                flash("Password doesn't match",'error')
        else:
            flash('Fields cannot be empty','error')

    return render_template('register.html')

@app.route('/analytics', methods=["POST","GET"])
def analytics():
    return render_template('analytics.html',title='stats')

@app.route('/notenoughdata',methods=["POST","GET"])
def notenoughdata():
    flash('Not enough data to generate a graph','info')
    return render_template('notEnoughData.html',title='not enough data')

@app.route('/classerror',methods=["POST","GET"])
def classerror():
    flash('Selected class cannot be found','error')
    return render_template('classError.html',title='class does not exist')

@app.route('/signup', methods=["POST","GET"])
def signup():
    return render_template('signup.html',title='signup')

# New student signup
@app.route('/newstudent', methods=['GET'])
def newstudent():
    return render_template('student_sign_up.html', scode=12003,ccode='Ab123')

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():

    # Stub for testing
    myClasses = ['CR123','CG234','TG445']
    newClass = request.form.get('addClassCode')
    # Add code to the database
    if request.method == 'POST':
        flash('Class added: ' + newClass,'info')
        myClasses.append(newClass)

    return render_template('dashboard.html', classes=myClasses)

@app.route('/student', methods=["POST", "GET"])
def student():
    if request.method == 'GET':
        #Delete existing data in database (can change this later)
        delete_posts()
        scode = request.args.get('studentCode')
        ccode = request.args.get('classCode')
        return render_template('student.html', studentcode=scode, classcode=ccode)
        
    if request.method == 'POST':
        #Date
        dateNow = date.today()

        #Time
        timeNow = time.asctime().split(' ')[3]
        currentTime = datetime.now()
        timeNow = currentTime.strftime("%I:%M %p")

        #Emoji number
        emoji = request.form.get('emoji')

        #class code
        classCode = request.form.get('classCode')

        #Student code
        studentCode = request.form.get('studentCode')

        #Elaborate number
        elaborateNumber = request.form.get('elaborateNumber')

        #Elaborate text
        elaborateText = request.form.get('elaborateText')

        #create data in database
        create_post(dateNow, timeNow, classCode, studentCode, emoji, elaborateNumber, elaborateText)
        
        # Message
        flash('Thank you for your feedback','info')
    return render_template('student.html', title='student')

@app.route('/professor', methods=["POST", "GET"])
def instructor():
    if not session.get('logged_in'):
            flash('Please log in to gain access to the website','info')
            return render_template('login.html', title='submit')
    else: 
        category = request.args.get('category')
        return render_template('professor.html', title='instructor')

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)