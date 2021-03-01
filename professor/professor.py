# All router to professor pages
from flask import Blueprint, stream_with_context,Response, render_template,request, flash, session, redirect, url_for, jsonify
import random
import pandas as pd
import time
from datetime import datetime
from CreateUserDatabase import *
import json
random.seed()
from sqlalchemy import event
from globalTime import utc2local
from datetime import timedelta
from cache import cache


professor_bp = Blueprint('professor_bp', __name__,
    template_folder='templates',
    static_folder='static')


# generate feedbacks data
def generate_feedbacks_by_category():
     # Get classes data for current username
    dashboardData = databaseConnection.query(Account).filter(Account.username == session.get('username'))
    categoryData = databaseConnection.query(Categories).filter(Categories.classCode == Account.classCode)

    # categories existed for this professor
    presentCategories = []
    wN = {}

    for category in categoryData:
        for classCode in dashboardData:
            if classCode.classCode == category.classCode:
                presentCategories.append(category.category + ' (' + classCode.classCode + ')')

    query = databaseConnection.query(Account, Feedback).filter(Account.username == session.get('username'),Account.classCode == Feedback.classCode)
    result = query.all()

    # Get each category name
    for i in categoryData:
        # Add a key to the dict with a value of 0
        wN[int(i.number)] = 0

    for feedbacks in result:
        feedbacks = mysql_aes_decrypt(feedbacks.Feedback.elaborateNumber, random_key)
        if int(feedbacks) in wN:
            # Can increment that value later
            wN[int(feedbacks)] += 1
        
    yield render_template('login.html',
                            title='dashboard',
                            data=dashboardData,
                            categoryData=categoryData,
                            categoryCount=categoryData.count(),
                            present=presentCategories,
                            wN = wN,
                            within = check_date_voted 
                            )


def get_id(classCode):
    query = databaseConnection.query(Feedback.id).filter(Feedback.classCode == classCode).order_by(Feedback.id.desc())
    result = query.first()
    return result

# Get all feedbacks for the past 5 seconds  
@cache.cached(timeout=10, key_prefix='last_10_emoji_values')
def get_emoji_cached(classCode):
    '''@classCode - current class
       :returns a list of emojis values e.g. [5,4,2,1,4,1,2,3,4,5]
    '''
    emoji = 0
    accumulate = []
    # Get feedbacks by classCode
    try:
        query = databaseConnection.query(Feedback).filter(Feedback.classCode == classCode).order_by(Feedback.id.desc())
        # get last 10 feedbacks
        result = query.limit(10).all()

        # get classCodes
        ccode = databaseConnection.query(Feedback.id).filter(Feedback.classCode == classCode).order_by(Feedback.id.desc())
        ccode = query.limit(10).all()
        if result and ccode:
            for i in result:
                print('Result: ',i)
                if i.id not in ccode:
                    print('Code: ', i.id)
                    emoji = mysql_aes_decrypt(i.emoji,random_key)
                    accumulate.append(int(emoji))
    # Cannot read from the database then do something
    except:
        emoji = 0
    print('Cached function',accumulate)
    return accumulate

def get_emoji(classCode):
    # Return 0 if something goes wrong
    emoji = 0
    # Get something from the database
    try:
        query = databaseConnection.query(Feedback).filter(Feedback.classCode == classCode).order_by(Feedback.id.desc())
        result = query.first()
        if result:
            emoji = mysql_aes_decrypt(result.emoji,random_key)
    # Cannot read from the database then do something
    except:
        emoji = 0
    return emoji

def get_student_code(classCode):
    # Return 0 if something goes wrong
    studentCode = 0
    # Get something from the database
    try:
        query = databaseConnection.query(Feedback.studentCode).filter(Feedback.classCode == classCode).order_by(Feedback.id.desc())
        result = query.first()
        if result:
            studentCode = result[0]
    # Cannot read from the database then do something
    except:
        studentCode = 0
    print('Student Code: ', str(studentCode))
    return studentCode

def get_time(classCode):
    query = databaseConnection.query(Feedback.time).filter(Feedback.classCode == classCode).order_by(Feedback.id.desc())
    result = query.first()
    print('Time now: ', result)
    return result


def get_id_cached(classCode):
    '''
    @classCode - class code to identify feedbacks
    '''
    pass


def get_student_feedback_count(classCode):
    # Get distinct student codes
    student_code = databaseConnection.query(Feedback.studentCode).filter(Feedback.classCode == classCode).distinct()
    result = student_code.all()
    # How many feedbacks left by this student
    return result.count()

def sum(data):
    '''Sum all the values in the list'''
    total = 0
    for i in data:
        # Should be an integer
        total += int(i)
    return round(total / len(data))

# Streams only the data

@professor_bp.route('/chart-data/<classCode>')
def chart_data(classCode):
    # call cached function here
    last_ten = get_emoji_cached(classCode)
    def generate_random_data(classCode):
        try:
            
            # Can process data in a certain way?
            # -----------------------------microbatch
            #data = []
            # Aggregate
            #current_id = get_id(classCode)
            # Wait for 5 elements in the dataset
            #while( len(data) < 5 ):
            # See if the latest id is not the current one
                #if get_id(classCode) != current_id:
                    #print('Added')
                    #data += get_emoji(classCode)

            # Send result
            time.sleep(5)
            print("sum is ", sum(last_ten))
            json_data = json.dumps(
                    {
                        'value':get_emoji(classCode),
                        'id': get_id(classCode),
                        'last10':sum(last_ten),
                        'numberOfFeedback':10,
                        'studentID':get_student_code(classCode)
                    })
            print('Live stream')
            yield f"data:{json_data}\n\n"
        except Exception as e:
            return Response('Error! ' + str(e))
        
    return Response(generate_random_data(classCode), mimetype='text/event-stream')
    
    
