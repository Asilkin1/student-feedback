# Flask barebones
from flask import Flask, render_template, request, redirect, url_for,session, abort,flash, make_response #Flask Stuff
from models import create_post, get_posts, delete_posts,create_class
from datetime import date, datetime, timedelta #get date and time
from sqlalchemy.orm import sessionmaker #Making Sessions and login
from CreateUserDatabase import *    # Table for Users
import time #date and time
import os #filepath

import matplotlib.pyplot as plt
import pandas as pd
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

# Helper functions from registration logic
from registration_logic import register

# Login engine
engine = create_engine('sqlite:///tutorial.db', echo=True)  # Connect to Users database

app = Flask(__name__)

#Class and student codes
classCode = ""
studentCode = ""

#Encryption Key
#random_key = os.urandom(16)
random_key = b"J3FTV1PL1jDFeMh01I9r+A=="
random_key = b64encode(random_key).decode('utf-8')


@app.route('/', methods=["POST", "GET"])
def index():    
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
                session['username'] = send_username
                flash('You have successfully logged in.','success')
            
                category = request.args.get('category')
                con = sl.connect('prof.db')
                c = con.cursor()
                result = c.execute("SELECT * FROM account").fetchall()
                con.close()
                return render_template('index.html', data = result)
            
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

    # Remove student codes and class code
    session.pop('classCode', None)
    session.pop('studentCode',None)

    # Feedback message
    flash('You have successfully logged out','success')
    return render_template('index.html')

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
@app.route('/newstudent', methods=['POST', 'GET'])
def newstudent():
    # Pass global var classCode and studentCode

    if request.method == "POST":
        # Get class code 
        classCode = request.form.get('classCode')
        studentCode = request.form.get('studentCode')
        
        session['classCode'] = classCode
        session['studentCode'] = studentCode
        session['logged_in'] = True

        return render_template('student.html')

    return render_template('student_sign_up.html')

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
        timeNow = time.asctime().split(' ')[3]
        currentTime = datetime.now()
        timeNow = currentTime.strftime("%I:%M %p")

        #Emoji number
        emoji = request.form.get('emoji')
        emoji = mysql_aes_encrypt(emoji, random_key)

        #Elaborate number
        elaborateNumber = request.form.get('elaborateNumber')
        elaborateNumber = mysql_aes_encrypt(elaborateNumber, random_key)

        #Elaborate text
        elaborateText = request.form.get('elaborateText')
        elaborateText = mysql_aes_encrypt(elaborateText, random_key)

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

#creates a table for professor info
con = sl.connect('prof.db')
with con:
    con.execute("""
        CREATE TABLE IF NOT EXISTS account (
        professorName text not null ,
        schoolName text not null,
        departmentName text not null,
        classId text not null,
        sectionName text not null,
        classCode integer not null,
        entryId integer PRIMARY KEY AUTOINCREMENT
        );
    """)

@app.route('/professor/create', methods=["POST", "GET"])
def professor():
    con = sl.connect('prof.db')
    inData = True
    
    if request.method == 'POST':
        #Professors unique class code (Randomly generated between x, and y with z being the amount generated)
        classCode = random.randrange(1,3000,1)

        #While loops until a random number is generated that is not already in the database
        while(inData):
            #Creates a cursor that checks if classCodes value exists at all
            cur = con.cursor()
            #Note that the , after classCode is nessassary otherwise you get an unsuported type error (turns the int into a tuple containing an int)
            cur.execute("""SELECT classCode FROM account WHERE classCode=?""", (classCode,))
            if not cur.fetchone():
                inData = False

        #Professors Name
        professorName = request.form.get('professorName')

        #Schools Name
        schoolName = request.form.get('schoolName')

        #Departments Name
        departmentName = request.form.get('departmentName')

        #Class' Id
        classId = request.form.get('classId')

        #Sections Name
        sectionName = request.form.get('sectionName')

        #adds data to database
        create_class(professorName, schoolName, departmentName, classId, sectionName, int(classCode))
        return redirect(url_for('instructorDashboard'))

    return render_template('forms/addClass.html', title='professor')


@app.route('/professor', methods=["POST", "GET"])
def instructor():
   if not session.get('logged_in'):
       flash('Please log in to gain access to the website','info')
       return render_template('login.html', title='submit')
   else:
       return render_template('professor.html')

@app.route('/professor/dashboard', methods=["POST", "GET"])
def instructorDashboard():
    session['logged_in'] = True
    category = request.args.get('category')
    con = sl.connect('prof.db')
    c = con.cursor()
    result = c.execute("SELECT * FROM account").fetchall()
    con.close()
    return render_template('index.html', title='dashboard', data = result)


# --------------------------------------------------------------------------------------------- Analytics
def decryption(classCode, Category):
    con = sql.connect('database.db')
    c = con.cursor()
    c.execute('''SELECT * FROM feedback WHERE classCode=?'''(classCode))
    
    Frame = pd.read_sql_query("SELECT * from feedback", con)

    for row in range(0,len(Frame.index)):
        Frame.at[row,'emoji'] = mysql_aes_decrypt(Frame.at[row,'emoji'],random_key)
        Frame.at[row,'elaborateNumber'] = mysql_aes_decrypt(Frame.at[row,'elaborateNumber'],random_key)
        Frame.at[row,'elaborateText'] = mysql_aes_decrypt(Frame.at[row,'elaborateText'],random_key)
    
    return Frame

