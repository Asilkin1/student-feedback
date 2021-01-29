import sqlite3 as sql 
from os import path

ROOT = path.dirname(path.relpath((__file__)))

def create_post(date, time, classCode, studentCode, emoji, elaborateNumber, elaborateText):
    con = sql.connect(path.join(ROOT, 'united.db'))
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS feedback (date, time, classCode, studentCode, emoji, elaborateNumber, elaborateText)''')
    cur.execute('insert into feedback (date, time, classCode, studentCode, emoji, elaborateNumber, elaborateText) values(?, ?, ?, ?, ?, ?, ?)', (date, time, classCode, studentCode, emoji, elaborateNumber, elaborateText))
    con.commit()

def get_posts():
    con = sql.connect(path.join(ROOT, 'database.db'))
    cur = con.cursor()
    cur.execute('select * from feedback')
    posts = cur.fetchall()
    return posts

def delete_posts():
    con = sql.connect(path.join(ROOT, 'database.db'))
    cur = con.cursor()
    cur.execute('delete from feedback')
    con.commit()
    
def create_class(professorName, schoolName, departmentName, classId, sectionName, classCode):
    con = sql.connect(path.join(ROOT, 'prof.db'))
    cur = con.cursor()
    cur.execute('insert into account (professorName, schoolName, departmentName, classId, sectionName, classCode) values(?, ?, ?, ?, ?, ?)', (professorName, schoolName, departmentName, classId, sectionName, classCode))
    con.commit()
    con.close()

def get_class():
    con = sql.connect(path.join(ROOT, 'prof.db'))
    cur = con.cursor()
    cur.execute('select * from account')
    posts = cur.fetchall()
    return posts

def delete_class():
    con = sql.connect(path.join(ROOT, 'prof.db'))
    cur = con.cursor()
    cur.execute('delete from account')
    con.commit()