# Show page which will get the data
@professor_bp.route('/get-chart/<classCode>')
def get_chart(classCode):
    return render_template('test_stream.html', classCode=classCode)

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

@professor_bp.route("/professor/delete/<id>/<ccode>", methods=['GET', 'POST'])
def deleteClass(id,ccode):
    databaseConnection.query(Account).filter(Account.entryId == int(id)).delete()
    databaseConnection.commit()
    databaseConnection.query(Feedback).filter(Feedback.classCode == ccode).delete()
    databaseConnection.commit()
    databaseConnection.query(Categories).filter(Categories.classCode == ccode).delete()
    databaseConnection.commit()

    flash('Class Deleted', 'success')
    return redirect(url_for('professor_bp.instructor'))

def deleteCategories(ccode):
    databaseConnection.query(Categories).filter(Categories.classCode == ccode).delete()
    databaseConnection.commit()

@professor_bp.route("/professor/edit/<string:id>", methods=['GET', 'POST'])
def editClass(id):
    
    query = databaseConnection.query(Account).filter(
                Account.entryId == id)
    result = query.first()

    # Populate article form fields
    schoolName = result.schoolName
    departmentName = result.departmentName
    className = result.className
    start = result.start 
    end = result.end
    days = result.days
    classCode = result.classCode
    mode = result.mode
    size = result.size

    # Parse for section
    parsingClassCode = result.classCode.split("-")
    sectionName = parsingClassCode[1]

    queryCategories = databaseConnection.query(Categories).filter(Categories.classCode == classCode)
    resultCategories = queryCategories.all()

    # Categories array
    data = []
    for category in resultCategories:
        data.append(category.category)

    if request.method == 'POST':
        deleteCategories(classCode)
        # Query feedback table for class code
        queryFeedBack = databaseConnection.query(Feedback).filter(Feedback.classCode == result.classCode)
        resultFeedback = queryFeedBack.first()

        # Parse for section in Feedback table
        if resultFeedback != None:
            parsingClassCode = resultFeedback.classCode.split("-")
            sectionFeedBack = parsingClassCode[1]
        
        # School Name
        schoolName = request.form['schoolName']

        # Department Name
        departmentName = request.form['departmentName']

        # Class Name
        className = request.form['className']

        # Section Name
        sectionName = request.form['sectionName']
        
        days = request.form.getlist('days')
        saveDays = ''

        # Start time
        start = request.form['start']

        #End time
        end = request.form['end']

        # Class mode
        mode = request.form['mode']

        # Class size
        size = request.form['size']

        # Categories
        categories = request.form.getlist('categories')
        
        # Set result in database to new result
        result.schoolName = schoolName
        result.departmentName = departmentName
        result.className = className
        result.start = start
        result.days = saveDays.join(days)
        result.end = end
        result.mode = mode
        result.size = size

        # Parse for class code
        parsingClassCode = result.classCode.split("-")
        classCode = parsingClassCode[0]

        result.classCode = str(classCode) + '-' + sectionName
        databaseConnection.commit()

        # Update class code in feedback table if the section got changed
        if resultFeedback != None:
            if sectionName != sectionFeedBack:
                for results in queryFeedBack.all():
                    results.classCode = result.classCode
        
        try:
            databaseConnection.commit()
        except:
            databaseConnection.rollback()

        # Update/add categories regardless if changed or not
        i = 1
        for category in categories:
            newCategory = Categories(result.classCode, category, str(i))
            databaseConnection.add(newCategory)
            i += 1
        databaseConnection.commit()

        flash('Class Updated', 'success')

        # Go back to the dashboard
        return redirect(url_for('professor_bp.instructor'))

    return render_template('editClass.html', entryId=id, schoolName=schoolName, departmentName=departmentName, className=className,
                                                    sectionName=sectionName, days=days, start=start, end=end, size=size, classMode=mode, data=data)
@professor_bp.route('/professor/create', methods=["POST", "GET"])
def professor():
    inData = True

    if request.method == 'POST':

        # While loops until a random number is generated that is not already in the database
        while(inData):
            # Professors unique class code (Randomly generated between x, and y with z being the amount generated)
            classCode = random.randrange(1, 3000, 1)

            query = databaseConnection.query(Account).filter(
                Account.classCode == classCode)
            # Creates a cursor that checks if classCodes value exists at all
            result = query.first()
            if result == None:
                inData = False

        # Schools Name
        schoolName = request.form.get('schoolName')
        
        # Departments Name
        departmentName = request.form.get('departmentName')
        
        # Class' Id
        className = request.form.get('className')
    
        # Sections Name
        sectionName = request.form.get('sectionName')

        # Mode
        mode = request.form.get('classMode')
        # Start Time
        start = request.form.get('start')

        # End Time
        end = request.form.get('end')

        # Class size
        classSize = str(request.form.get('size'))

        #days
        days = request.form.getlist('day')
        saveDays = ''

        #categories
        categories = request.form.getlist('categories')

        # Combined section and class code
        classAndSection = str(classCode) + '-' + sectionName
        
        # adds data to database
        newClass = Account(schoolName, departmentName,
                           className, classAndSection, start, end, saveDays.join(days), classSize, mode, session['username'])
        databaseConnection.add(newClass)

        try:
            databaseConnection.commit()
        except:
            databaseConnection.rollback()

        i = 1
        for category in categories:
            newCategory = Categories(classAndSection, category, str(i))
            databaseConnection.add(newCategory)
            i += 1
        databaseConnection.commit()
            
        return redirect(url_for('professor_bp.instructor'))

    return render_template('addClass.html', title='professor')
