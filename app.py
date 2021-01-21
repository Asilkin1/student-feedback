# Flask barebones
from flask import Flask, render_template, request, redirect, url_for
from models import create_post, get_posts, delete_posts
from datetime import date, datetime
import time
import random

app = Flask(__name__)

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




import sqlite3 as sl

#Creates a database via SQLite to store Professor information
con = sl.connect('output.db')
with con:
    con.execute("""
        CREATE TABLE IF NOT EXISTS Prof (
        ProfessorName TEXT,
        SchoolName TEXT,
        DepartmentName TEXT,
        ClassID INTEGER NOT NULL,
        SectionName TEXT,
        ClassCode INTEGER NOT NULL
        );
    """)


@app.route('/professor', methods=["POST", "GET"])
def professor():
    #Replace this later by instead searching through the professor database
    codeList = []
    #Keep this though
    inList = True
    if request.method == 'POST':
        #Professors unique class code (Randomly generated)
        classCode = random.randrange(1,3000,1)
        #Checks the list of existing codes to make sure the one currently generated is unique
        while inList:
            for i in codeList:
                if codeList[i] == classCode:
                    inList = True
                    print(inList)
                break
            classCode = random.randrange(1,20,1)
        codeList.append(classCode)
        #Prints it out for debuggin purposes, should always be unique
        print(classCode)

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

        #create data in database
        #Todo
        #(professorName, schoolName, departmentName, classId, sectionName, classCode)

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
