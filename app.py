# Flask barebones
from flask import Flask, render_template, request, redirect, url_for, session, app, abort,flash, make_response, Response, render_template_string, Markup
from flask_session.__init__ import Session as flaskGlobalSession

# pagination
from flask_paginate import Pagination, get_page_args


from models import create_post, get_posts, delete_posts,create_class 
from datetime import date, datetime, timedelta #get date and time
from sqlalchemy.orm import sessionmaker #Making Sessions and login
from sqlalchemy import insert,delete
from CreateUserDatabase import *    # Table for Users
import time #date and time
import os #filepath

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sqlite3 as sql

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io

#Encryption stuff
from Crypto.Cipher import AES
from base64 import b64encode
import Padding
import binascii
import hashlib

import random
import sqlite3 as sl

#random code
import bcrypt

# Database engine
engine = create_engine('sqlite:///united.db', echo=True,connect_args={"check_same_thread": False})  # Connect to Users database
# Establish connection to the database
Session = sessionmaker(bind=engine)
# Provides connection to the database for any operations
databaseConnection = Session()

app = Flask(__name__)

#Encryption Key
#random_key = os.urandom(16)
random_key = b"J3FTV1PL1jDFeMh01I9r+A=="
random_key = b64encode(random_key).decode('utf-8')


@app.route('/', methods=["POST", "GET"])
def index():
    return render_template('index.html')

# @app.before_request
# def make_session_permanent():
#     session.permanent = True
#     app.permanent_session_lifetime = timedelta(minutes=1)
   
# -------------------------------------------------------------------- Log in
@app.route('/login/', methods=['GET','POST'])
def login(page=1):
    # Sumbitting login form
    if request.method == 'POST':
        send_username = request.form.get('username')
        send_password = request.form.get('password')
        
        # If the password and username is provided
        if send_password and send_username:
            session['logged_in'] = True
            session['username'] = send_username
            # Compare professor credentials with the records in the databse
            query = databaseConnection.query(User).filter(User.username.in_([send_username]), User.password.in_([send_password]))
            # Store result of the query
            result = query.first()
         
            # Match found in the database
            if result:
                session['logged_in'] = True
                session['username'] = send_username
                flash('You have successfully logged in.','success')

                # Category for ... ?
                category = request.args.get('category')

                # Get classes data for current username
                dashboardData = databaseConnection.query(Account).filter(Account.username == session.get('username'))

                users = list(dashboardData)
                # Not sure about this
                search = False
                #q = request.args.get('page')
                q = request.args.get('q')
                if q:
                    search = True
                # Get current page
                page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')

                #page = request.args.get(get_page_args(),type=int,default=1)
                print(page)
                per_page = 3
                print("aaah", per_page)
                pagination_users = users[offset: offset + per_page]
                print(pagination_users)

                pagination = Pagination(page=page,per_page=3, total=dashboardData.count(), search=search, record_name='Classes',css_framework='bootstrap4')    
                return render_template('index.html', title='dashboard', data=pagination_users, page=page, pagination=pagination)
            
            else:
                flash('Wrong password or username','error')

                # Get classes data for current username
                dashboardData = databaseConnection.query(Account).filter(Account.username == session.get('username'))

                users=list(dashboardData)
                # Not sure about this
                search = False
                q = request.args.get('page')
                if q:
                    search = True
                # Get current page
                page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
                page = request.args.get(get_page_args(),type=int,default=1)
                per_page=3
                print(page)
                print("aaaa", per_page)
                pagination_users = users[offset: offset + per_page]
                print(pagination_users)
                
                pagination = Pagination(page=page,per_page=3, total=dashboardData.count(), search=search, record_name='Classes',css_framework='bootstrap4') 
                return render_template('login.html', title='dashboard', data=pagination_users, page=page, pagination=pagination)

        else:
            flash('Check your username and password','error')
    elif request.method == 'GET':
        # Get classes data for current username
        dashboardData = databaseConnection.query(Account).filter(Account.username == session.get('username'))

        #dashboardData = databaseConnection.query(Account).filter(Account.username == session.get('username')).paginate(per_page=3)
        users = list(dashboardData)

        print("hi", users)
        q = request.args.get('q')

        # Not sure about this
        search = False
        if q:
            search = True
        # Get current page
        page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
        #page = request.args.get(get_page_args(),type=int,default=1)
        page = request.args.get('page')
        if page == None:
            page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
        print(page)
        per_page=3
        # if per_page is 3, offset shows items 1-3 in the first page, 4-6 on the next page, etc
        offset = (int(page) - 1) * per_page + 1
        print("offset", offset)
        pagination_users = users[offset: offset + per_page]
        print("combined", offset + per_page)
        print("aaa", per_page)
        print(pagination_users)
        
        pagination = Pagination(page=page,per_page=3, total=dashboardData.count(), search=search, record_name='Classes',css_framework='bootstrap4')
        return render_template('login.html', title='dashboard', data=pagination_users, page=page, pagination=pagination)

        return render_template('login.html')
    else:
        return render_template('login.html')

