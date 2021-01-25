# Flask barebones
from flask import Flask, render_template, request, redirect, url_for, make_response,url_for,session, abort,flash
from models import create_post, get_posts, delete_posts
from datetime import date, datetime
import time
import os
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3 as sql

# Sessions and registration
from CreateUserDatabase import *
# Login engine
engine = create_engine('sqlite:///tutorial.db', echo=True)

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io

app = Flask(__name__)

# ---------------------------------------------------------------------------- Professor need to login/register
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

# ---------------------------------------------------------------- Manage class codes
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


@app.route('/signup', methods=["POST", "GET"])
def signup():
    return render_template('signup.html', title='signup')


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

#Called by professor.html
@app.route('/analytics/check',methods=["POST","GET"])
def check():
    #Pull variables from professor form
    ccode = request.args.get('classCode') 
    Category = request.args.get('category')

    con = sql.connect('database.db') # connect to the database
    Frame = pd.read_sql_query("SELECT * from feedback", con)  # Database to Pandas
    # Filter Database by class code
    Frame = Frame[Frame['classCode'] == ccode]


    if(Frame.empty): #if the frame is empty, no class exists
        return render_template('ClassNotFound.html',title='CNF')

    elif(len(Frame.index) < 10): #If the whole datatable is smaller than 10 values
        return render_template('notEnoughData.html', title='NED')
    
    #Checks the size of the data depending on what category
    else:
        if(Category == 'Instructor'):
            Frame = Frame[Frame['elaborateNumber']== "Instructor/Professor"]
            if(len(Frame.index) < 10):
                return render_template('notEnoughData.html',title='NED')
            else:
                return render_template('analytics.html',title='data')
        
        elif(Category == 'Teaching-Style'):
            Frame = Frame[Frame['elaborateNumber'] == "Teaching Style"]
            if(len(Frame.index) < 10):
                return render_template('notEnoughData.html',title='NED')
            else:
                return render_template('analytics.html',title='data')
        
        elif(Category == 'Topic'):
            Frame = Frame[Frame['elaborateNumber'] == "Topic"]
            if(len(Frame.index) < 10):
                return render_template('notEnoughData.html',title='NED')
            else:
                return render_template('analytics.html',title='data')
        
        elif(Category == 'Other'):
            Frame = Frame[Frame['elaborateNumber'] == "Other"]
            if(len(Frame.index) < 10):
                return render_template('notEnoughData.html',title='NED')
            else:
                return render_template('analytics.html',title='data')


@app.route('/analytics/plot/<classCode>&<Category>', methods=["POST","GET"]) #vars to be passed in are <classcode> and <category>. & makes sure they are seperate!
#Called by analytics.html
def drawbar(classCode,Category):

    #Match the category var to database names
    if(Category=='Instructor'):
        Category='Instructor/Professor'
    elif(Category=='Teaching-Style'):
        Category='Teaching Style'

    con = sql.connect('database.db') # connect to the database
    Frame = pd.read_sql_query("SELECT * from feedback", con)  # Database to Pandas
    Frame = Frame[Frame['classCode'] == classCode] #filter by class
    Frame = Frame[Frame['elaborateNumber']== Category] #filter by category
    
    fig = Figure()
    axis = fig.add_subplot(1,1,1)
    Frame = Frame['emoji'] #get just the scores
    x = [1,2,3,4,5] #Array of scores
    y = [Frame[Frame==1].count(),Frame[Frame==2].count(),Frame[Frame==3].count(),Frame[Frame==4].count(),Frame[Frame==5].count()] #Count of each score
    axis.bar(x,y) #bar plot
    axis.set_title(Category)
    axis.set_xlabel('Score')
    axis.set_ylabel('Count')
    
    #Flask stuff to print plot
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route('/analytics/calc/<classCode>&<Category>', methods=["POST","GET"])
#Called by Analytics.html 
def calc(classCode,Category):
    if(Category=='Instructor'):
        Category='Instructor/Professor'
    elif(Category=='Teaching-Style'):
        Category='Teaching Style'

    con = sql.connect('database.db') # connect to the database
    Frame = pd.read_sql_query("SELECT * from feedback", con)  # Database to Pandas
    Frame = Frame[Frame['classCode'] == classCode] #filter by class
    Frame = Frame[Frame['elaborateNumber']== Category] #filter by category
    Frame = Frame['emoji'] #Get just the numbers
    return f'Your average score was {round(Frame.mean(),2)}' #return the mean

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True)
