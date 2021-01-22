# Flask barebones
from flask import Flask, render_template, request, redirect, url_for,session, abort,flash
from models import create_post, get_posts, delete_posts
from datetime import date, datetime
from sqlalchemy.orm import sessionmaker
from CreateUserDatabase import *
import time
import os

# Login engine
engine = create_engine('sqlite:///tutorial.db', echo=True)

app = Flask(__name__)


@app.route('/', methods=["POST", "GET"])
def index():
    if not session.get('logged_in'):
        return render_template('login.html', title='submit')
    else:
        return render_template('index.html', title='submit')

# -------------------------------------------------------------------- Log in
@app.route('/login', methods=['GET','POST'])
def login():
    send_username = str(request.form['username'])
    send_password = str(request.form['password'])

    Session = sessionmaker(bind=engine)
    s = Session()

    query = s.query(User).filter(User.username.in_([send_username]), User.password.in_([send_password]))
    result = query.first()

    if result:
        session['logged_in'] = True
        session['studentCode'] = "2479YH"
        session['username'] = send_username
        flash('Your are successfully logged in')
    else:
       session['logged_in'] = False  

    return render_template('index.html')
# --------------------------------------------------------------------- Log out
@app.route('/logout')
def logout():
    # User is logged out
    session['logged_in'] = False
    # User is removed from the session
    session.pop('username', None)
    session.pop('studentCode', None)
    return render_template('login.html')

# --------------------------------------------------------------------- Registration
@app.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data, form.email.data,
                    form.password.data)
        db_session.add(user)
        flash('Thanks for registering')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/signup',methods=['GET'])
def unauthorized():
      if request.path == '/student':
          return render_template('student_sign_up.html', title='instructor')
      else:
          return render_template('professor_sign_up.html')

@app.route('/analytics', methods=["POST","GET"])
def analytics():
    return render_template('analytics.html',title='stats')

@app.route('/notenoughdata',methods=["POST","GET"])
def notenoughdata():
    return render_template('notEnoughData.html',title='not enough data')

@app.route('/classerror',methods=["POST","GET"])
def classerror():
    return render_template('classError.html',title='class does not exist')

@app.route('/signup', methods=["POST","GET"])
def signup():
    return render_template('signup.html',title='signup')

@app.route("/regisration",methods=["POST"])
def registration():
    email = request.form.get('email')
    password = request.form.get('password')
    repassword = request.form.get('repassword')

    if password == repassword:
        return redirect(url_for('index'))

# New student signup
@app.route('/newstudent', methods=['GET'])
def newstudent():
    return render_template('student_sign_up.html', scode=12003,ccode='Ab123')


@app.route('/student', methods=["POST", "GET"])
def student():
    if request.method == 'GET':
        #Delete existing data in database (can change this later)
        #delete_posts()
        scode = request.args.get('studentCode')
        ccode = request.args.get('classCode')
        return render_template('student.html', studentcode=scode, classcode=ccode)
        
    if request.method == 'POST':
        #Date
        dateNow = date.today()

        #Time
        #timeNow = time.asctime().split(' ')[3]
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

    return render_template('student.html', title='student')

@app.route('/professor', methods=["POST", "GET"])
def instructor():
    category = request.args.get('category')
    return render_template('professor.html', title='instructor')

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)