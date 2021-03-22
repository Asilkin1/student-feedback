# All router to professor pages
from flask import Blueprint, stream_with_context,Response, render_template,request, flash, session, redirect, url_for, jsonify
import random
import pandas as pd
import time
from datetime import datetime
from CreateUserDatabase import *
import json
from sqlalchemy import event
from globalTime import utc2local
from datetime import timedelta
from threading import Thread
from cache import cache
from professor.logic import *  # REST API for professor routes
random.seed()
thread = None

professor_bp = Blueprint('professor_bp', __name__,
    template_folder='templates',
    static_folder='static')

# generate feedbacks data
def generate_feedbacks_by_category():
    '''Show datatable with @class_name, @class_code, @categories'''
     # Get classes data for current username
    dashboardData = databaseConnection.query(Account).\
    filter(Account.username == session.get('username'))
    categoryData = databaseConnection.query(Categories).filter(Categories.classCode == Account.classCode)

    yield render_template('login.html',
                            title='dashboard',
                            data=dashboardData,
                            categoryData=categoryData,
                            )
# ---------------
#  REST API     |
# ---------------

# ---------------------------------------------Get categories for selected class
@professor_bp.route('/chart-data/showCategories/<classCode>')
def get_categories_for_class(classCode):
    '''Get categories for selected class'''
    global thread
    
    if thread is None:
        thread = Thread(target=print_log_thread('/chart-data/showCategories/<classCode>'))
        thread.daemon = True
        thread.start()

    # get categories only for this classcode
    categoryData = databaseConnection.query(Categories).filter(Categories.classCode == classCode)

    # categories existed for this professor
    presentCategories = []
    wN = {}
    
    for category in categoryData:
            if classCode == category.classCode:
                presentCategories.append(category.category + '(' + classCode + ')')
                # Count feedback for each category
                wN[category.category] = 0
   
    # Get all feedbacks for the class
    query = databaseConnection.query(Feedback).filter(Feedback.classCode == classCode)
    result = query.all()

    # Go over all results
    for i in result:
        for key in wN:
            if list(wN.keys()).index(key)+1 == int(mysql_aes_decrypt(i.elaborateNumber, random_key)):
                wN[key] += 1  #wN['test'] += 1

    json_data = json.dumps(
                    {
                        'categories':presentCategories,
                        'feedbackCount':wN
                    })
    return jsonify(result=json_data)

# ---------------------------------------------Get average of 10 last votes
@professor_bp.route('/chart-data/average/<classCode>')
def get_average_rating(classCode):
    '''Get average from last 10 feedbacks'''
    avg,two,three = get_emoji_cached(classCode)
    json_data = json.dumps(
                    {
                        'average':sum(avg),
                    })
    return jsonify(result=json_data)

# ---------------------------------------------Get feedback percentages
@professor_bp.route('/chart-data/percentage/<classCode>')
def get_percentage(classCode):
    '''Get percentage for each feeling'''
    # Get all feedbacks for this classCode
    get_categories = databaseConnection.query(Feedback).filter(Feedback.classCode == classCode)
    g_c_result = get_categories.all()
    
    # Get class size
    get_class_size = databaseConnection.query(Account).filter(Account.classCode == classCode)
    g_c_s = get_class_size.all()
    
    excited = []
    und = []
    neutral = []
    tired = []
    anxious = []
    
    if g_c_result:
        for i in g_c_result:
            res = int(mysql_aes_decrypt(i.elaborateNumber, random_key))
            
            if res == 5:
                excited.append(res)
            if res == 4:
                und.append(res)
            if res == 3:
                neutral.append(res)
            if res == 2:
                tired.append(res)
            if res == 1:
                anxious.append(res)
            
    json_data = json.dumps(
                    {
                        'excited': len(excited),
                        'understand':len(und),
                        'neutral':len(neutral),
                        'tired':len(tired),
                        'anxious': len(anxious)
                    })
    return jsonify(cat=json_data)
    

# ---------------------------------------------Get categories voted
@professor_bp.route('/chart-data/categoriesVoted/<classCode>')
def categories_voted(classCode):
    '''Get categories voted for'''
    categories_voted = get_class_categories_voted(classCode)
    json_data = json.dumps(
                    {
                        'categoriesVoted':categories_voted,
                    })
    return jsonify(categories_voted=json_data)

# ----------------------------------------------Get student code voted
@professor_bp.route('/chart-data/studentcode/<classCode>')
def get_latest_studentcode(classCode):
    '''Get student code'''
    code = get_student_code(classCode)
    json_data = json.dumps(
                    {
                        'scode':code,
                    })
    return jsonify(scode=json_data)

