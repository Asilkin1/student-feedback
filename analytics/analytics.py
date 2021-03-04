from flask import Blueprint, render_template,request,make_response
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sqlite3 as sql

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io

from encryption import *
from CreateUserDatabase import *

analytics_bp = Blueprint('analytics_bp', __name__,
    template_folder='templates',
    static_folder='static')

# Routes for the analyrics page
@analytics_bp.route('/analytics/check/',methods=["POST", "GET"])
def check():
    # Pull variables from professor form
    ccode = request.args.get('ccode')
    Category = request.args.get('category')

    query = databaseConnection.query(Categories).filter(Categories.category == Category)
    result = query.first()

    Category = result.number

    Frame = pd.read_sql_query("SELECT * from Feedback", engine)
    Frame = Frame[Frame['classCode']==ccode]
    # This should be decrypted now
    Frame = decrypt_frame(Frame)

    if(Frame.empty):  # if the frame is empty, no class exists
        return render_template('ClassNotFound.html', title='CNF')

    elif(len(Frame.index) < 10):  # If the whole datatable is smaller than 10 values
        Frame = Frame[Frame['elaborateNumber'] == Category]
        PassFrame = Frame
        return render_template('notEnoughData.html', title='NED', data=PassFrame)

    # Checks the size of the data depending on what category
    else:
        Show = calc(ccode, Category)
        if Category:
            Frame = Frame[Frame['elaborateNumber'] == Category]
            PassFrame = Frame
            if(len(Frame.index) < 10):
                return render_template('notEnoughData.html', title='NED', data=PassFrame)
            else:
                return render_template('analytics.html',title='data', data=PassFrame, display=Show)

# vars to be passed in are <classcode> and <category>. & makes sure they are seperate!
@analytics_bp.route('/analytics/plot/<classCode>&<Category>', methods=["POST", "GET"])
# Called by analytics.html
def drawbar(classCode, Category):
    query = databaseConnection.query(Categories).filter(Categories.category == Category)
    result = query.first()

    Category = result.number

    # Should have decryption here?
    Frame = pd.read_sql_query("SELECT * from feedback", engine)
    Frame = Frame[Frame['classCode'] == classCode]

    Frame = decrypt_frame(Frame)

    Frame = Frame[Frame['elaborateNumber'] == Category]

    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    Frame = Frame['emoji']  # get just the scores
    y = [Frame[Frame == 1].count(), Frame[Frame == 2].count(), Frame[Frame == 3].count(
    ), Frame[Frame == 4].count(), Frame[Frame == 5].count()]  # Count of each score
    axis.bar([1, 2, 3, 4, 5], y)  # bar plot

    if(Frame.empty == False):
        if(max(y) <= 10):
            Range = np.arange(0, max(y)+1, 1, dtype=int)
        elif(max(y) <= 20):
            Range = np.arange(0, max(y)+2, 2, dtype=int)
        elif(max(y) <= 50):
            Range = np.arange(0, max(y)+5, 5, dtype=int)
        elif(max(y) <= 100):
            Range = np.arange(0, max(y)+10, 10, dtype=int)
        else:
            Range = np.arange(0, max(y), dtype=int)
        axis.set_yticks(Range)
    axis.set_title(f'{Category} Overall')
    axis.set_xlabel('Score')
    axis.set_ylabel('Count')

    # Flask stuff to print plot
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@analytics_bp.route('/analytics/calc/<classCode>&<Category>', methods=["POST", "GET"])
# Called by Analytics.html
def calc(classCode, Category):
    Frame = pd.read_sql_query("SELECT * from feedback", engine)
    Frame = Frame[Frame['classCode'] == classCode]

    Frame = decrypt_frame(Frame)

    Frame = Frame[Frame['elaborateNumber'] == Category]

    Frame = Frame['emoji']  # Get just the numbers
    return f'Your average score is {round(Frame.mean(),2)}'  # return the mean

@analytics_bp.route('/analytics/plottime/today/<classCode>&<Category>', methods=["POST", "GET"])
# Called by Analytics.html
def drawtimetoday(classCode, Category):
    query = databaseConnection.query(Categories).filter(Categories.category == Category)
    result = query.first()

    Category = result.number

    Frame = pd.read_sql_query("SELECT * from feedback", engine)
    # This looks stil encrypted
    Frame = Frame[Frame['classCode'] == classCode]

    Frame = decrypt_frame(Frame)
    Frame = Frame[Frame['elaborateNumber'] == Category]

    dateNow = date.today()  # Get today's date

    # Filter the frame to pull data for today
    Frame = Frame[Frame['date'] == f'{dateNow}']

    Frame = Frame['emoji']  # Get just the numbers

    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    y = [Frame[Frame == 1].count(), Frame[Frame == 2].count(), Frame[Frame == 3].count(
    ), Frame[Frame == 4].count(), Frame[Frame == 5].count()]  # Count of each score
    axis.bar([1, 2, 3, 4, 5], y)  # bar plot

    if(Frame.empty == False):
        if(max(y) <= 10):
            Range = np.arange(0, max(y)+1, 1, dtype=int)
        elif(max(y) <= 20):
            Range = np.arange(0, max(y)+2, 2, dtype=int)
        elif(max(y) <= 50):
            Range = np.arange(0, max(y)+5, 5, dtype=int)
        elif(max(y) <= 100):
            Range = np.arange(0, max(y)+10, 10, dtype=int)
        else:
            Range = np.arange(0, max(y), dtype=int)
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

