from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

engine = create_engine('sqlite:///united.db', echo=True)
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


#Feedback database
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

    def __init__(self, date, time, classCode,studentCode,emoji,elaborateNumber, elaborateText):
        self.date = date
        self.time = time
        self.classCode = classCode
        self.studentCode = studentCode
        self.emoji = emoji
        self.elaborateNumber = elaborateNumber
        self.elaborateText = elaborateText


# create tables
Base.metadata.create_all(engine)