#Called by professor.html
@app.route('/analytics/check',methods=["POST","GET"])
def check():
    #Pull variables from professor form
    ccode = request.args.get('classCode') 
    Category = request.args.get('category')

    Frame = decryption(ccode,Category) #Get the pd dataframe that has been decrypted

    if(Frame.empty): #if the frame is empty, no class exists
        return render_template('ClassNotFound.html',title='CNF')

    elif(len(Frame.index) < 10): #If the whole datatable is smaller than 10 values
        PassFrame = Frame
        return render_template('notEnoughData.html', title='NED',data=PassFrame)
    
    #Checks the size of the data depending on what category
    else:
        if(Category == 'Instructor'):
            Frame = Frame[Frame['elaborateNumber']== "Instructor/Professor"]
            PassFrame = Frame
            if(len(Frame.index) < 10):
                return render_template('notEnoughData.html',title='NED', data=PassFrame)
            else:
                return render_template('analytics.html',title='data', data=PassFrame)
        
        elif(Category == 'Teaching-style'):
            Frame = Frame[Frame['elaborateNumber'] == "Teaching Style"]
            PassFrame = Frame
            if(len(Frame.index) < 10):
                return render_template('notEnoughData.html',title='NED', data=PassFrame)
            else:
                return render_template('analytics.html',title='data', data=PassFrame)
        
        elif(Category == 'Topic'):
            Frame = Frame[Frame['elaborateNumber'] == "Topic"]
            PassFrame = Frame
            if(len(Frame.index) < 10):
                return render_template('notEnoughData.html',title='NED',data=PassFrame)
            else:
                return render_template('analytics.html',title='data',data=PassFrame)
        
        elif(Category == 'Other'):
            Frame = Frame[Frame['elaborateNumber'] == "Other"]
            PassFrame = Frame
            if(len(Frame.index) < 10):
                return render_template('notEnoughData.html',title='NED',data=PassFrame)
            else:
                return render_template('analytics.html',title='data',data=PassFrame)


@app.route('/analytics/plot/<classCode>&<Category>', methods=["POST","GET"]) #vars to be passed in are <classcode> and <category>. & makes sure they are seperate!
#Called by analytics.html
def drawbar(classCode,Category,Frame):

    #Match the category var to database names
    if(Category=='Instructor'):
        Category='Instructor/Professor'
    elif(Category=='Teaching-style'):
        Category='Teaching Style'
    
    fig = Figure()
    axis = fig.add_subplot(1,1,1)
    Frame = Frame['emoji'] #get just the scores
    y = [Frame[Frame==1].count(),Frame[Frame==2].count(),Frame[Frame==3].count(),Frame[Frame==4].count(),Frame[Frame==5].count()] #Count of each score
    axis.bar([1,2,3,4,5],y) #bar plot
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
def calc(classCode,Category,Frame):
    if(Category=='Instructor'):
        Category='Instructor/Professor'
    elif(Category=='Teaching-style'):
        Category='Teaching Style'

    Frame = Frame['emoji'] #Get just the numbers
    return f'Your average score was {round(Frame.mean(),2)}' #return the mean

@app.route('/analytics/plottime/today/<classCode>&<Category>', methods=["POST","GET"])
#Called by Analytics.html 
def drawtimetoday(classCode,Category,Frame):
    
    #Match the category var to database names
    if(Category=='Instructor'):
        Category='Instructor/Professor'
    elif(Category=='Teaching-style'):
        Category='Teaching Style'

    dateNow = date.today() #Get today's date

    Frame = Frame[Frame['date'] == f'{dateNow}'] #Filter the frame to pull data for today

    Frame = Frame['emoji'] #Get just the numbers
    
    fig = Figure()
    axis = fig.add_subplot(1,1,1)
    y = [Frame[Frame==1].count(),Frame[Frame==2].count(),Frame[Frame==3].count(),Frame[Frame==4].count(),Frame[Frame==5].count()] #Count of each score
    axis.bar([1,2,3,4,5],y) #bar plot
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
def drawtimeyest(classCode,Category,Frame):
    
    #Match the category var to database names
    if(Category=='Instructor'):
        Category='Instructor/Professor'
    elif(Category=='Teaching-style'):
        Category='Teaching Style'

    dateNow = date.today() #Get today's date
    Yest = timedelta(days=-1) #One day ago
    dateYest = dateNow + Yest #Get the date for yesterday

    Frame = Frame[Frame['date'] == f'{dateYest}'] #Filter frame based on dates from yesterday

    Frame = Frame['emoji'] #Get just the numbers
    
    fig = Figure()
    axis = fig.add_subplot(1,1,1)
    y = [Frame[Frame==1].count(),Frame[Frame==2].count(),Frame[Frame==3].count(),Frame[Frame==4].count(),Frame[Frame==5].count()] #Count of each score
    axis.bar([1,2,3,4,5],y) #bar plot
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
def drawtimeweek(classCode,Category,Frame):
    
    #Match the category var to database names
    if(Category=='Instructor'):
        Category='Instructor/Professor'
    elif(Category=='Teaching-Style'):
        Category='Teaching Style'

    dateNow = date.today() #Get today's date
    Week = timedelta(days=-7) #Seven days earlier
    dateWeek = dateNow + Week #Get the date for 1 week ago

    Frame = Frame[Frame['date'] >= f'{dateWeek}'] #Filter the frame based on dates within the last week

    Frame = Frame['emoji'] #Get just the numbers
    
    fig = Figure()
    axis = fig.add_subplot(1,1,1)
    y = [Frame[Frame==1].count(),Frame[Frame==2].count(),Frame[Frame==3].count(),Frame[Frame==4].count(),Frame[Frame==5].count()] #Count of each score
    axis.bar([1,2,3,4,5],y) #bar plot
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
    app.secret_key = os.urandom(12)
    app.run(debug=True)