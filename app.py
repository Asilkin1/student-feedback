# Flask barebones
from flask import Flask, render_template, request, redirect, url_for, make_response
from models import create_post, get_posts, delete_posts
from datetime import date, datetime
import time
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3 as sql

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io

app = Flask(__name__)


@app.route('/', methods=["POST", "GET"])
def index():
    return render_template('index.html', title='submit')


@app.route('/analytics', methods=["POST", "GET"])
def analytics():
    return render_template('analytics.html', title='stats')


@app.route('/signup', methods=["POST", "GET"])
def signup():
    return render_template('signup.html', title='signup')


@app.route('/student', methods=["POST", "GET"])
def student():
    if request.method == 'GET':
        # Delete existing data in database (can change this later)
        # delete_posts()
        pass

    if request.method == 'POST':
        # Date
        dateNow = date.today()

        # Time
        #timeNow = time.asctime().split(' ')[3]
        currentTime = datetime.now()
        timeNow = currentTime.strftime("%I:%M %p")

        # Emoji number
        emoji = request.form.get('emoji')

        # class code
        classCode = request.form.get('classCode')

        # Student code
        studentCode = request.form.get('studentCode')

        # Elaborate number
        elaborateNumber = request.form.get('elaborateNumber')

        # Elaborate text
        elaborateText = request.form.get('elaborateText')

        # create data in database
        create_post(dateNow, timeNow, classCode, studentCode,
                    emoji, elaborateNumber, elaborateText)

    return render_template('student.html', title='student')


@app.route('/professor', methods=["POST", "GET"])
def instructor():
    return render_template('professor.html', title='instructor')

@app.route('/analytics/check',methods=["POST","GET"])
def check():
    classCode = "AB123"
    Category = 'Instructor/Professor'
    
    con = sql.connect('database.db') # connect to the database

    Frame = pd.read_sql_query("SELECT * from feedback", con)  # Database to Pandas
    # Filter Database by class code
    Frame = Frame[Frame['classCode'] == classCode]
    if(Frame.empty):
        # Return 'Class does not exist' message
        pass
    elif(len(Frame.index) < 10):
        return render_template('notEnoughData.html', title='NED')
    else:
        if(Category == 'Instructor/Professor'):
            Frame = Frame[Frame['elaborateNumber']== "Instructor/Professor"]
            if(len(Frame.index) < 10):
                return False
            else:
                return True
        elif(Category == 'Teaching Style'):
            Frame = Frame[Frame['elaborateNumber'] == "Teaching Style"]
            if(len(Frame.index) < 10):
                # Return 'There is not sufficient data' and display table only
                pass
            else:
                pass
        elif(Category == 'Topic'):
            Frame = Frame[Frame['elaborateNumber'] == "Topic"]
            if(len(Frame.index) < 10):
                # Return 'There is not sufficient data' and display table only
                pass
            else:
                pass
        elif(Category == 'Other'):
            Frame = Frame[Frame['elaborateNumber'] == "Other"]
            if(len(Frame.index) < 10):
                # Return 'There is not sufficient data' and display table only
                pass
            else:
                pass

@app.route('/analytics/plot', methods=["POST", "GET"])
def data():
    
    classCode = "AB123"
    Category = 'Instructor/Professor'
    con = sql.connect('database.db') # connect to the database
    Frame = pd.read_sql_query("SELECT * from feedback", con)  # Database to Pandas
    Frame = Frame[Frame['classCode'] == classCode]
    Frame = Frame[Frame['elaborateNumber']== "Instructor/Professor"]

    fig = Figure()
    axis = fig.add_subplot(1,1,1)
    axis.hist(Frame['emoji'])
    axis.set_title(Category)
    axis.set_xlabel('Score')
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response


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
