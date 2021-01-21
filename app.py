# Flask barebones
from flask import Flask, render_template, request, redirect, url_for
from models import create_post, get_posts, delete_posts
from datetime import date, datetime
import time

app = Flask(__name__)

@app.route('/', methods=["POST", "GET"])
def index():
    return render_template('index.html', title='submit')

@app.route('/analytics', methods=["POST","GET"])
def analytics():
    return render_template('analytics.html',title='stats')

@app.route('/signup', methods=["POST","GET"])
def signup():
    return render_template('signup.html',title='signup')

@app.route('/student', methods=["POST", "GET"])
def student():
    if request.method == 'GET':
        #Delete existing data in database (can change this later)
        #delete_posts()
        pass

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
def instructor():
    return render_template('professor.html', title='instructor')

if __name__ == '__main__':
    app.run(debug=True)