# --------------------------------------------------------------------- Log out
@app.route('/logout')
def logout():
    # User is logged out
    session['logged_in'] = False
    # User is removed from the session
    session.pop('username', None)
    # Remove student codes and class code
    session.pop('classCode', None)
    session.pop('studentCode',None)

    # Feedback message
    flash('You have successfully logged out','success')
    return render_template('index.html')

# --------------------------------------------------------------------- Registration
@app.route('/register', methods=['GET','POST'])
def register():
    
    if request.method == 'POST':
        flash('Please register to gain access to the website','info')
        # Get username from the form
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')

        if username and password and repassword:
            # Passwords should match
            if str(password) == str(repassword):
                user = User(username,password)
                databaseConnection.add(user)
                databaseConnection.commit()
                flash('You are registered')

        else:
            flash('Password doesn\'t match')
    else:
        flash('Cannot be empty')
    return render_template('register.html')


def classerror():
    flash('Selected class cannot be found','error')
    return render_template('classError.html',title='class does not exist')

@app.route('/signup', methods=["POST","GET"])
def signup():
    return render_template('signup.html',title='signup')

# New student signup ! Need to have a separate route for student login, same as for professor
@app.route('/newstudent', methods=['POST', 'GET'])
def newstudent():
    if request.method == "POST":
        # Get class code 
        classCode = request.form.get('classCode')

        # Generate a unique code here
        studentCode = request.form.get('studentCode')
        
         ## hash student code
        myCode = studentCode.encode('ascii')   ## Convert code to binary
        salt = b'$2b$16$MTSQ7iU1kQ/bz6tdBgjrqu' #bcrypt.gensalt(rounds=16)   # used for hashing
        print(salt)
        hashed = bcrypt.hashpw(myCode,salt)    ## hashing the code
        
        print('Hashed code', myCode.decode())
        # Connect to the database
        query = databaseConnection.query(StudentCodes).filter(StudentCodes.code == hashed.decode())
        # Searching for the code
        print(hashed.decode())
        result = query.first()
        
        # Returning user
        if result:
            flash('Welcome! Remember your code for the future use','success')
            flash(myCode.decode(),'info')
            session['classCode'] = classCode
            session['studentCode'] = studentCode
            session['logged_in'] = True
            
            # Insert new user into the database
            newUser = StudentCodes(hashed.decode())
            databaseConnection.add(newUser)
            databaseConnection.commit()
            
            return render_template('student.html')
        
        # No records found
        elif result == None:
            flash(Markup('The code does not exist. Do you want to <a href="/student/registration">register</a>?'), 'error')
            return redirect(url_for('newstudent'))
                 
    elif request.method == "GET":
        return render_template('student_sign_up.html')

