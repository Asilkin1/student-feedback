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
        create_post(dateNow, timeNow, classCode, studentCode, emoji, elaborateNumber, elaborateText)

    return render_template('student.html', title='student')


@app.route('/professor', methods=["POST", "GET"])
def instructor():
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


    if(Frame.empty):
        # Return 'Class does not exist' message
        pass
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
def draw(classCode,Category):

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
