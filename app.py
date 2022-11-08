import string
from flask import Flask, render_template, url_for, redirect, request, jsonify, flash
from flask_cors import CORS
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField, validators, IntegerField
import random
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user



app = Flask(__name__)
app.config["SECRET_KEY"] = "karan"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///exam.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


csrf = CSRFProtect(app)
cors = CORS(app)
login_manager = LoginManager(app)
db = SQLAlchemy(app)
app.app_context().push()


DASHBOARD_LOGIN_ID = "root"
DASHBOARD_LOGIN_PASSWORD = "root"
ACTIVE_SUBJECT = ""
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



# FLASK WTFORMS


class LoginForm(FlaskForm):
    roll_no = IntegerField(label="id", validators=[validators.data_required()])
    password = PasswordField(label="password", validators=[validators.data_required()])
    submit = SubmitField(label="Log In")



# FLASK LOGIN


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# ROUTE'S START HERE


# HOMEPAGE

@app.route("/")
def homepage():
    # db.create_all()
    # user = User(roll_no=00, password="root")
    # db.session.add(user)
    # db.session.commit()

    global ACTIVE_SUBJECT
    dashboard_login_form = LoginForm()
    with open("database.txt", "r") as file:
        exam_data = file.read()
        exam_data = eval(exam_data)
        ACTIVE_SUBJECT = exam_data["active_subject"]
    return render_template("index.html", dashboard_login_form=dashboard_login_form)


# about page

@app.route("/about")
def aboutpage():
    return render_template("about_index.html")


@app.route("/teacher-login")
def teacher():
    dashboard_login_form = LoginForm()

    return render_template("Teachers/teacher-login.html", dashboard_login_form=dashboard_login_form)


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    dashboard_login_form = LoginForm()

    if dashboard_login_form.validate_on_submit():

        admin = User.query.filter_by(id=1).first()

        roll_no = int(dashboard_login_form.roll_no.data)
        password = dashboard_login_form.password.data

        if admin.roll_no != roll_no:
            flash("Id does not exist, please try again")
            return redirect(url_for('teacher'))
        elif admin.password == password:
            # login_user(admin)
            return render_template("Dashboard_for_teachers/dashboard.html")
        else:
            flash("Password is wrong, try again")
            return redirect(url_for('teacher'))
        

    return redirect(url_for('teacher'))


@app.route("/create_test")
def create_test():
    csrf = LoginForm()

    return render_template("Dashboard_for_teachers/create_test.html", csrf=csrf)


@app.route("/form-submit", methods=["POST"])
def form_submit():
    form_data = request.form.to_dict(flat=False)

    subject_name = form_data["test_title"][0]

    if db.session.query(Questions).filter_by(subject_name=subject_name).first() is not None:
        flash("Subject name should be UNIQUE, please try again")
        return redirect(url_for('create_test'))

    questions_count = int((len(form_data)-3)/6)

    for index in range(1, questions_count+1):
        subject_name = form_data["test_title"][0]
        test_time = int(form_data["test_time"][0])
        question = form_data[f"q{index}"][0]
        option_1 = form_data[f"{index}option1"][0]
        option_2 = form_data[f"{index}option2"][0]
        option_3 = form_data[f"{index}option3"][0]
        option_4 = form_data[f"{index}option4"][0]
        answer = form_data[f"{index}answer"][0]

        questions = Questions(subject_name=subject_name, test_time=test_time, question=question, option_1=option_1, option_2=option_2, option_3=option_3, option_4=option_4, answer=answer)
        db.session.add(questions)
        db.session.commit()


    return render_template("Dashboard_for_teachers/dashboard.html")


@app.route("/all-exams")
def all_exam():
    with open("database.txt", "r") as file:
        exam_data = file.read()
        exam_data = eval(exam_data)

    all_exams = {}
    all_exams = {key: 0 for key in exam_data.keys()}
    all_exams["active_subject"] = exam_data["active_subject"]

    return jsonify(all_exams)


# ENDPOINTS FOR DROP DOWN MENU OPTIONS

