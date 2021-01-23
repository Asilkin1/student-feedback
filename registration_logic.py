import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from CreateUserDatabase import *

# Add new user to the database
def register(username,password):
    engine = create_engine('sqlite:///tutorial.db', echo=True)
    
    # create a Session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    user = User(username,password)
    session.add(user)

    session.commit()