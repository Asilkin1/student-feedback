import mysql.connector as mysql

def connection():
    conn = mysql.connect(host = "localhost",
                        user = "root",
                        passwd = "apples123",
                        db = "studentfeedback")
    c = conn.cursor()

    return c, conn