# Convert UTC string to local time
from datetime import date, datetime
import time

def utc2local(utc):
    '''@utc - time in UTC '''
    epoch = time.mktime(utc.timetuple())
    offset = datetime.fromtimestamp (epoch) - datetime.utcfromtimestamp (epoch)
    return utc + offset

# Get time now in the UTC
UTC = datetime.utcnow()

# Get time in local format
print(utc2local(UTC).strftime("%H:%M"))