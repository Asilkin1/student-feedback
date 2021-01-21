# Flask barebones
from flask import Flask, render_template, request, redirect, url_for
from models import create_post, get_posts, delete_posts
from datetime import date, datetime
import time
import sqlite3 as sql
import pandas as pd

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

@app.route('/professor.html', methods=["POST", "GET"])
def instructor():

    return render_template('professor.html', title='instructor')

@app.route('/professorData/<classCode>', methods=["POST", "GET"])
def data(classCode):
    if request.method == 'POST':
        ROOT = path.dirname(path.relpath((__file__))) #Filepath for database
        con = sql.connect(path.join(ROOT, 'database.db')) #connect to the database

        Frame = pd.read_sql_query("SELECT * from feedback", con) #Database to Pandas
        Frame = Frame[Frame['classCode']== classCode] #Filter Database by class code
        if(Frame.empty):
            #Return 'Class does not exist' message
        elif(len(Frame.index)<10):
            #Return 'There is not sufficient data' and display table only
        else:
            #Category Graphs#
            #Professor
            Frame = Frame[Frame['elaborateNumber']=="Instructor/Professor"]
            if(len(Frame.index)<10):
                #Return 'There is not sufficient data' and display table only
            else:
                hist = Frame.hist(bins = int(len(Frame.index)/2))
                
            #Teaching Style
            Frame = Frame[Frame['elaborateNumber']=="Teaching Style"]
            if(len(Frame.index)<10):
                #Return 'There is not sufficient data' and display table only
            else:
                hist = Frame.hist(bins = int(len(Frame.index)/2))

            #Topic
            Frame = Frame[Frame['elaborateNumber']=="Topic"]
            if(len(Frame.index)<10):
                #Return 'There is not sufficient data' and display table only
            else:
                hist = Frame.hist(bins = int(len(Frame.index)/2))

            #Other
            Frame = Frame[Frame['elaborateNumber']=="Other"]
            if(len(Frame.index)<10):
                #Return 'There is not sufficient data' and display table only
            else:
                hist = Frame.hist(bins = int(len(Frame.index)/2))

    return render_template('professorData.html', title='data')

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
