from flask import Blueprint, render_template,request,session, redirect, url_for,flash, session
from datetime import timedelta
from CreateUserDatabase import *

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
    return render_template('admin_index.html')

