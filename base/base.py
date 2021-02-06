from flask import Blueprint, render_template,request,session
from CreateUserDatabase import * 

# Define our blueprint with routes
base_bp = Blueprint('base_bp', __name__,
    template_folder='templates',
    static_folder='static')

@base_bp.route('/', methods=["POST", "GET"])
def index():
    if session.get('logged_in') and session.get('studentCode'):
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
        
        # Get some data about class votes
        # Don't forget to get each row for current student code only once
        yourCodeVotes = databaseConnection.query(Feedback.studentCode).filter(Feedback.classCode == session.get('classCode'),Feedback.studentCode == session.get('studentCode')).distinct()
        yourVotedTimes = databaseConnection.query(Feedback.studentCode).filter(Feedback.classCode == session.get('classCode'),Feedback.studentCode == session.get('studentCode'))            
        
        distinctVoters = databaseConnection.query(Feedback.studentCode).filter(Feedback.classCode == session.get('classCode'),Feedback.studentCode != session.get('studentCode')).distinct()
        classSize = databaseConnection.query(Account.size).filter(Account.classCode == session.get('classCode'))


        return render_template('index.html', 
                            title='dashboard', 
                            data=dashboardData,
                            instructor=feedbackInstructor.count(),
                            topic=feedbackTopic.count(),
                            other=feedbackOther.count(),
                            teaching=feedbackTeachingStyle.count(),
                            you=yourCodeVotes.count(), notYou = distinctVoters.count(), size=classSize.one()[0], voted = yourVotedTimes.count())

    else:
        return render_template('index.html')