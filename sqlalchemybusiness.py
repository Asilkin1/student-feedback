from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Database engine
engine = create_engine('sqlite:///united.db', echo=True,
                       connect_args={"check_same_thread": False})  # Connect to Users database
# Establish connection to the database

Session = sessionmaker(bind=engine)
# Provides connection to the database for any operations
databaseConnection = Session()