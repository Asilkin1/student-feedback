from flask import Blueprint, render_template,request,session
from CreateUserDatabase import *

# Define our blueprint with routes
base_bp = Blueprint('base_bp', __name__,
    template_folder='templates',
    static_folder='static')

@base_bp.route('/', methods=["POST", "GET"])
def index():
    # Might use the line below for another graph with class codes ready to be checked
    #hasCodes = databaseConnection.query(Account, Feedback).filter(Account.username == session.get('username'),Account.classCode == Feedback.classCode)

    return render_template('index.html', 
                        title='dashboard', 
                        data=get_dashboard_data(session.get('username')),
                        instructor=count_feedback_by_category('Instructor/Professor',session.get('username')),
                        topic=count_feedback_by_category('Topic',session.get('username')),
                        other=count_feedback_by_category('Other',session.get('username')),
                        teaching=count_feedback_by_category('Teaching style',session.get('username'))
                        )
