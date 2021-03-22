from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey, event
from sqlalchemy import Column, Date, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker
from encryption import *
from  datetime import datetime, date, timezone
from globalTime import utc2local
import os
# db path OS dependant
# Works on windows
db_path = 'sqlite:///' + os.fspath(os.getcwd()) + '/united.db'

print(db_path)
# Set database for specified environment
engine = create_engine(db_path, echo=True,connect_args={"check_same_thread": False})  
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


# Admin table
class Admin(Base):
    __tablename__ = "admin_login"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)

#----------------------------------------------------------------------
    def __init__(self, username, password):
        self.username = username
        self.password = password
        
# Admin creates usernames for professor
class AdminUsernames(Base):
    __tablename__ = "admin_creates_usernames"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    professorName = Column(String)

#----------------------------------------------------------------------
    def __init__(self, username, professorName):
        self.username = username
        self.professorName = professorName
        

        
# Categories table
class Categories(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    classCode = Column(Text, nullable=False)
    category = Column(Text, nullable=False)
    number = Column(Text, nullable=False)

    def __init__(self, classCode,category,number):
        self.classCode = classCode
        self.category = category
        self.number = number


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
    elaborateText = Column(String(140),nullable=False)
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

#---------------------------------------------------------------
# Check date voted
def check_date_voted(ccode):
    """
    @ccode - class code
    """
    # Date
    dateNow = date.today()

     # Time in UTC
    currentTime = datetime.utcnow()
    print('Time now: ', currentTime)
    # Convert to local time
    timeNow = utc2local(currentTime).strftime("%H:%M")
    print('Time now+: ', timeNow)
    currentDay = dateNow.weekday()
        
    currentDay = dateNow.weekday()

    day = ""

    # Monday
    if currentDay == 0:
        day = "M"
    # Tuesday
    if currentDay == 1:
        day = "T"
    # Wednesday
    if currentDay == 2:
        day = "W"
    # Thursday
    if currentDay == 3:
        day = "H"
    # Friday
    if currentDay == 4:
        day = "F"

    query = databaseConnection.query(Account).filter(Account.classCode == ccode)
    result = query.first()
    classStart = result.start
    classEnd = result.end
    classDays = result.days
    inClass = ''
    
    if (timeNow > classStart) and (timeNow < classEnd) and (day in classDays):
        inClass = "Inside"
    else:
        inClass = "Outside"
    
    return inClass

#----------------------------------------------------------------
# Student code voted
def you_voted(ccode,scode):
     return databaseConnection.query(Feedback.studentCode).filter(Feedback.classCode == ccode,Feedback.studentCode == scode).distinct().count()

#----------------------------------------------------------------
# You voted times
def voted_times(ccode,scode):
    return databaseConnection.query(Feedback.studentCode).filter(Feedback.classCode == ccode,Feedback.studentCode == scode).count()

#----------------------------------------------------------------
# Get cass size
def get_class_size(ccode):
    return databaseConnection.query(Account.size).filter(Account.classCode == ccode).one()[0]

#----------------------------------------------------------------
# Not your votes
def not_your_votes(ccode,scode):
    return databaseConnection.query(Feedback.studentCode).filter(Feedback.classCode == ccode,Feedback.studentCode != scode).count()

#----------------------------------------------------------------
# Distinct voters
def get_distinct_voters(ccode, scode):
    return databaseConnection.query(Feedback.studentCode).filter(Feedback.classCode == ccode, Feedback.studentCode != scode).distinct().count()

#----------------------------------------------------------------
# Total voters
def get_total_voters(ccode):
    return databaseConnection.query(Feedback.studentCode).filter(Feedback.classCode == ccode).distinct().count()

#----------------------------------------------------------------
# Count feedback categories
def count_feedback_by_category(category,username):
    query = databaseConnection.query(Account, Feedback).filter(Account.username == username,Account.classCode == Feedback.classCode,Feedback.elaborateNumber == category)
    result = query.all()
    category_count = 0

    # Loop through the query results
    for feedbacks in result:
        # Decrypt the value where the table is Feedback and the column is elaborate number
        feedbacks = mysql_aes_decrypt(feedbacks.Feedback.elaborateNumber, random_key)

        if feedbacks == category:
            category_count += 1

    return category_count
#----------------------------------------------------------------
# Load professor dashboard data
def get_dashboard_data(username):
     return databaseConnection.query(Account).filter(Account.username == username)

# ------------------ Database event handler for update and insert
# Insert and update event for the database
def insert_update(mapper, connection, target):
    tablename = mapper.mapped_table.name

    data = {}
    for name in mapper.c.keys():
        v = getattr(target, name)
        if isinstance(v,datetime):
            v = v.astimezone(timezone.utc)
        data[name] = v

    print('Something changed in the database',tablename, 'Name:', v,' inserted or updated ')

# Decrypt frame
def decrypt_frame(Frame):
    # Go through the columns and data in each column in the Frame
    for (column, columnData) in Frame.iteritems():
        # if the column is emoji
        if column == "emoji":
            # Go through the data in emoji column
            for values in columnData.values:
                # If it is decrypted, continue
                if isinstance(values, int):
                    continue
                else:
                    # If it isn't decrypted, decrypt it
                    decryptValue = mysql_aes_decrypt(values, random_key)
                    # Replace it everywhere in the column
                    Frame[column] = Frame[column].replace(values, int(decryptValue))
        # if the column is elaborateText
        if column == "elaborateText":
            # Go through the data in emoji column
            for values in columnData.values:
                # If it is decrypted, continue
                if isinstance(values, str):
                    continue
                else:
                    # If it isn't decrypted, decrypt it
                    decryptValue = mysql_aes_decrypt(values, random_key)
                    # Replace it everywhere in the column
                    Frame[column] = Frame[column].replace(values, decryptValue)
        # if the column is elaborateNumber
        if column == "elaborateNumber":
            # Go through the data in emoji column
            for values in columnData.values:
                # If it is decrypted, continue
                if isinstance(values, str):
                    continue
                else:
                    # If it isn't decrypted, decrypt it
                    decryptValue = mysql_aes_decrypt(values, random_key)
                    # Replace it everywhere in the column
                    Frame[column] = Frame[column].replace(values, decryptValue)
    return Frame

# create tables
Base.metadata.create_all(engine)
