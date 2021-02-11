# All global imports should reside in each individual blueprint
# The lines below should be moved to some other parts of the app
from flask import Flask, render_template, request, redirect, url_for, session, app, abort, flash, make_response, Response, render_template_string
from flask_session.__init__ import Session as flaskGlobalSession

# Add flask sockets for some dynamic data insertion
from flask_socketio import SocketIO, send, emit

# ------------BLUEPRINTS-------------------
from analytics.analytics import analytics_bp
from professor.professor import professor_bp
from feedback.feedback import student_bp
from auth.auth import auth_bp
from base.base import base_bp

app = Flask(__name__)
app.register_blueprint(analytics_bp)
app.register_blueprint(professor_bp)
app.register_blueprint(student_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(base_bp)
# Initialize SocketIO in flask app
socketio = SocketIO(app)

# Let web client to know the event name
@socketio.event('message')
def message_received(message):
    print(message)
    # Send something we can show in the webbrowser
    send('Message from flask')

# Only call it on professor dashboard
@socketio.event('dashboard')
def message_received(dashboard):
    # Send to the webbrowser
    emit('data for professor dashboard: ',dashboard)

@socketio.on('connect')
def test_connect():
    send('Conneted message send to the client')

if __name__ == '__main__':
    # This secret if for local development environment
    app.secret_key = 'super secret key'
    # app configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['ENV'] = 'dev'    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/student-feedback/student-feedback/united.db'
    app.config['DEBUG'] = True
    weirdsession = flaskGlobalSession()
    weirdsession.init_app(app)
    # Run sockets
    socketio.run(app)
