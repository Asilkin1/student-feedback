from cache import cache
from CreateUserDatabase import *
import time

def get_id(classCode):
    '''Get feedback ID'''
    query = databaseConnection.query(Feedback.id).filter(Feedback.classCode == classCode).order_by(Feedback.id.desc())
    result = query.first()
    return result

# Get all feedbacks for the past 5 seconds  
@cache.cached(timeout=10, key_prefix='last_10_emoji_values')
def get_emoji_cached(classCode):
    '''@classCode - current class
       :returns a list of emojis values e.g. [5,4,2,1,4,1,2,3,4,5]
    '''
    emoji = 0
    time = 0
    id = 0
    accumulate = []
    timeAccumulate = []
    idAccumulate = []
    # Get feedbacks by classCode
    try:
        query = databaseConnection.query(Feedback).filter(Feedback.classCode == classCode).order_by(Feedback.id.desc())
        # get last 10 feedbacks
        result = query.limit(10).all()

        # get classCodes
        ccode = databaseConnection.query(Feedback.id).filter(Feedback.classCode == classCode).order_by(Feedback.id.desc())
        ccode = query.limit(10).all()
        if result and ccode:
            for i in result:
                print('Result: ',i)
                if i.id not in ccode:
                    print('Code: ', i.id)
                    emoji = mysql_aes_decrypt(i.emoji,random_key)
                    accumulate.append(int(emoji))
                    timeAccumulate.append(i.time)
                    idAccumulate.append(i.id)
    # Cannot read from the database then do something
    except:
        emoji = 0
        time = 0
        id = 0
    print('Cached function',accumulate)
    accumulate.reverse()
    timeAccumulate.reverse()
    idAccumulate.reverse()
    print(timeAccumulate)
    return accumulate, timeAccumulate, idAccumulate

def get_emoji(classCode):
    '''Get emoji'''
    emoji = 0
    # Get something from the database
    try:
        query = databaseConnection.query(Feedback).filter(Feedback.classCode == classCode).order_by(Feedback.id.desc())
        result = query.first()
        if result:
            emoji = mysql_aes_decrypt(result.emoji,random_key)
    # Cannot read from the database then do something
    except:
        emoji = 0
    return emoji

@cache.cached(timeout=1, key_prefix='last_student_voted')
def get_student_code(classCode):
    '''Get student code'''
    # Return 0 if something goes wrong
    studentCode = 0
    # Get something from the database
    try:
        query = databaseConnection.query(Feedback.studentCode).filter(Feedback.classCode == classCode).order_by(Feedback.id.desc())
        result = query.first()
        if result:
            studentCode = result[0]
    # Cannot read from the database then do something
    except:
        studentCode = 0
    print('Student Code: ', str(studentCode))
    return studentCode

def get_time(classCode):
    '''Get time'''
    query = databaseConnection.query(Feedback.time).filter(Feedback.classCode == classCode).order_by(Feedback.id.desc())
    result = query.first()
    print('Time now: ', result)
    return result

def get_student_feedback_count(classCode):
    '''Get student feedback count'''
    student_code = databaseConnection.query(Feedback.studentCode).filter(Feedback.classCode == classCode).distinct()
    result = student_code.all()
    # How many feedbacks left by this student
    return result.count()

def get_class_categories_voted(classCode):
    categories_voted = databaseConnection.query(Feedback.elaborateNumber).filter(Feedback.classCode == classCode).distinct()
    result = categories_voted.all()
    categories = []
    if result:
        for feedbacks in result:
            feedbacks = mysql_aes_decrypt(feedbacks.elaborateNumber, random_key)
            num_to_word = databaseConnection.query(Categories.category).filter(Categories.number == feedbacks,Categories.classCode == classCode)
            res = num_to_word.all()
            categories.append(res)
    

    if len(categories) > 0:
        return categories
    else:
        return 0


def sum(data):
    '''Sum all the values in the list'''
    total = 0
    if len(data)>0:
        for i in data:
            # Should be an integer
            total += int(i)
        return round(total / len(data))
    else:
        return 0
    
def print_log_thread(message):
    '''Print any statements in this thread'''
    print('[Background thread] ',message)
    time.sleep(1)