from flask import Blueprint, render_template,request,session, redirect, url_for
from CreateUserDatabase import *

# Define our blueprint with routes
base_bp = Blueprint('base_bp', __name__,
    template_folder='templates',
    static_folder='static')

@base_bp.route('/', methods=["POST", "GET"])
def index():
    # log out when returned to the website
    session.clear()
    if session.get('username'):
        return redirect(url_for('professor_bp.instructor'))
    elif session.get('studentCode'):
        return redirect(url_for('student_bp.student'))
    else:
        return render_template('index.html')