@analytics_bp.route('/analytics/plottime/yesterday/<classCode>&<Category>', methods=["POST", "GET"])
# Called by Analytics.html
def drawtimeyest(classCode, Category):
    query = databaseConnection.query(Categories).filter(Categories.category == Category)
    result = query.first()

    Category = result.number

    # Get all items from database
    Frame = pd.read_sql_query("SELECT * from feedback", engine)
    Frame = Frame[Frame['classCode'] == classCode]

    Frame = decrypt_frame(Frame)

    Frame = Frame[Frame['elaborateNumber'] == Category]

    dateNow = date.today()  # Get today's date
    Yest = timedelta(days=-1)  # One day ago
    dateYest = dateNow + Yest  # Get the date for yesterday

    # Filter frame based on dates from yesterday
    Frame = Frame[Frame['date'] == f'{dateYest}']

    Frame = Frame['emoji']  # Get just the numbers

    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    y = [Frame[Frame == 1].count(), Frame[Frame == 2].count(), Frame[Frame == 3].count(
    ), Frame[Frame == 4].count(), Frame[Frame == 5].count()]  # Count of each score
    axis.bar([1, 2, 3, 4, 5], y)  # bar plot

    if(Frame.empty == False):
        if(max(y) <= 10):
            Range = np.arange(0, max(y)+1, 1, dtype=int)
        elif(max(y) <= 20):
            Range = np.arange(0, max(y)+2, 2, dtype=int)
        elif(max(y) <= 50):
            Range = np.arange(0, max(y)+5, 5, dtype=int)
        elif(max(y) <= 100):
            Range = np.arange(0, max(y)+10, 10, dtype=int)
        else:
            Range = np.arange(0, max(y), dtype=int)
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

@analytics_bp.route('/analytics/plottime/week/<classCode>&<Category>', methods=["POST", "GET"])
# Called by Analytics.html
def drawtimeweek(classCode, Category):
    query = databaseConnection.query(Categories).filter(Categories.category == Category)
    result = query.first()

    Category = result.number

    Frame = pd.read_sql_query("SELECT * from feedback", engine)
    Frame = Frame[Frame['classCode'] == classCode]

    Frame = decrypt_frame(Frame)

    Frame = Frame[Frame['elaborateNumber'] == Category]

    dateNow = date.today()  # Get today's date
    Week = timedelta(days=-7)  # Seven days earlier
    dateWeek = dateNow + Week  # Get the date for 1 week ago

    # Filter the frame based on dates within the last week
    Frame = Frame[Frame['date'] >= f'{dateWeek}']

    Frame = Frame['emoji']  # Get just the numbers

    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    y = [Frame[Frame == 1].count(), Frame[Frame == 2].count(), Frame[Frame == 3].count(
    ), Frame[Frame == 4].count(), Frame[Frame == 5].count()]  # Count of each score
    axis.bar([1, 2, 3, 4, 5], y)  # bar plot

    if(Frame.empty == False):
        if(max(y) <= 10):
            Range = np.arange(0, max(y)+1, 1, dtype=int)
        elif(max(y) <= 20):
            Range = np.arange(0, max(y)+2, 2, dtype=int)
        elif(max(y) <= 50):
            Range = np.arange(0, max(y)+5, 5, dtype=int)
        elif(max(y) <= 100):
            Range = np.arange(0, max(y)+10, 10, dtype=int)
        else:
            Range = np.arange(0, max(y), dtype=int)
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

@analytics_bp.route('/professor/analytics/<classCode>', methods=["POST", "GET"])
def analytics(classCode):
    Frame = pd.read_sql_query("SELECT * from Feedback", engine)
    Frame = Frame[Frame['classCode']==classCode]
    # This should be decrypted now
    Frame = decrypt_frame(Frame)

    # Get total voters for the class
    totalVoters = databaseConnection.query(Feedback.studentCode).filter(Feedback.classCode == classCode).distinct().count()
    # Get total feedbacks
    totalFeedback = databaseConnection.query(Feedback).filter(Feedback.classCode == classCode).count()
    return render_template('viewAllFeedback.html', 
                            title='All Feedback', 
                            data=Frame, 
                            size=get_class_size(classCode),  
                            total=totalVoters,
                            totalFeedback = totalFeedback)