@app.route('/student/registration', methods=["POST", "GET"])
def studentRegistration():

    if request.method == "POST":
        # Generate a unique code here
        studentCode = request.form.get('studentCode')
        
            ## hash student code
        myCode = studentCode.encode('ascii')   ## Convert code to binary
        salt = b'$2b$16$MTSQ7iU1kQ/bz6tdBgjrqu' #bcrypt.gensalt(rounds=16)   # used for hashing
        print(salt)
        hashed = bcrypt.hashpw(myCode,salt)    ## hashing the code
        
        print('Hashed code', myCode.decode())
        # Connect to the database
        query = databaseConnection.query(StudentCodes).filter(StudentCodes.code == hashed.decode())

        # Need redirect to login after signup

        # Searching for the code
        print(hashed.decode())
        result = query.first()

        # Code exists
        if result:
            flash('The code is already in use ','error')
            return redirect(url_for('newstudent'))
            # Returning user
        
        else:
            flash(f"This is your code {hashed.decode()}",'info')
            # Add new user to the database
            newStudent = StudentCodes(hashed.decode())
            databaseConnection.add(newStudent)
            databaseConnection.commit()

            return render_template('student_sign_up.html')

    elif request.method == "GET":
        return render_template('student_sign_in.html')

@app.route('/student/', methods=["POST", "GET"])
def student():
    
    if request.method == 'GET':
        #Delete existing data in database (can change this later)
        #delete_posts()
        pass
        
    if request.method == 'POST':
        #Date
        dateNow = date.today()

        #Time
        currentTime = datetime.now()
        timeNow = currentTime.strftime("%I:%M %p")

        #Emoji number
        emoji = request.form.get('emoji')
        #emoji = mysql_aes_encrypt(emoji, random_key)

        #Elaborate number
        elaborateNumber = request.form.get('elaborateNumber')
        #elaborateNumber = mysql_aes_encrypt(elaborateNumber, random_key)

        #Elaborate text
        elaborateText = request.form.get('elaborateText')
        print(elaborateText)
        #elaborateText = mysql_aes_encrypt(elaborateText, random_key)

        #create data in database
        create_post(dateNow, timeNow, session['classCode'], session['studentCode'], emoji, elaborateNumber, elaborateText)

        #Decryption test
        #elaborateText = mysql_aes_decrypt(elaborateText, random_key)
        #create_post(dateNow, timeNow, classCode, studentCode, emoji, elaborateNumber, elaborateText)
        
        # Message
        flash('Thank you for your feedback','info')
    return render_template('student.html', title='student')

#Encryption
def mysql_aes_encrypt(val, key):
    val = Padding.appendPadding(val,blocksize=Padding.AES_blocksize,mode='Random')
    
    def mysql_aes_key(key):
        return hashlib.sha256(key.encode()).digest()

    def mysql_aes_val(val, key):
        encrypted = AES.new(key, AES.MODE_ECB)
        print(encrypted)
        return(encrypted.encrypt(val))

    k = mysql_aes_key(key)
    v = mysql_aes_val(val.encode(), k)
    v = binascii.hexlify(bytearray(v))
    

    return v

#Decryption
def mysql_aes_decrypt(val,key):
    val = binascii.unhexlify(bytearray(val))

    def mysql_aes_key(key):
        return hashlib.sha256(key.encode()).digest()

    def mysql_aes_val(val, key):
        decrypted = AES.new(key, AES.MODE_ECB)
        return(decrypted.decrypt(val))

    k = mysql_aes_key(key)
    v = mysql_aes_val(val, k)

    v = Padding.removePadding(v.decode(),mode='Random')

    return v


