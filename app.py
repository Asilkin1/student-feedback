# All global imports should reside in each individual blueprint
# The lines below should be moved to some other parts of the app
from gimports import *
from sqlalchemybusiness import *

from flask import Flask


# ------------BLUEPRINTS-------------------
#import blueprint for analytics
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

# Encryption Key
#random_key = os.urandom(16)
random_key = b"J3FTV1PL1jDFeMh01I9r+A=="
random_key = b64encode(random_key).decode('utf-8')


# Stream data into any template ------------------------------------------------------------------
def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)  # this is some sort of delay I assume
    return rv

# ------------------ Database event handler for update and insert
# Inset and update event for the database
def insert_update(mapper, connection, target):
    tablename = mapper.mapped_table.name

    data = {}
    for name in mapper.c.keys():
        v = getattr(target, name)
        if isinstance(v,datetime):
            v = v.astimezone(timezone.utc)
        data[name] = v

    print('Something changed in the database',tablename, 'Name:', v,' inserted or updated ')


def delete_event_db_handler(mapper, connection,target):
    '''Do something when entry is removed'''
    print('Something removed from the database')
    tablename = mapper.mapped_table.name
    index = get_es_index(tablename)
    doc_type = 'doc'
    id = target.id
    res = es.delete(index=index, doc_type=doc, id=id)
    print('delete index', res)


# Set event listener for Account table
event.listen(Account, 'after_update',insert_update,propagate=True)
event.listen(Account, 'after_delete',delete_event_db_handler,propagate=True)


@app.route('/realtime')
def render_realtime():
    return Response(stream_template('realtime.html', data=databaseConnection.query(Account).all()))
    

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    weirdsession = flaskGlobalSession()
    weirdsession.init_app(app)
    app.run(debug=True)