@app.route("/active-exam/<exam_title>")  # first make a dictionary then make it string then pass to url
def active_exam(exam_title):
    global ACTIVE_SUBJECT

    exam_title = eval(exam_title)  # to convert string to dictionary

    if ACTIVE_SUBJECT == exam_title["subject_name"]:

        if not exam_title["is_active"]:
            ACTIVE_SUBJECT = ""

            with open("database.txt", "r") as file:
                exam_data = file.read()
                exam_data = eval(exam_data)

            exam_data["active_subject"] = ACTIVE_SUBJECT

            with open("database.txt", "w") as file:
                file.write(f"{exam_data}")

            return "Subject Deactivated"
    else:
        ACTIVE_SUBJECT = exam_title["subject_name"]

        with open("database.txt", "r") as file:
            exam_data = file.read()
            exam_data = eval(exam_data)

        exam_data["active_subject"] = ACTIVE_SUBJECT

        with open("database.txt", "w") as file:
            file.write(f"{exam_data}")

        return "Subject Activated"


@app.route("/delete_subject/<subject_name>")
def delete_subject(subject_name):
    with open("database.txt", "r") as file:
        exam_data = file.read()
        exam_data = eval(exam_data)

    del exam_data[subject_name.replace("%20", " ")]

    with open("database.txt", "w") as file:
        file.write(f"{exam_data}")

    return "Subject Deleted"


@app.route("/subject_questions")
def subject_questions():
    with open("database.txt", "r") as file:
        exam_data = file.read()
        exam_data = eval(exam_data)

    return jsonify(exam_data[SHOW_TEST])


@app.route("/show_test/<subject_name>")
def show_test(subject_name):
    global SHOW_TEST
    SHOW_TEST = subject_name
    if subject_name != ACTIVE_SUBJECT:
        csrf = LoginForm()
        print(ACTIVE_SUBJECT)
        return render_template("Dashboard_for_teachers/show-test.html", csrf=csrf)
    else:
        csrf = LoginForm()
        print(ACTIVE_SUBJECT)
        return render_template("Dashboard_for_teachers/show-active-test.html", csrf=csrf)


@app.route("/update_add_subject_questions", methods=["POST"])
def update_add_subject_questions():
    form_raw_data = request.form.to_dict(flat=False)

    with open("database.txt", "r") as file:
        exam_data = file.read()
        exam_data = eval(exam_data)

    exam_data[f"{form_raw_data['test_title'][0]}"] = form_raw_data

    with open("database.txt", "w") as file:
        file.write(f"{exam_data}")

    return render_template("Dashboard_for_teachers/dashboard.html")



# STUDENT SECTION STARTS HERE


# to show only active test to student

@app.route("/students-active-page")
def students_active_page():
    return render_template("Students/student_active_test.html")


# student page

@app.route("/students")
def students():
    return render_template("Students/student_test.html")


# to show test page to student

@app.route("/students_test_page")
def students_test_page():
    csrf = LoginForm()
    return render_template("Students/student_test.html", csrf=csrf)


@app.route("/students_active")
def students_active():
    with open("database.txt", "r") as file:
        exam_data = file.read()
        exam_data = eval(exam_data)

    return jsonify(exam_data[ACTIVE_SUBJECT])


@app.route("/student-reponse", methods=["POST"])
def student_reponse():
    response_data = request.form.to_dict(flat=False)
    print(response_data)

    # try:
    #     with open("student_response.txt", "r") as file:
    #         student_data = file.read()
    #         student_data = eval(student_data)

    #     with open("student_response.txt", "w") as file:
    #         student_data["student"] = response_data
    # except:
    #     with open("student_response.txt", "w") as file:
    #         response_data = {"student": response_data}
    #         file.write(f"{response_data}")

    return "more work needed"


# KRISHNA'S CODE

@app.route("/generate-passwords/<count>")
def generate_passwords(count):
    count = int(count)
    passwords = []
    for i in range(1, count + 1):
        password = ''.join(
            random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(6))
        dict1 = {"number": i, "password": password}
        passwords.append(dict1)

    return jsonify(passwords)




if __name__ == "__main__":
    app.run(debug=True)