@app.route('/professor/create', methods=["POST", "GET"])
def professor():
    inData = True
    
    if request.method == 'POST':

        #While loops until a random number is generated that is not already in the database
        while(inData):
            #Professors unique class code (Randomly generated between x, and y with z being the amount generated)
            classCode = random.randrange(1,3000,1)
            print(classCode)

            query = databaseConnection.query(Account).filter(Account.classCode == classCode)
            #Creates a cursor that checks if classCodes value exists at all
            result = query.first()
            #Note that the , after classCode is nessassary otherwise you get an unsuported type error (turns the int into a tuple containing an int)
            # cur.execute("""SELECT classCode FROM account WHERE classCode=?""", (classCode,))
            if result == None:
                 inData = False

        #Professors Name
        professorName = request.form.get('professorName')
        print("professor name: ", professorName)

        #Schools Name
        schoolName = request.form.get('schoolName')
        print("school name: ", schoolName)

        #Departments Name
        departmentName = request.form.get('departmentName')
        print("department name: ", departmentName)
        #Class' Id
        classId = request.form.get('classId')
        print("classID name: ", classId)
        #Sections Name
        sectionName = request.form.get('sectionName')
        print("Section name: " ,sectionName)


        #adds data to database
        #engine.execute(Account.insert(), professorName, schoolName, departmentName, classId, sectionName, int(classCode))
        newClass = Account(professorName, schoolName,departmentName, classId, sectionName, int(classCode), session['username'])
        databaseConnection.add(newClass)
        try:
            databaseConnection.commit()
        except:
            databaseConnection.rollback()
        #create_class(professorName, schoolName, departmentName, classId, sectionName, int(classCode))
        return redirect(url_for('login'))

    return render_template('forms/addClass.html', title='professor')


@app.route('/professor', methods=["POST", "GET"])
def instructor():
   if not session.get('logged_in'):
       flash('Please log in to gain access to the website','info')
       return render_template('login.html', title='submit')
   else:
       return render_template('professor.html')

# --------------------------------------------------------------------------------------------- Analytics
def decryption(classCode, Category):
    con = sql.connect('united.db')
    c = con.cursor()
    c.execute('''SELECT * FROM feedback WHERE classCode=?''', (classCode))
    
    Frame = pd.read_sql_query("SELECT * from feedback", con)

    for row in range(0,len(Frame.index)):
        Frame.at[row,'emoji'] = mysql_aes_decrypt(Frame.at[row,'emoji'],random_key)
        Frame.at[row,'elaborateNumber'] = mysql_aes_decrypt(Frame.at[row,'elaborateNumber'],random_key)
        Frame.at[row,'elaborateText'] = mysql_aes_decrypt(Frame.at[row,'elaborateText'],random_key)
    
    return Frame

#Called by professor.html
@app.route('/analytics/check/',methods=["POST","GET"])
def check():
    #Pull variables from professor form
    ccode = request.args.get('ccode') 
    Category = request.args.get('category')


    #Frame = decryption(ccode,Category) #Get the pd dataframe that has been decrypted

    con = sql.connect('united.db')
    c = con.cursor()
    Frame = pd.read_sql_query("SELECT * from feedback", con)
    Frame = Frame[Frame['classCode']==ccode]

    if(Frame.empty): #if the frame is empty, no class exists
        return render_template('ClassNotFound.html',title='CNF')

    elif(len(Frame.index) < 10): #If the whole datatable is smaller than 10 values
        PassFrame = Frame
        return render_template('notEnoughData.html', title='NED',data=PassFrame)
    
    #Checks the size of the data depending on what category
    else:
        Show=calc(ccode,Category)
        if(Category == 'Instructor'):
            Frame = Frame[Frame['elaborateNumber']== "Instructor/Professor"]
            PassFrame = Frame
            if(len(Frame.index) < 10):
                return render_template('notEnoughData.html',title='NED', data=PassFrame)
            else:
                return render_template('analytics.html',title='data', data=PassFrame,display=Show)
        
        elif(Category == 'Teaching-style'):
            Frame = Frame[Frame['elaborateNumber'] == "Teaching style"]
            PassFrame = Frame
            if(len(Frame.index) < 10):
                return render_template('notEnoughData.html',title='NED', data=PassFrame)
            else:
                return render_template('analytics.html',title='data', data=PassFrame,display=Show)
        
        elif(Category == 'Topic'):
            Frame = Frame[Frame['elaborateNumber'] == "Topic"]
            PassFrame = Frame
            if(len(Frame.index) < 10):
                return render_template('notEnoughData.html',title='NED', data=PassFrame)
            else:
                return render_template('analytics.html',title='data', data=PassFrame,display=Show)
        
        elif(Category == 'Other'):
            Frame = Frame[Frame['elaborateNumber'] == "Other"]
            PassFrame = Frame
            if(len(Frame.index) < 10):
                return render_template('notEnoughData.html',title='NED', data=PassFrame)
            else:
                return render_template('analytics.html',title='data', data=PassFrame,display=Show)


