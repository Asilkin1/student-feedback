# Flask barebones
from flask import Flask, render_template, request, redirect, url_for
import time
import sqlite3 as sql

app = Flask(__name__)

@app.route('/', methods=["POST", "GET"])
def index():
    return render_template('submit.html', title='submit')

@app.route('/student', methods=["POST", "GET"])
def student():
    Date = f'{time.asctime().split(' ')[1]} {time.asctime().split(' ')[2]} {time.asctime().split(' ')[4]}'
    Time = time.asctime().split(' ')[3]
    ClassID = 
    StudentID = 
    EmojiNum = 
    FbNum = EmojiNum-3
    ElabCat = 
    ElabTxt = 
    
    #Create and Save the data table so it can be added to
    conn = sql.connect('Datatable.db') #Make a sqlite database
    c = conn.cursor() #Connect to database
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='tweets' ''') #See if the table exists already
    if c.fetchone()[0]!=1: #If the table does not exist, create it
        c.execute('''CREATE TABLE StudentTable (Date, Time, Class ID, Student ID, Emoji #, Feedback #, Elaborate Category, Elaborate Text)''')
    c.execute("INSERT INTO tweets (Date, Time, Class ID, Student ID, Emoji #, Feedback #, Elaborate #, Elaborate Text) VALUES (?,?,?,?,?,?,?,?)",(Date,Time,ClassID,StudentID,EmojiNum,FbNum,ElabCat,ElabTxt)) #Insert the information into the table
    conn.commit() #Commit/save changes
    conn.close() #Close the data table
    
    return render_template('studentPortal.html', title='student')

@app.route('/instructor', methods=["POST", "GET"])
def instructor():
    return render_template('instructorPortal.html', title='instructor')


if __name__ == '__main__':
    app.run(debug=True)
