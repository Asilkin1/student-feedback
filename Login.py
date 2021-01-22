from flask_login import UserMixin


class Student(UserMixin, db.Model):
    pass