@app.route('/analytics/plot/<classCode>&<Category>', methods=["POST","GET"]) #vars to be passed in are <classcode> and <category>. & makes sure they are seperate!
#Called by analytics.html
def drawbar(classCode,Category):

    #Match the category var to database names
    if(Category=='Instructor'):
        Category='Instructor/Professor'
    elif(Category=='Teaching-style'):
        Category='Teaching style'

    con = sql.connect('united.db')
    Frame = pd.read_sql_query("SELECT * from feedback", con)
    Frame = Frame[Frame['classCode']==classCode]
    Frame = Frame[Frame['elaborateNumber']==Category]

    fig = Figure()
    axis = fig.add_subplot(1,1,1)
    Frame = Frame['emoji'] #get just the scores
    y = [Frame[Frame==1].count(),Frame[Frame==2].count(),Frame[Frame==3].count(),Frame[Frame==4].count(),Frame[Frame==5].count()] #Count of each score
    axis.bar([1,2,3,4,5],y) #bar plot

    if(Frame.empty==False):
        if(max(y) <=10):
            Range=np.arange(0,max(y)+1,1,dtype=int)
        elif(max(y) <= 20):
            Range=np.arange(0,max(y)+2,2,dtype=int)
        elif(max(y)<=50):
            Range=np.arange(0,max(y)+5,5,dtype=int)
        elif(max(y)<=100):
            Range=np.arange(0,max(y)+10,10,dtype=int)
        else:
            Range=np.arange(0,max(y),dtype=int)
        axis.set_yticks(Range)
    axis.set_title(f'{Category} Overall')
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
    elif(Category=='Teaching-style'):
        Category='Teaching style'

    con = sql.connect('united.db')
    Frame = pd.read_sql_query("SELECT * from feedback", con)
    Frame = Frame[Frame['classCode']==classCode]
    Frame = Frame[Frame['elaborateNumber']==Category]

    Frame = Frame['emoji'] #Get just the numbers
    return f'Your average score is {round(Frame.mean(),2)}' # #return the mean

@app.route('/analytics/plottime/today/<classCode>&<Category>', methods=["POST","GET"])
#Called by Analytics.html 
def drawtimetoday(classCode,Category):
    
    #Match the category var to database names
    if(Category=='Instructor'):
        Category='Instructor/Professor'
    elif(Category=='Teaching-style'):
        Category='Teaching style'

    con = sql.connect('united.db')
    Frame = pd.read_sql_query("SELECT * from feedback", con)
    Frame = Frame[Frame['classCode']==classCode]
    Frame = Frame[Frame['elaborateNumber']==Category]

    dateNow = date.today() #Get today's date
    
    Frame = Frame[Frame['date'] == f'{dateNow}'] #Filter the frame to pull data for today
    
    Frame = Frame['emoji'] #Get just the numbers
    
    fig = Figure()
    axis = fig.add_subplot(1,1,1)
    y = [Frame[Frame==1].count(),Frame[Frame==2].count(),Frame[Frame==3].count(),Frame[Frame==4].count(),Frame[Frame==5].count()] #Count of each score
    axis.bar([1,2,3,4,5],y) #bar plot
    
    if(Frame.empty==False):
        if(max(y) <=10):
            Range=np.arange(0,max(y)+1,1,dtype=int)
        elif(max(y) <= 20):
            Range=np.arange(0,max(y)+2,2,dtype=int)
        elif(max(y)<=50):
            Range=np.arange(0,max(y)+5,5,dtype=int)
        elif(max(y)<=100):
            Range=np.arange(0,max(y)+10,10,dtype=int)
        else:
            Range=np.arange(0,max(y),dtype=int)
        axis.set_yticks(Range)
    axis.set_title(f'{Category} for Today')
    axis.set_xlabel('Score')
    axis.set_ylabel('Count')

    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route('/analytics/plottime/yesterday/<classCode>&<Category>', methods=["POST","GET"])
