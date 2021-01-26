# Flask barebones
from flask import Flask, render_template, request, redirect, url_for
from models import create_post, get_posts, delete_posts
from datetime import date, datetime
import time
import random
from wtforms import Form, validators, TextField
import os

from Crypto.Cipher import AES
from base64 import b64encode
import Padding
import binascii
import hashlib

from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'studentfeedback'

mysql = MySQL(app)

classCode = ""
studentCode = ""
random_key = os.urandom(16)
random_key = b64encode(random_key).decode('utf-8')

@app.route('/', methods=["POST", "GET"])
def index():
    return render_template('submit.html', title='submit')
    
@app.route("/student/login", methods=["GET", "POST"])
def studentLogin():
    # if request.method == 'GET':
    #     # classCode = request.form['classCode']
    #     # studentCode = request.form['studentCode']

    #     # cur = mysql.connection.cursor()

    #     # cur.execute("INSERT IGNORE into users (classCode, studentCode) values (%s, %s)", (classCode, studentCode))

    #     # mysql.connection.commit()
    #     # cur.close()
    #     # print(classCode)
    #     return render_template('student.html', title='student')

    return render_template('studentLogin.html', title='login')

@app.route('/student/', methods=["POST", "GET"])
def student():
    classCode = request.args.get('classCode')
    studentCode = request.args.get('studentCode')

    if request.method == 'GET':
        #Delete existing data in database (can change this later)
        pass

    if request.method == 'POST':
        cur = mysql.connection.cursor()

        cur.execute("INSERT into users (classCode, studentCode) values (%s, %s)", (classCode, studentCode))

        mysql.connection.commit()
        cur.close()

        #Date
        dateNow = date.today()

        #Time
        currentTime = datetime.now()
        timeNow = currentTime.strftime("%I:%M %p")

        #Emoji number
        emoji = request.form.get('emoji')
        emoji = mysql_aes_encrypt(emoji, random_key)

        #class code
        #classCode = request.form.get('classCode')

        #Student code
        #studentCode = request.form.get('studentCode')

        #Elaborate number
        elaborateNumber = request.form.get('elaborateNumber')
        elaborateNumber = mysql_aes_encrypt(elaborateNumber, random_key)


        #Elaborate text
        elaborateText = request.form.get('elaborateText')
        elaborateText = mysql_aes_encrypt(elaborateText, random_key)

        #create data in database
        create_post(dateNow, timeNow, classCode, studentCode, emoji, elaborateNumber, elaborateText)
        #elaborateText = mysql_aes_decrypt(elaborateText, random_key)
        #create_post(dateNow, timeNow, classCode, studentCode, emoji, elaborateNumber, elaborateText)

    return render_template('student.html', title='student')

@app.route('/professor', methods=["POST", "GET"])
def instructor():
    return render_template('professor.html', title='instructor')

def mysql_aes_encrypt(val, key):
    val = Padding.appendPadding(val,blocksize=Padding.AES_blocksize,mode='Random')
    #val=binascii.hexlify(bytearray(val.encode()))
    
    def mysql_aes_key(key):
        return hashlib.sha256(key.encode()).digest()
        # final_key = bytearray(16)
        # for i, c in enumerate(key):
        #     final_key[i%16] ^= ord(key[i])
        # return bytes(final_key)

    def mysql_aes_val(val, key):
        encrypted = AES.new(key, AES.MODE_ECB)
        print(encrypted)
        return(encrypted.encrypt(val))
        # pad_value = 16 - (len(val) % 16)
        # print(chr(pad_value))
        # return '%s%s' % (val, chr(pad_value)*pad_value)

    k = mysql_aes_key(key)
    v = mysql_aes_val(val.encode(), k)
    v = binascii.hexlify(bytearray(v))
    

    # cipher = AES.new(k, AES.MODE_ECB)

    return v

def mysql_aes_decrypt(val,key):
    val = binascii.unhexlify(bytearray(val))

    def mysql_aes_key(key):
        return hashlib.sha256(key.encode()).digest()

    def mysql_aes_val(val, key):
        decrypted = AES.new(key, AES.MODE_ECB)
        return(decrypted.decrypt(val))

    k = mysql_aes_key(key)
    v = mysql_aes_val(val, k)

    v = Padding.removePadding(v.decode(),mode='Random')

    return v

if __name__ == '__main__':
    app.run(debug=True)

