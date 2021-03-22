from flask import Flask,app
from flask_session.__init__ import Session as flaskGlobalSession
from cache import cache
import logging

# ------------BLUEPRINTS-------------------
from analytics.analytics import analytics_bp
from professor.professor import professor_bp
from feedback.feedback import student_bp
from auth.auth import auth_bp
from base.base import base_bp
from admin.admin import admin_bp

app = Flask(__name__)
app.register_blueprint(analytics_bp)
app.register_blueprint(professor_bp)
app.register_blueprint(student_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(base_bp)
app.register_blueprint(admin_bp)

# Set logging to a file
logging.basicConfig(filename='feedback.log', level=logging.DEBUG,format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

if __name__ == '__main__':
    # This secret if for local development environment
    app.secret_key = 'super secret key'
    # app configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['ENV'] = 'dev'    
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/student-feedback/student-feedback/united.db'
    app.config['DEBUG'] = True
    weirdsession = flaskGlobalSession()
    weirdsession.init_app(app)
    cache.init_app(app)
    app.run(threaded=True)