#Called by Analytics.html 
def drawtimeyest(classCode,Category):
    
    #Match the category var to database names
    if(Category=='Instructor'):
        Category='Instructor/Professor'
    elif(Category=='Teaching-style'):
        Category='Teaching style'

    con = sql.connect('united.db')
    Frame = pd.read_sql_query("SELECT * from feedback", con)
    Frame = Frame[Frame['classCode']==classCode]
    Frame = Frame[Frame['elaborateNumber']==Category]

    dateNow = date.today() #Get today's date
    Yest = timedelta(days=-1) #One day ago
    dateYest = dateNow + Yest #Get the date for yesterday

    Frame = Frame[Frame['date'] == f'{dateYest}'] #Filter frame based on dates from yesterday

    Frame = Frame['emoji'] #Get just the numbers
    
    fig = Figure()
    axis = fig.add_subplot(1,1,1)
    y = [Frame[Frame==1].count(),Frame[Frame==2].count(),Frame[Frame==3].count(),Frame[Frame==4].count(),Frame[Frame==5].count()] #Count of each score
    axis.bar([1,2,3,4,5],y) #bar plot
    
    if(Frame.empty==False):
        if(max(y) <=10):
            Range=np.arange(0,max(y)+1,1,dtype=int)
        elif(max(y) <= 20):
            Range=np.arange(0,max(y)+2,2,dtype=int)
        elif(max(y)<=50):
            Range=np.arange(0,max(y)+5,5,dtype=int)
        elif(max(y)<=100):
            Range=np.arange(0,max(y)+10,10,dtype=int)
        else:
            Range=np.arange(0,max(y),dtype=int)
        axis.set_yticks(Range)
    axis.set_title(f'{Category} for Yesterday')
    axis.set_xlabel('Score')
    axis.set_ylabel('Count')

    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route('/analytics/plottime/week/<classCode>&<Category>', methods=["POST","GET"])
#Called by Analytics.html 
def drawtimeweek(classCode,Category):
    
    #Match the category var to database names
    if(Category=='Instructor'):
        Category='Instructor/Professor'
    elif(Category=='Teaching-Style'):
        Category='Teaching style'

    con = sql.connect('united.db')
    Frame = pd.read_sql_query("SELECT * from feedback", con)
    Frame = Frame[Frame['classCode']==classCode]
    Frame = Frame[Frame['elaborateNumber']==Category]

    dateNow = date.today() #Get today's date
    Week = timedelta(days=-7) #Seven days earlier
    dateWeek = dateNow + Week #Get the date for 1 week ago

    Frame = Frame[Frame['date'] >= f'{dateWeek}'] #Filter the frame based on dates within the last week

    Frame = Frame['emoji'] #Get just the numbers
    
    fig = Figure()
    axis = fig.add_subplot(1,1,1)
    y = [Frame[Frame==1].count(),Frame[Frame==2].count(),Frame[Frame==3].count(),Frame[Frame==4].count(),Frame[Frame==5].count()] #Count of each score
    axis.bar([1,2,3,4,5],y) #bar plot
    
    if(Frame.empty==False):
        if(max(y) <=10):
            Range=np.arange(0,max(y)+1,1,dtype=int)
        elif(max(y) <= 20):
            Range=np.arange(0,max(y)+2,2,dtype=int)
        elif(max(y)<=50):
            Range=np.arange(0,max(y)+5,5,dtype=int)
        elif(max(y)<=100):
            Range=np.arange(0,max(y)+10,10,dtype=int)
        else:
            Range=np.arange(0,max(y),dtype=int)
        axis.set_yticks(Range)
    axis.set_title(f'{Category} for the Last Week')
    axis.set_xlabel('Score')
    axis.set_ylabel('Count')

    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response


if __name__ == '__main__':
    # app.secret_key = os.urandom(12)

    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    weirdsession = flaskGlobalSession()
    weirdsession.init_app(app)
    app.run(debug=True)
    