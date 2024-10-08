import string
import bcrypt
from flask import Flask, render_template, url_for, redirect, request, jsonify, flash, abort
from flask_cors import CORS
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField, validators, IntegerField
import random
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from functools import wraps



app = Flask(__name__)
app.config["SECRET_KEY"] = "karan"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///exam.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["WTF_CSRF_ENABLED"] = False



csrf = CSRFProtect(app)
cors = CORS(app)
login_manager = LoginManager(app)
db = SQLAlchemy(app)
app.app_context().push()


# ACTIVE_SUBJECT = "None" NOT NEEDED NOW    
SHOW_TEST = ""



# SQLALCHEMY TABLES


class Questions(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(250), nullable=False)
    test_time = db.Column(db.Integer, nullable=False)
    question = db.Column(db.Text, nullable=False)
    option_1 = db.Column(db.String(250), nullable=False)
    option_2 = db.Column(db.String(250), nullable=False)
    option_3 = db.Column(db.String(250), nullable=False)
    option_4 = db.Column(db.String(250), nullable=False)
    answer = db.Column(db.String(250), nullable=False)


class StudentResponse(db.Model):
    __tablename__ = "student_response"
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.Integer, nullable=False)
    question = db.Column(db.Text, nullable=False)
    option_1 = db.Column(db.String(250), nullable=False)
    option_2 = db.Column(db.String(250), nullable=False)
    option_3 = db.Column(db.String(250), nullable=False)
    option_4 = db.Column(db.String(250), nullable=False)
    answer = db.Column(db.String(250), nullable=False)


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.Integer, unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)


class AllSubject(db.Model):
    __tablename__ = "all_subjects"
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(250), nullable=False)

class AllScore(db.Model):
    __tablename__ = "all_scores"
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)



# FLASK WTFORMS


class LoginForm(FlaskForm):
    roll_no = IntegerField(label="id", validators=[validators.data_required()])
    password = PasswordField(label="password", validators=[validators.data_required()])
    submit = SubmitField(label="Log In")


class UpdatePasswordForm(FlaskForm):
    current = StringField('current', validators=[validators.data_required()])
    # Minimum eight characters, at least one uppercase letter, one lowercase letter, one number and one special character:
    # ^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$
    new = StringField('new', validators=[validators.data_required(), validators.regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')])
    # new = StringField('new', validators=[validators.data_required()])



# FLASK LOGIN


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# ADMIN LOGIN DECORATOR FUNCTION

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function

# def admin_only(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         try:
#             current_user.password
#         except:
#             return abort(403)
            
#         admin = User.query.filter_by(id=1).first()

#         if current_user.password == admin.password:
#             return f(*args, **kwargs)
#         else:
#             return abort(403)

#     return decorated_function



# ROUTE'S START HERE


# HOMEPAGE

@app.route("/", methods=["GET", "POST"])
def homepage():
    db.create_all()
    # user = User(roll_no=99, password="root")
    # db.session.add(user)
    # db.session.commit()

    # subject = AllSubject(subject_name="None")
    # db.session.add(subject)
    # db.session.commit()

    student_login_form = LoginForm()

    if student_login_form.validate_on_submit():
        student_roll_no = student_login_form.roll_no.data
        student_password = student_login_form.password.data

        user = User.query.filter_by(password=student_password).first()

        if user is None:
            flash("Password is wrong, try again")
            return render_template("index.html", student_login_form=student_login_form)

        user.roll_no = student_roll_no
        db.session.commit()

        login_user(user)

        return redirect(url_for("students_active_page"))

    return render_template("index.html", student_login_form=student_login_form)


# about page

@app.route("/about")
def aboutpage():
    return render_template("about.html")


@app.route("/teacher-login", methods=["GET", "POST"])
def teacher():
    dashboard_login_form = LoginForm()

    if dashboard_login_form.validate_on_submit():

        admin = User.query.filter_by(id=1).first()

        roll_no = int(dashboard_login_form.roll_no.data)
        password = bytes(dashboard_login_form.password.data, "UTF-8")
        admin_password_hash = bytes(admin.password, "UTF-8")

        if admin.roll_no != roll_no:
            flash("Id does not exist, please try again")
            return render_template("Teachers/teacher-login.html", dashboard_login_form=dashboard_login_form, teacher_page=True)
        elif bcrypt.checkpw(password, admin_password_hash):
            login_user(admin)
            return render_template("Dashboard_for_teachers/dashboard.html")
        else:
            flash("Password is wrong, try again")
            return render_template("Teachers/teacher-login.html", dashboard_login_form=dashboard_login_form, teacher_page=True)

    return render_template("Teachers/teacher-login.html", dashboard_login_form=dashboard_login_form, teacher_page=True)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))


@app.route("/dashboard")
@admin_only
def dashboard():
    return render_template("Dashboard_for_teachers/dashboard.html")


@app.route("/create_test")
@admin_only
def create_test():
    csrf = LoginForm()

    return render_template("Dashboard_for_teachers/create_test.html", csrf=csrf)


