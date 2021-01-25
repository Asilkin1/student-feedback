import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from CreateUserDatabase import *

engine = create_engine('sqlite:///tutorial.db', echo=True)

# create a Session
Session = sessionmaker(bind=engine)
session = Session()

user = User("admin","password")
session.add(user)

user = User("blue","green")
session.add(user)

user = User("student","professor")
session.add(user)

user = User("apple","orange")
session.add(user)

# commit the record the database
session.commit()

session.commit()