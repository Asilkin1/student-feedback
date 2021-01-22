# Flask barebones
from flask import Flask, render_template, request, redirect, url_for
from models import create_post, get_posts, delete_posts, create_class, get_class, delete_class
from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import sqlite3 as sl
import time
import random

app = Flask(__name__)

db = SQLAlchemy()
login_manager = LoginManager()



@app.route('/', methods=["POST", "GET"])
def index():
    return render_template('submit.html', title='submit')

@app.route('/student', methods=["POST", "GET"])
def student():
    if request.method == 'GET':
        #Delete existing data in database (can change this later)
        delete_posts()

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
        classCode integer PRIMARY KEY
        );
    """)

#Right now this goes to the /professor part of the website. As this is a sign up page it should probably be changed to something like /professor/signup and go back to /professor when finished
@app.route('/professor/create', methods=["POST", "GET"])
def professor():
    con = sl.connect('prof.db')
    inData = True
    
    if request.method == 'GET':
        #Delete existing data in database (can change this later)
        delete_posts()
    
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

    return render_template('professor.html', title='professor')

@app.route('/professor/0', methods=["POST", "GET"])
def submission():
    return render_template('professor.html', title='professor')

if __name__ == '__main__':
    app.run(debug=True)

# # Flask barebones
# from flask import Flask, render_template, request, redirect, url_for

# app = Flask(__name__)

# @app.route('/', methods=["POST", "GET"])
# def index():
#     return render_template('index.html', title='submit')

# @app.route('/student.html', methods=["POST", "GET"])
# def student():
#     # If POST methods
#     if request.method == "POST":
        
#         # Get mood from the form
#         mood = request.form['mood']

#         # Get elaborate stats
#         elaborate = request.form['elaborate']

#         # Get desc
#         desc = request.form['desc'] # This doesn work

#         # Let see what it will print
#         print(mood,elaborate,desc)

#         return render_template('student.html', title='student')
    
#     if request.method == "GET":
#         return render_template('student.html', title='student')

# @app.route('/professor.html', methods=["POST", "GET"])
# def instructor():
#     return render_template('professor.html', title='instructor')


# if __name__ == '__main__':
#     app.run(debug=True)