@app.route("/form-submit", methods=["POST"])
@admin_only
def form_submit():
    form_data = request.form.to_dict(flat=False)
    print(form_data)

    subject_name = form_data["test_title"][0]

    if db.session.query(Questions).filter_by(subject_name=subject_name).first() is not None:
        flash("Subject name should be UNIQUE, please try again")
        return redirect(url_for('create_test'))

    subject = AllSubject(subject_name=subject_name)
    db.session.add(subject)
    db.session.commit()

    questions_count = int((len(form_data)-2)/6)

    for count in range(1, questions_count+1):
        subject_name = form_data["test_title"][0]
        test_time = int(form_data["test_time"][0])
        question = form_data[f"q{count}"][0]
        option_1 = form_data[f"{count}option1"][0]
        option_2 = form_data[f"{count}option2"][0]
        option_3 = form_data[f"{count}option3"][0]
        option_4 = form_data[f"{count}option4"][0]
        answer = form_data[f"{count}answer"][0]

        questions = Questions(subject_name=subject_name, test_time=test_time, question=question, option_1=option_1, option_2=option_2, option_3=option_3, option_4=option_4, answer=answer)
        db.session.add(questions)
        db.session.commit()


    # return render_template("Dashboard_for_teachers/dashboard.html")
    return redirect(url_for('dashboard'))

@app.route("/all-exams")
@login_required
def all_exam():

    all_subjects = db.session.query(AllSubject.subject_name).all()
    all_subjects = [subject[0] for subject in all_subjects]
    
    return jsonify(all_subjects)


# ENDPOINTS FOR DROP DOWN MENU OPTIONS

# endpoint for response page
@app.route("/response_page")
@admin_only
def response():
    return render_template("Dashboard_for_teachers/response.html")

@app.route("/all-students-responses")
# @admin_only
def all_students_responses():
    all_students_responses = db.session.query(StudentResponse).all()
    
    all_students_responses = [response.__dict__ for response in all_students_responses]
    
    for response in all_students_responses:
        del response["_sa_instance_state"]

    return jsonify(all_students_responses)

@app.route("/active-exam/<subject_name>")  # first make a dictionary then make it string then pass to url
@admin_only
def active_exam(subject_name):

    subject_name = eval(subject_name)  # to convert string to dictionary

    active_subject = AllSubject.query.filter_by(id=1).first()

    if subject_name["subject_name"] != "None":
        active_subject.subject_name = subject_name["subject_name"]
        db.session.commit()

        return "Subject Activated"
    else:
        db.session.query(StudentResponse).delete()
        db.session.query(AllScore).delete()
        db.session.query(User).filter(User.id != 1).delete()

        active_subject.subject_name = "None"
        db.session.commit()

        return "Subject Deactivated"


@app.route("/delete_subject/<subject_name>")
@admin_only
def delete_subject(subject_name):

        active_subject = AllSubject.query.filter_by(id=1).first()

        if active_subject.subject_name == subject_name:
            return "Subject is active, please deactivate it first"

        # delete all rows in Questions table with subject_name
        Questions.query.filter_by(subject_name=subject_name).delete()
        db.session.commit()

        # delete subject_name from AllSubject table
        AllSubject.query.filter_by(subject_name=subject_name).delete()
        db.session.commit()

        return "Subject Deleted"


@app.route("/subject_questions")
def subject_questions():
    active_subject = AllSubject.query.filter_by(subject_name=SHOW_TEST).first()

    all_questions = Questions.query.filter_by(subject_name=active_subject.subject_name).all()
    all_questions = [question.__dict__ for question in all_questions]
    
    for question in all_questions:
        question.pop("_sa_instance_state")
    
    return jsonify(all_questions)


@app.route("/show_test/<subject_name>")
def show_test(subject_name):
    global SHOW_TEST
    csrf = LoginForm()
    SHOW_TEST=subject_name

    if  AllSubject.query.filter_by(id=1).first().subject_name == SHOW_TEST:
        return render_template("Dashboard_for_teachers/show-active-test.html", csrf=csrf)
    else:
        return render_template("Dashboard_for_teachers/show-test.html", csrf=csrf)


@app.route("/update_add_subject_questions", methods=["POST"])
def update_add_subject_questions():
    return "bye"

# @app.route("/subject_questions")
# def subject_questions():
#     with open("database.txt", "r") as file:
#         exam_data = file.read()
#         exam_data = eval(exam_data)

#     return jsonify(exam_data[SHOW_TEST])


# @app.route("/show_test/<subject_name>")
# def show_test(subject_name):
#     global SHOW_TEST
#     SHOW_TEST = subject_name
#     if subject_name != ACTIVE_SUBJECT:
#         csrf = LoginForm()
#         print(ACTIVE_SUBJECT)
        # return render_template("Dashboard_for_teachers/show-test.html", csrf=csrf)
#     else:
#         csrf = LoginForm()
#         print(ACTIVE_SUBJECT)
#         return render_template("Dashboard_for_teachers/show-active-test.html", csrf=csrf)


