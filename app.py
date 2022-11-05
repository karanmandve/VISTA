import string
from flask import Flask, render_template, url_for, redirect, request, jsonify, Response
from flask_cors import CORS
from exam import Exam
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField, validators
import random


app = Flask(__name__)
app.config["SECRET_KEY"] = "karan"

csrf = CSRFProtect(app)
cors = CORS(app)

# sql= MySQLPool() #for database
exam= Exam()


DASHBOARD_LOGIN_ID = "root"
DASHBOARD_LOGIN_PASSWORD = "root"
ACTIVE_SUBJECT = ""
SHOW_TEST=""



class LoginForm(FlaskForm):
    id = StringField(label="id", validators=[validators.data_required()])
    password = PasswordField(label="password", validators=[validators.data_required()])
    submit = SubmitField(label="Log In")


# HOMEPAGE
@app.route("/")
def homepage():
    global ACTIVE_SUBJECT
    dashboard_login_form = LoginForm()
    with open("database.txt", "r") as file:
                exam_data = file.read()
                exam_data = eval(exam_data)
                ACTIVE_SUBJECT=exam_data["active_subject"]
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
        if dashboard_login_form.id.data == DASHBOARD_LOGIN_ID and dashboard_login_form.password.data == DASHBOARD_LOGIN_PASSWORD:
            return render_template("Dashboard_for_teachers/dashboard.html")

    return redirect(url_for('teacher'))
    

@app.route("/create_test")
def create_test():
    csrf = LoginForm()
   
    return render_template("Dashboard_for_teachers/create_test.html", csrf=csrf)


@app.route("/form-submit", methods=["POST"])
def form_submit():
    form_raw_data = request.form.to_dict(flat=False)
    form_data = {form_raw_data['test_title'][0] : form_raw_data}
    
    try:
        with open("database.txt", "r") as file:
            exam_data = file.read()
            exam_data = eval(exam_data)
            
        exam_data[f"{form_raw_data['test_title'][0]}"] = form_raw_data

        with open("database.txt", "w") as file:
            file.write(f"{exam_data}")
    except:
        with open("database.txt", "w") as file:
            file.write(f"{form_data}")

    return render_template("Dashboard_for_teachers/dashboard.html")


@app.route("/all-exams")
def all_exam():
    with open("database.txt", "r") as file:
        exam_data = file.read()
        exam_data = eval(exam_data)

    all_exams = {}
    all_exams = {key:0 for key in exam_data.keys()}
    all_exams["active_subject"] = exam_data["active_subject"]

    return jsonify(all_exams)


# ENDPOINTS FOR DROP DOWN MENU OPTIONS

@app.route("/active-exam/<exam_title>") #first make a dictionary then make it string then pass to url
def active_exam(exam_title):
    global ACTIVE_SUBJECT
    
    exam_title = eval(exam_title)# to convert string to dictionary

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

    del exam_data[subject_name.replace("%20"," ")]

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
    SHOW_TEST=subject_name
    if subject_name != ACTIVE_SUBJECT:
        csrf = LoginForm()
        print(ACTIVE_SUBJECT)
        return render_template("Dashboard_for_teachers/show-test.html",csrf=csrf)
    else :
        csrf = LoginForm()
        print(ACTIVE_SUBJECT)
        return render_template("Dashboard_for_teachers/show-active-test.html",csrf=csrf)


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
    return render_template("Students/student_test.html",csrf=csrf)


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

    try:
        with open("student_response.txt", "r") as file:
            student_data = file.read()
            student_data = eval(student_data)


        with open("student_response.txt", "w") as file:
            student_data["student"] = response_data
    except:
        with open("student_response.txt", "w") as file:
            response_data = {"student":response_data}
            file.write(f"{response_data}")

    return "more work needed"


# KRISHNA'S CODE

@app.route("/generate-passwords/<count>")
def generate_passwords(count):
    count=int(count)
    global STUDENT_PASSWORDS
    passwords = []
    for i in range(1, count+1):
        password = ''.join(
            random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(6))
        dict1 = {"number": i, "password": password}
        passwords.append(dict1)

    return jsonify(passwords)


# # send student password
# @app.route("/show-passwords/")
# def show_passwords():

#     return jsonify(STUDENT_PASSWORDS)




if __name__ == "__main__":
    app.run(debug=True)

