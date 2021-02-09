from flask import Blueprint, render_template,request,session
from CreateUserDatabase import *

# Define our blueprint with routes
base_bp = Blueprint('base_bp', __name__,
    template_folder='templates',
    static_folder='static')

@base_bp.route('/', methods=["POST", "GET"])
def index():
    return render_template('index.html')
