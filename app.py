# Flask barebones
from flask import Flask, render_template, request, redirect, url_for
from models import create_post, get_posts, delete_posts
from datetime import date, datetime
import time
import random
from wtforms import Form, validators, TextField

from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'studentfeedback'

mysql = MySQL(app)

classCode = ""
studentCode = ""

@app.route('/', methods=["POST", "GET"])
def index():
    return render_template('submit.html', title='submit')
    
@app.route("/student/login", methods=["GET", "POST"])
def studentLogin():
    if request.method == 'POST':    
        classCode = request.form['classCode']
        studentCode = request.form['studentCode']

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO users (classCode, studentCode) values (%s, %s)", (classCode, studentCode))

        mysql.connection.commit()
        cur.close()
        print(classCode)
        return render_template('student.html', title='student')

    return render_template('studentLogin.html', title='login')

@app.route('/student', methods=["POST", "GET"])
def student():
    if request.method == 'GET':
        #Delete existing data in database (can change this later)
        delete_posts()

    if request.method == 'POST':
        cur = mysql.connection.cursor()

        cur.execute("select * from users order by uid desc limit 1")
        content = cur.fetchone()
        print(content)

        #Get class and student codes
        classCode = content[1]
        studentCode = content[2]

        print(classCode)
        #Date
        dateNow = date.today()

        #Time
        currentTime = datetime.now()
        timeNow = currentTime.strftime("%I:%M %p")

        #Emoji number
        emoji = request.form.get('emoji')

        #class code
        #classCode = request.form.get('classCode')

        #Student code
        #studentCode = request.form.get('studentCode')

        #Elaborate number
        elaborateNumber = request.form.get('elaborateNumber')

        #Elaborate text
        elaborateText = request.form.get('elaborateText')

        #create data in database
        create_post(dateNow, timeNow, classCode, studentCode, emoji, elaborateNumber, elaborateText)

    return render_template('student.html', title='student')

@app.route('/professor', methods=["POST", "GET"])
def instructor():
    return render_template('professor.html', title='instructor')

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
