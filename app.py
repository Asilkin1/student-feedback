# Flask barebones
from flask import Flask, render_template, request, redirect, url_for, make_response
from models import create_post, get_posts, delete_posts, create_class, get_class, delete_class
from datetime import date, datetime
import time
import random
import sqlite3 as sl
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
    classCode = request.args.get('classCode')
    studentCode = request.args.get('studentCode')
    if request.method == 'GET':
        # Delete existing data in database (can change this later)
        # delete_posts()
        pass

    if request.method == 'POST':
        # Date
        dateNow = date.today()

        # Time
        currentTime = datetime.now()
        timeNow = currentTime.strftime("%I:%M %p")

        # Emoji number
        emoji = request.form.get('emoji')

        # Elaborate number
        elaborateNumber = request.form.get('elaborateNumber')

        # Elaborate text
        elaborateText = request.form.get('elaborateText')

        # create data in database
        create_post(dateNow, timeNow, classCode, studentCode, emoji, elaborateNumber, elaborateText)

    return render_template('student.html', title='student')



#The "Dashboard" of the professor. Right now shows any classes that they create along with its class code and has a button to create a new class
@app.route('/professor', methods=["POST", "GET"])
def submission():
    con = sl.connect('prof.db')
    c = con.cursor()
    result = c.execute("SELECT * FROM account").fetchall()
    con.close()

    return render_template('dashboard.html', title='dashboard', data = result)

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
        return redirect(url_for('submission'))

    return render_template('professor.html', title='professor')


@app.route('/professorStats', methods=["POST", "GET"])
def instructor():
    return render_template('professorStats.html', title='instructor')

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
    app.run(debug=True)
