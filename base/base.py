from flask import Blueprint, render_template,request,session
from CreateUserDatabase import * 

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

    feedbackInstructor = databaseConnection.query(Account, Feedback).filter(Account.username == session.get('username'),Account.classCode == Feedback.classCode,Feedback.elaborateNumber == 'Instructor/Professor')
    feedbackTeachingStyle = databaseConnection.query(Account, Feedback).filter(Account.username == session.get('username'),Account.classCode == Feedback.classCode,Feedback.elaborateNumber == 'Teaching style')
    feedbackTopic = databaseConnection.query(Account, Feedback).filter(Account.username == session.get('username'),Account.classCode == Feedback.classCode,Feedback.elaborateNumber == 'Topic')
    feedbackOther = databaseConnection.query(Account, Feedback).filter(Account.username == session.get('username'),Account.classCode == Feedback.classCode,Feedback.elaborateNumber == 'Other')

    return render_template('index.html', 
                        title='dashboard', 
                        data=dashboardData,
                        instructor=feedbackInstructor.count(),
                        topic=feedbackTopic.count(),
                        other=feedbackOther.count(),
                        teaching=feedbackTeachingStyle.count()
                        )