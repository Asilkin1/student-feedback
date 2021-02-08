from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey, event
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker

from  datetime import datetime 

# Set database for specified environment
engine = create_engine('sqlite:///united.db', echo=True,connect_args={"check_same_thread": False})  
Session = sessionmaker(bind=engine)
databaseConnection = Session()

Base = declarative_base()

# User database(professor)
class User(Base):
    __tablename__ = "professor_login"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)

#----------------------------------------------------------------------
    def __init__(self, username, password):
        self.username = username
        self.password = password


#Feedback database(feedback)
class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True)
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    classCode = Column(String, nullable=False)
    studentCode = Column(String, nullable=False)
    emoji = Column(Integer, nullable=False)
    elaborateNumber = Column(Integer,nullable=False)
    elaborateText = Column(String,nullable=False)
    inClass = Column(String, nullable=False)

    def __init__(self, date, time, classCode,studentCode,emoji,elaborateNumber, elaborateText, inClass):
        self.date = date
        self.time = time
        self.classCode = classCode
        self.studentCode = studentCode
        self.emoji = emoji
        self.elaborateNumber = elaborateNumber
        self.elaborateText = elaborateText
        self.inClass = inClass

# Table for professor account
class Account(Base):

    __tablename__ = 'account'

    entryId = Column(Integer, autoincrement=True, primary_key=True)
    schoolName = Column(String, nullable=False)
    departmentName = Column(String, nullable=False)
    className = Column(String, nullable=False)
    classCode = Column(String, nullable=False)
    start = Column(String, nullable=False)
    end = Column(String, nullable=False)
    days = Column(String, nullable=False)
    size = Column(String, nullable=False)
    mode = Column(String, nullable=False)
    # Account is associated with a professor username
    username = Column(String, ForeignKey('professor_login.username'))

    def __init__(self, schoolName, departmentName, className, classCode, start, end, days, size, mode, username):
        self.schoolName = schoolName
        self.departmentName = departmentName
        self.className = className
        self.classCode = classCode
        self.start = start
        self.end = end
        self.days = days
        self.size = size
        self.mode = mode
        self.username = username

class StudentCodes(Base):
    __tablename__ = 'studentcodes'

    code = Column(String, primary_key=True, nullable=False)
    def __init__(self, code):
        self.code = code

#----------------------------------------------------------------
# Count feedback categories
def count_feedback_by_category(category,username):
    feedbackInstructor = databaseConnection.query(Account, Feedback).filter(Account.username == username,Account.classCode == Feedback.classCode,Feedback.elaborateNumber == category)
    return feedbackInstructor.count()
#----------------------------------------------------------------
# Load professor dashboard data
def get_dashboard_data(username):
     return databaseConnection.query(Account).filter(Account.username == username)

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


# create tables
Base.metadata.create_all(engine)
