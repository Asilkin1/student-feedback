# All imports done
from flask import Blueprint, render_template,request,session, flash 
from CreateUserDatabase import * 

auth_bp = Blueprint('auth_bp', __name__,
    template_folder='templates',
    static_folder='static')


@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
    # Sumbitting login form
    if request.method == 'POST':
        send_username = request.form.get('username')
        send_password = request.form.get('password')

        # If the password and username is provided
        if send_password and send_username:
            # Compare professor credentials with the records in the databse
            query = databaseConnection.query(User).filter(User.username.in_(
                [send_username]), User.password.in_([send_password]))
            # Store result of the query
            result = query.first()

            # Match found in the database
            if result:
                # Here we can login
                session['logged_in'] = True
                session['username'] = send_username
                flash('You have successfully logged in.', 'success')

                # Category for ... ?
                category = request.args.get('category')

                # Filter professor by class codes, feedbacks and username
                hasCodes = databaseConnection.query(Account, Feedback).filter(Account.username == session.get('username'),Account.classCode == Feedback.classCode)

                # Get classes data for current username
                dashboardData = databaseConnection.query(Account).filter(
                    Account.username == session.get('username'))

                feedbackInstructor = databaseConnection.query(Account, Feedback).filter(Account.username == session.get('username'),Account.classCode == Feedback.classCode,Feedback.elaborateNumber == 'Instructor/Professor')
                feedbackTeachingStyle = databaseConnection.query(Account, Feedback).filter(Account.username == session.get('username'),Account.classCode == Feedback.classCode,Feedback.elaborateNumber == 'Teaching style')
                feedbackTopic = databaseConnection.query(Account, Feedback).filter(Account.username == session.get('username'),Account.classCode == Feedback.classCode,Feedback.elaborateNumber == 'Topic')
                feedbackOther = databaseConnection.query(Account, Feedback).filter(Account.username == session.get('username'),Account.classCode == Feedback.classCode,Feedback.elaborateNumber == 'Other')

                return render_template('index.html',
                                       title='dashboard',
                                       data=dashboardData,
                                       instructor=feedbackInstructor.count(),
                                       topic=feedbackTopic.count(),
                                       other=feedbackOther.count(),
                                       teaching=feedbackTeachingStyle.count()
                                       )

            else:
                flash('Wrong password or username', 'error')

                # Get classes data for current username
                dashboardData = databaseConnection.query(Account).filter(
                    Account.username == session.get('username'))

                # Filter professor by class codes, feedbacks and username
                hasCodes = databaseConnection.query(Account, Feedback).filter(Account.username == session.get('username'),Account.classCode == Feedback.classCode)

                # Get classes data for current username
                dashboardData = databaseConnection.query(Account).filter(
                    Account.username == session.get('username'))

                feedbackInstructor = databaseConnection.query(Account, Feedback).filter(Account.username == session.get('username'),Account.classCode == Feedback.classCode,Feedback.elaborateNumber == 'Instructor/Professor')
                feedbackTeachingStyle = databaseConnection.query(Account, Feedback).filter(Account.username == session.get('username'),Account.classCode == Feedback.classCode,Feedback.elaborateNumber == 'Teaching style')
                feedbackTopic = databaseConnection.query(Account, Feedback).filter(Account.username == session.get('username'),Account.classCode == Feedback.classCode,Feedback.elaborateNumber == 'Topic')
                feedbackOther = databaseConnection.query(Account, Feedback).filter(Account.username == session.get('username'),Account.classCode == Feedback.classCode,Feedback.elaborateNumber == 'Other')

                return render_template('login.html', 
                                        title='dashboard', 
                                        data=dashboardData,
                                        instructor=feedbackInstructor.count(),
                                        topic=feedbackTopic.count(),
                                        other=feedbackOther.count(),
                                        teaching=feedbackTeachingStyle.count())

        else:
            flash('Check your username and password', 'error')
            return render_template('login.html')
    elif request.method == 'GET':
        # Get classes data for current username
        # Filter professor by class codes, feedbacks and username
        hasCodes = databaseConnection.query(Account, Feedback).filter(Account.username == session.get('username'),Account.classCode == Feedback.classCode)

        # Get classes data for current username
        dashboardData = databaseConnection.query(Account).filter(Account.username == session.get('username'))

        feedbackInstructor = databaseConnection.query(Account, Feedback).filter(Account.username == session.get('username'),Account.classCode == Feedback.classCode,Feedback.elaborateNumber == 'Instructor/Professor')
        feedbackTeachingStyle = databaseConnection.query(Account, Feedback).filter(Account.username == session.get('username'),Account.classCode == Feedback.classCode,Feedback.elaborateNumber == 'Teaching style')
        feedbackTopic = databaseConnection.query(Account, Feedback).filter(Account.username == session.get('username'),Account.classCode == Feedback.classCode,Feedback.elaborateNumber == 'Topic')
        feedbackOther = databaseConnection.query(Account, Feedback).filter(Account.username == session.get('username'),Account.classCode == Feedback.classCode,Feedback.elaborateNumber == 'Other')

        return render_template('/login.html', 
                                title='dashboard', 
                                data=dashboardData,
                                instructor=feedbackInstructor.count(),
                                topic=feedbackTopic.count(),
                                other=feedbackOther.count(),
                                teaching=feedbackTeachingStyle.count())

    else:
        return render_template('login.html')

@auth_bp.route('/signup', methods=["POST", "GET"])
def signup():
    return render_template('signup.html', title='signup')

@auth_bp.route('/logout')
def logout():
    # User is logged out
    session['logged_in'] = False
    # User is removed from the session
    session.pop('username', None)
    # Remove student codes and class code
    session.pop('classCode', None)
    session.pop('studentCode', None)

    # Feedback message
    flash('You have successfully logged out', 'success')
    return render_template('index.html')