# @app.route("/update_add_subject_questions", methods=["POST"])
# def update_add_subject_questions():
#     form_raw_data = request.form.to_dict(flat=False)

#     with open("database.txt", "r") as file:
#         exam_data = file.read()
#         exam_data = eval(exam_data)

#     exam_data[f"{form_raw_data['test_title'][0]}"] = form_raw_data

#     with open("database.txt", "w") as file:
#         file.write(f"{exam_data}")

#     return render_template("Dashboard_for_teachers/dashboard.html")



# STUDENT SECTION STARTS HERE



# to show only active test to student

@app.route("/students-active-page")
@login_required
def students_active_page():
    current_user
    return render_template("Students/student_active_test.html",current_user=current_user)


# to show test page to student

@app.route("/students_test_page")
@login_required
def students_test_page():
    csrf = LoginForm()
    return render_template("Students/student_test.html", csrf=csrf)


# active exam all questions

@app.route("/active-exam-questions")
@login_required
def active_exam_questions():
    # get all question from Questions table with respect to subject_name
    active_subject = AllSubject.query.filter_by(id=1).first()
    all_questions = Questions.query.filter_by(subject_name=active_subject.subject_name).all()

    #convert all_question into dictionary
    all_questions = [question.__dict__ for question in all_questions]

    # remove _sa_instance_state from all_questions
    for question in all_questions:
        question.pop("_sa_instance_state")

    return jsonify(all_questions)


# # student page

# @app.route("/students")
# def students():
#     return render_template("Students/student_test.html")


@app.route("/student-response", methods=["POST"])
@login_required
def student_response():
    response_data = request.form.to_dict(flat=False)

    counter = int(len(response_data)/6)

    for count in range(1, counter+1):
        roll_no = current_user.roll_no
        question = response_data[f"q{count}"][0]
        option_1 = response_data[f"{count}option1"][0]
        option_2 = response_data[f"{count}option2"][0]
        option_3 = response_data[f"{count}option3"][0]
        option_4 = response_data[f"{count}option4"][0]
        answer = response_data[f"{count}answer"][0]

        student_response = StudentResponse(roll_no=roll_no, question=question, option_1=option_1, option_2=option_2, option_3=option_3, option_4=option_4, answer=answer)
        db.session.add(student_response)
        db.session.commit()

    active_subject = AllSubject.query.filter_by(id=1).first()
    questions_data = Questions.query.filter_by(subject_name=active_subject.subject_name).all()

    question_answer_dict = {data.question:data.answer for data in questions_data}

    score = 0

    for count in range(1, counter+1):
        question = response_data[f"q{count}"][0]
        answer = response_data[f"{count}answer"][0]

        if answer == question_answer_dict[question]:
            score += 1

        data=[score,counter]

    score_table = AllScore(roll_no=current_user.roll_no, score=score, total_questions=counter)
    db.session.add(score_table)
    db.session.commit()

    logout_user()

    return render_template("Students/student_result.html")


@app.route("/student_result")
def student_result():
    all_results = AllScore.query.all()

    # convert all_results into dictionary
    all_results = [result.__dict__ for result in all_results]

    # remove _sa_instance_state from all_results

    for result in all_results:
        result.pop("_sa_instance_state")

    return jsonify(all_results)


# KRISHNA'S CODE


@app.route("/generate-passwords/<count>")
@admin_only
def generate_passwords(count):
    count = int(count)
    passwords = []
    all_user = []

    for i in range(1, count + 1):
        password = ''.join(
            random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(6))
        dict1 = {"number": i, "password": password}
        passwords.append(dict1)

        user = User(roll_no=i, password=password)
        all_user.append(user)


    db.session.bulk_save_objects(all_user)
    db.session.commit()

    return jsonify(passwords)


@app.route("/change-password", methods=['POST', 'GET'])
def change_password_page():
    form = UpdatePasswordForm() 
    message = ""
    if form.validate_on_submit():
        admin = User.query.filter_by(id=1).first()
        current_password_hash = bytes(admin.password, "UTF-8")
        form_password = bytes(form.current.data, "UTF-8")
        if bcrypt.checkpw(form_password, current_password_hash):
            new_password = bytes(form.new.data, "UTF-8")
            salt = bcrypt.gensalt()
            new_password_hashed = bcrypt.hashpw(new_password, salt)
            admin.password = str(new_password_hashed, "UTF-8")
            db.session.commit()
            return "Password updated successfully"
        else:
            return "Incorrect Password"

    return render_template("Dashboard_for_teachers/change_password.html", form=form)


@app.route("/print")
def printChange():
    admin = User.query.filter_by(id=1).first()
    admin.password="$2b$12$.Hp/mxMv.AVKOkCtqfSb5.NcuPQM79Q66wSD6ciSkPW5TykywYMuW"
    db.session.commit()
    dict1 = {
        "roll no": admin.roll_no,
        "password": admin.password,
    }
    return jsonify(dict1)




if __name__ == "__main__":
    app.run(debug=True)

