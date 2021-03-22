from flask import Blueprint, render_template,request,session, redirect, url_for,flash, session
from datetime import timedelta
from CreateUserDatabase import *
import random
random.seed()
import csv

# Define our blueprint with routes
admin_bp = Blueprint('admin_bp', __name__,
    template_folder='templates',
    static_folder='static')

# Ask to login for any routes in admin
@admin_bp.before_request
def before_request():
    session.permanent = True
    admin_bp.permanent_session_lifetime = timedelta(minutes=95)
    if not session.get('logged_in'):
        return render_template('admin_index.html')
    
    
@admin_bp.route('/admin', methods=['POST','GET'])
def adminindex():
    '''Show datatable with professor name and username'''
     # Get classes data for current username
    query = databaseConnection.query(AdminUsernames.username, Account.classCode).filter(AdminUsernames.username == Account.username)
    result = query.all()
    return  render_template('admin_index.html',
                            data=result)
    
# Add classes from csv file
@admin_bp.route("/admin/bulkadd", methods=["GET", "POST"])
def hello():
    if request.method == 'POST':
    
        # Create variable for uploaded file
        f = request.files['fileupload']  

        #store the file contents as a string
        fstring = csv.reader(f)
        
        #create list of dictionaries keyed by header row
        print('CSV uploaded', fstring)
        
        # Insert rows from csv into the database
        

        #do something list of dictionaries
    return redirect(url_for("admin_bp.adminindex"))


@admin_bp.route('/admin/createprofessor', methods=['POST','GET'])
def createprofessor():
    return render_template('create_professor.html')

@admin_bp.route("/admin/delete/<id>/<ccode>", methods=['GET', 'POST'])
def deleteClass(id,ccode):
    databaseConnection.query(Account).filter(Account.entryId == int(id)).delete()
    databaseConnection.commit()
    databaseConnection.query(Feedback).filter(Feedback.classCode == ccode).delete()
    databaseConnection.commit()
    databaseConnection.query(Categories).filter(Categories.classCode == ccode).delete()
    databaseConnection.commit()

    flash('Class Deleted', 'success')
    return redirect(url_for('admin_bp.adminindex'))

def deleteCategories(ccode):
    databaseConnection.query(Categories).filter(Categories.classCode == ccode).delete()
    databaseConnection.commit()

@admin_bp.route("/admin/edit/<string:id>", methods=['GET', 'POST'])
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

# Create a class based on the professor username
@admin_bp.route('/admin/create', methods=["POST", "GET"])
def createclass():
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
                           className, classAndSection, start, end, saveDays.join(days), classSize, mode, "")
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
            
        return redirect(url_for('admin_bp.adminindex'))

    return render_template('addClass.html', title='professor')

