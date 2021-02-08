# All global imports should reside in each individual blueprint
# The lines below should be moved to some other parts of the app
from flask import Flask, render_template, request, redirect, url_for, session, app, abort, flash, make_response, Response, render_template_string
from flask_session.__init__ import Session as flaskGlobalSession

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



# Stream data into any template ------------------------------------------------------------------
def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)  # this is some sort of delay I assume
    return rv


@app.route('/realtime')
def render_realtime():
    return Response(stream_template('realtime.html', data=databaseConnection.query(Account).all()))

if __name__ == '__main__':
    # This secret if for local development environment
    app.secret_key = 'super secret key'
    # app configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['ENV'] = 'dev'    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/student-feedback/student-feedback/united.db'

    weirdsession = flaskGlobalSession()
    weirdsession.init_app(app)
    app.run(debug=True)
