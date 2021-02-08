from flask import Blueprint, render_template,request,session
from CreateUserDatabase import * 
from encryption import *

# Define our blueprint with routes
base_bp = Blueprint('base_bp', __name__,
    template_folder='templates',
    static_folder='static')

@base_bp.route('/', methods=["POST", "GET"])
def index():
    # Get classes data for current username
    dashboardData = databaseConnection.query(Account).filter(Account.username == session.get('username'))

    # Filter professor by class codes, feedbacks and username
    hasCodes = databaseConnection.query(Account, Feedback).filter(Account.username == session.get('username'),Account.classCode == Feedback.classCode)

    # Get classes data for current username
    dashboardData = databaseConnection.query(Account).filter(
    Account.username == session.get('username'))

    query = databaseConnection.query(Account, Feedback).filter(Account.username == session.get('username'),Account.classCode == Feedback.classCode)
    result = query.all()
    instructorCount = 0
    teachingStyleCount = 0
    topicCount = 0
    otherCount = 0

    # Loop through the query results
    for feedbacks in result:
        # Decrypt the value where the table is Feedback and the column is elaborate number
        feedbacks = mysql_aes_decrypt(feedbacks.Feedback.elaborateNumber, random_key)

        if feedbacks == "Instructor/Professor":
            instructorCount += 1
        if feedbacks == "Teaching style":
            teachingStyleCount += 1
        if feedbacks == "Topic":
            topicCount += 1
        if feedbacks == "Other":
            otherCount += 1
    
    return render_template('index.html', 
                        title='dashboard', 
                        data=dashboardData,
                        instructor=instructorCount,
                        topic=topicCount,
                        other=otherCount,
                        teaching=teachingStyleCount
                        )