@professor_bp.route('/chart-data/<classCode>')
def chart_data(classCode):
    # call cached function here
    last_ten, lastTimes, lastIDs= get_emoji_cached(classCode)
    excitedArr = []
    understandArr = []
    neutralArr = []
    tiredArr = []
    anxiousArr = []
    excitedID = []
    understandID = []
    neutralID = []
    tiredID = []
    anxiousID = []
    excited = {}
    understand = {}
    neutral = {}
    tired = {}
    anxious = {}
    i = 0
    for emoji in last_ten:
        if emoji == 5:
            excitedArr.append(len(excitedArr)+1)
            excitedID.append(lastIDs[i])
            excited[lastTimes[i]] = len(excitedArr)
            i += 1
        if emoji == 4:
            understandArr.append(len(understandArr)+1)
            understandID.append(i)
            understand[lastTimes[i]] = len(understandArr)
            i += 1
        if emoji == 3:
            neutralArr.append(len(neutralArr)+1)
            neutralID.append(i)
            neutral[lastTimes[i]] = len(neutralArr)
            i += 1
        if emoji == 2:
            tiredArr.append(len(tiredArr)+1)
            tiredID.append(i)
            tired[lastTimes[i]] = len(tiredArr)
            i += 1
        if emoji == 1:
            anxiousArr.append(len(anxiousArr)+1)
            anxiousID.append(i)
            anxious[lastTimes[i]] = len(anxiousArr)
            i += 1
    def generate_random_data(classCode):
        try:
            # Send result
            time.sleep(5)
            json_data = json.dumps(
                    {
                        'value':get_emoji(classCode),
                        'id': get_id(classCode),
                        'last10':sum(last_ten),
                        'numberOfFeedback':10,
                        'studentID':get_student_code(classCode)
                    })
            yield f"data:{json_data}\n\n"
        except Exception as e:
            return Response('Error! ' + str(e))
        
    return Response(generate_random_data(classCode), mimetype='text/event-stream')
    
    
# Show page which will get the data
@professor_bp.route('/get-chart/<classCode>')
def get_chart(classCode):
    last_ten, lastTimes, lastIDs= get_emoji_cached(classCode)
    excitedArr = []
    understandArr = []
    neutralArr = []
    tiredArr = []
    anxiousArr = []
    excitedID = []
    understandID = []
    neutralID = []
    tiredID = []
    anxiousID = []
    excited = {}
    understand = {}
    neutral = {}
    tired = {}
    anxious = {}
    i = 0
    for emoji in last_ten:
        if emoji == 5:
            excitedArr.append(len(excitedArr)+1)
            excitedID.append(lastIDs[i])
            excited[lastTimes[i]] = len(excitedArr)
            i += 1
        if emoji == 4:
            understandArr.append(len(understandArr)+1)
            understandID.append(i)
            understand[lastTimes[i]] = len(understandArr)
            i += 1
        if emoji == 3:
            neutralArr.append(len(neutralArr)+1)
            neutralID.append(i)
            neutral[lastTimes[i]] = len(neutralArr)
            i += 1
        if emoji == 2:
            tiredArr.append(len(tiredArr)+1)
            tiredID.append(i)
            tired[lastTimes[i]] = len(tiredArr)
            i += 1
        if emoji == 1:
            anxiousArr.append(len(anxiousArr)+1)
            anxiousID.append(i)
            anxious[lastTimes[i]] = len(anxiousArr)
            i += 1
    
    return render_template('test_stream.html', classCode=classCode, last_ten = last_ten, lastTimes = lastTimes, lastIDs = lastIDs, excitedArr = excitedArr,
                            understandArr = understandArr, neutralArr = neutralArr, tiredArr = tiredArr, anxiousArr = anxiousArr,
                            excitedID = excitedID, understandID = understandID, neutralID = neutralID, tiredID = tiredID, anxiousID = anxiousID, 
                            excited=excited, understand=understand, neutral=neutral, tired=tired, anxious=anxious)

# Ask to login for any routes in professor
@professor_bp.before_request
def before_request():
    session.permanent = True
    professor_bp.permanent_session_lifetime = timedelta(minutes=95)
    if not session.get('logged_in'):
        flash('Please log in to gain access to the website.', 'info')
        return render_template('login.html')

@professor_bp.route('/professor', methods=["POST", "GET"])
def instructor():
    return Response(stream_with_context(generate_feedbacks_by_category()))


