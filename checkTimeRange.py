# Check if the feedback left within class time range
# Day of a class is passed as a number from 1 to 7
# StartClass/EndClass are the datetime objects
# with the year, month,day,hour,minute specified
# USED 24 hour format for now

import datetime
from datetime import timedelta
import time
from datetime import date

# Start today at 18:00
start = datetime.datetime(2021,2,2,18,00)
# End today at 19:00
end = datetime.datetime(2021,2,2,19,00)


# startClass and endClass are datetime objects built from database values
# day is a number from 1 to 7
def isInClassFeedback(day,startClass,endClass):
    '''Returns True if a feedback received within class time
       timenow >= start | timenow =< end -> true
    '''
    now = datetime.datetime.now()
    print('Class start at: ', startClass)
    print('Class end at: ', endClass)
    print('Feedback left: ', now)
    
    # Check if today have a class
    if isClassToday(day):
        # Check if now > start and  now < end
        #return now >= startClass now <= endClass:
        return timedelta(hours=startClass.hour,minutes=startClass.minute) < timedelta(hours=now.hour,minutes=now.minute) and timedelta(hours=endClass.hour,minutes=endClass.minute) > timedelta(hours=now.hour,minutes=now.minute)
        
    else:
        return False

# Day is a number from the database
def isClassToday(day):
    '''Return True if class is held today
        1 - Monday
        2 - Tuesday
        3 - Wednesday
        4 - Thursday
        5 - Friday
        6 - Saturday
        7 - Sunday 
    '''
    return date.today().isoweekday() == day

print(isInClassFeedback(2,start,end))
