# All router to professor pages
from flask import Blueprint, stream_with_context,Response, render_template,request, flash, session, redirect, url_for, jsonify
import random
import pandas as pd
from CreateUserDatabase import *

professor_bp = Blueprint('professor_bp', __name__,
    template_folder='templates',
    static_folder='static')


def get_categories(query, decryptFunction):
    '''get categories for each professor'''
    count_categories = {}

    for c in query.all():
        # decrypt each category
        c = decryptFunction
        count_categories[str(c)] += 1
    # Return Category name as a KEY and count as VALUE
    return count_categories

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
        print('-------',i.number)
        # Add the category
        wN[int(i.number)] = 0

    for feedbacks in result:
        feedbacks = mysql_aes_decrypt(feedbacks.Feedback.elaborateNumber, random_key)
        print('feedback loop', feedbacks)
        if int(feedbacks) in wN:
            print('Increment')
            wN[int(feedbacks)] += 1
        
    print('RESULT',wN)

    yield render_template('login.html',
                            title='dashboard',
                            data=dashboardData,
                            categoryData=categoryData,
                            categoryCount=categoryData.count(),
                            present=presentCategories,
                            wN = wN
                            )

def generate_realtime_class(classCode):
   print(classCode)
   Frame = pd.read_sql_query("SELECT * from Feedback",engine)
   Frame = Frame[Frame['classCode'] == classCode]
   Frame = decrypt_frame(Frame)
   
   yield render_template('realtime_class.html',
                            title='reaaltime class',
                            data=Frame)

@professor_bp.route('/professor/<classCode>', methods=['POST','GET'])
def realtime_professor(classCode):
    return Response(stream_with_context(generate_realtime_class(classCode)))

# Ask to login for any routes in professor
@professor_bp.before_request
def before_request():
    if not session.get('logged_in'):
        flash('Please log in to gain access to the website.', 'info')
        print('You have to be logged in')
        return render_template('login.html')

@professor_bp.route('/professor', methods=["POST", "GET"])
def instructor():
    return Response(stream_with_context(generate_feedbacks_by_category()))

@professor_bp.route("/professor/delete/<string:id>/<string:ccode>", methods=['GET', 'POST'])
def deleteClass(id, ccode):
    databaseConnection.query(Account).filter(Account.entryId == id).delete()
    databaseConnection.commit()
    databaseConnection.query(Feedback).filter(Feedback.classCode == ccode).delete()
    databaseConnection.commit()
    databaseConnection.query(Categories).filter(Categories.classCode == ccode).delete()
    databaseConnection.commit()

    flash('Class Deleted', 'success')
    return redirect(url_for('professor_bp.instructor'))

@professor_bp.route("/professor/edit/<string:id>", methods=['GET', 'POST'])
def editClass(id):
    
    query = databaseConnection.query(Account).filter(
                Account.entryId == id)
    result = query.first()

    # Populate article form fields
    schoolName = result.schoolName
    departmentName = result.departmentName
    className = result.className
    print('class name :', className)
    start = result.start 
    end = result.end
    days = result.days
    parsingClassCode = result.classCode.split("-")
    mode = result.mode
    size = result.size

    # Parse for section
    sectionName = parsingClassCode[1]

    if request.method == 'POST':
        # Query feedback table for class code
        queryFeedBack = databaseConnection.query(Feedback).filter(Feedback.classCode == result.classCode)
        resultFeedback = queryFeedBack.first()

        # Parse for section in Feedback table
        if resultFeedback != None:
            parsingClassCode = resultFeedback.classCode.split("-")
            sectionFeedBack = parsingClassCode[1]
        
        schoolName = request.form['schoolName']
        departmentName = request.form['departmentName']
        className = request.form['className']
        sectionName = request.form['sectionName']
        
        days = request.form.getlist('days')
        saveDays = ''

        start = request.form['start']
        end = request.form['end']
        mode = request.form['mode']
        size = request.form['size']
        
        databaseConnection.commit()
        
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
        databaseConnection.commit()

        flash('Class Updated', 'success')

        # Go back to the dashboard
        return redirect(url_for('professor_bp.instructor'))

    return render_template('editClass.html', entryId=id, schoolName=schoolName, departmentName=departmentName, className=className,
                                                    sectionName=sectionName, days=days, start=start, end=end, size=size, classMode=mode)
@professor_bp.route('/professor/create', methods=["POST", "GET"])
def professor():
    inData = True

    if request.method == 'POST':

        # While loops until a random number is generated that is not already in the database
        while(inData):
            # Professors unique class code (Randomly generated between x, and y with z being the amount generated)
            classCode = random.randrange(1, 3000, 1)
            print(classCode)

            query = databaseConnection.query(Account).filter(
                Account.classCode == classCode)
            # Creates a cursor that checks if classCodes value exists at all
            result = query.first()
            if result == None:
                inData = False

        # Schools Name
        schoolName = request.form.get('schoolName')
        print(schoolName)
        
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
        print('Days picked: ', days)

        #categories
        categories = request.form.getlist('categories')
        print("what is happening now ", categories)

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
