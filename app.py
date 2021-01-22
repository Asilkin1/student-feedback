# Flask barebones
from flask import Flask, render_template, request, redirect, url_for
from models import create_post, get_posts, delete_posts
from datetime import date, datetime
from flask_login import LoginManager, login_required
from flask_user import roles_required, current_user, UserManager,UserMixin
import time

app = Flask(__name__)
# login_manager = LoginManager(app)
# login_manager.login_view = 'login'

# @login_manager.user_loader
@app.route('/', methods=["POST", "GET"])
def index():
    return render_template('index.html', title='submit')

# @login_manager.unauthorized_handler
@app.route('/signup',methods=['GET'])
def unauthorized():
      if request.path == '/student':
          return render_template('student_sign_up.html', title='instructor')
      else:
          return render_template('professor_sign_up.html')

@app.route('/analytics', methods=["POST","GET"])
# @login_required
# @roles_required('Professor')
def analytics():
    return render_template('analytics.html',title='stats')

@app.route('/notenoughdata',methods=["POST","GET"])
def notenoughdata():
    return render_template('notEnoughData.html',title='not enough data')

@app.route('/classerror',methods=["POST","GET"])
def classerror():
    return render_template('classError.html',title='class does not exist')

@app.route('/signup', methods=["POST","GET"])
def signup():
    return render_template('signup.html',title='signup')

@app.route("/regisration",methods=["POST"])
def registration():
    email = request.form.get('email')
    password = request.form.get('password')
    repassword = request.form.get('repassword')

    if password == repassword:
        return redirect(url_for('index'))

# New student signup
@app.route('/newstudent', methods=['GET'])
def newstudent():
    #class code
    classCode = request.form.get('classCode')
    
    #student code
    studentCode = request.form.get('studentCode')

    return render_template('student_sign_up.html', scode=12003)


    

@app.route('/student', methods=["POST", "GET"])
# @login_required
def student():
    if request.method == 'GET':
        #Delete existing data in database (can change this later)
        #delete_posts()
        ccode = request.args.get('classCode')
        return render_template('student.html', classcode=ccode)
        

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

@app.route('/professor', methods=["POST", "GET"])
# @login_required
def instructor():
    return render_template('professor.html', title='instructor')

if __name__ == '__main__':
    app.run(debug=True)