import string
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
app.config["SESSION_COOKIE_SECURE"]=True
# app.config["SERVER_NAME"]="vista.azurewebsites.net"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///exam.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


csrf = CSRFProtect(app)
csrf.init_app(app)
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



# FLASK WTFORMS


class LoginForm(FlaskForm):
    roll_no = IntegerField(label="id", validators=[validators.data_required()])
    password = PasswordField(label="password", validators=[validators.data_required()])
    submit = SubmitField(label="Log In")



# FLASK LOGIN


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# ADMIN LOGIN DECORATOR FUNCTION


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            current_user.password
        except:
            abort(403)
            
        admin = User.query.filter_by(id=1).first()

        if current_user.password == admin.password:
            return f(*args, **kwargs)
        else:
            return abort(403)

    return decorated_function



# ROUTE'S START HERE


# HOMEPAGE

@app.route("/")
def homepage():
    # db.create_all()
    # user = User(roll_no=00, password="root")
    # db.session.add(user)
    # db.session.commit()

    # subject = AllSubject(subject_name="None")
    # db.session.add(subject)
    # db.session.commit()

    dashboard_login_form = LoginForm()

    return render_template("index.html", dashboard_login_form=dashboard_login_form)


# about page

@app.route("/about")
def aboutpage():
    return render_template("about_index.html")


@app.route("/teacher-login", methods=["GET", "POST"])
def teacher():
    dashboard_login_form = LoginForm()

    if dashboard_login_form.validate_on_submit():

        admin = User.query.filter_by(id=1).first()

        roll_no = int(dashboard_login_form.roll_no.data)
        password = dashboard_login_form.password.data

        if admin.roll_no != roll_no:
            flash("Id does not exist, please try again")
            return render_template("Teachers/teacher-login.html", dashboard_login_form=dashboard_login_form)
            # return redirect(url_for('teacher'))
        elif admin.password == password:
            login_user(admin, remember=True)
            return render_template("Dashboard_for_teachers/dashboard.html")
        else:
            flash("Password is wrong, try again")
            return render_template("Teachers/teacher-login.html", dashboard_login_form=dashboard_login_form)
            # return redirect(url_for('teacher'))

    return render_template("Teachers/teacher-login.html", dashboard_login_form=dashboard_login_form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))


@app.route("/dashboard", methods=["GET", "POST"])
@admin_only
def dashboard():
    # dashboard_login_form = LoginForm()

    # if dashboard_login_form.validate_on_submit():

    #     admin = User.query.filter_by(id=1).first()

    #     roll_no = int(dashboard_login_form.roll_no.data)
    #     password = dashboard_login_form.password.data

    #     if admin.roll_no != roll_no:
    #         flash("Id does not exist, please try again")
    #         return redirect(url_for('teacher'))
    #     elif admin.password == password:
    #         login_user(admin, remember=True)
    #         return render_template("Dashboard_for_teachers/dashboard.html")
    #     else:
    #         flash("Password is wrong, try again")
    #         return redirect(url_for('teacher'))
        

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

    subject_name = form_data["test_title"][0]

    if db.session.query(Questions).filter_by(subject_name=subject_name).first() is not None:
        flash("Subject name should be UNIQUE, please try again")
        return redirect(url_for('create_test'))

    subject = AllSubject(subject_name=subject_name)
    db.session.add(subject)
    db.session.commit()

    questions_count = int((len(form_data)-3)/6)

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


    return render_template("Dashboard_for_teachers/dashboard.html")


@app.route("/all-exams")
@login_required
def all_exam():

    all_subjects = db.session.query(AllSubject.subject_name).all()
    all_subjects = [subject[0] for subject in all_subjects]
    return jsonify(all_subjects)


# ENDPOINTS FOR DROP DOWN MENU OPTIONS

@app.route("/active-exam/<subject_name>")  # first make a dictionary then make it string then pass to url
@admin_only
def active_exam(subject_name):

    subject_name = eval(subject_name)  # to convert string to dictionary

    active_subject = AllSubject.query.filter_by(id=1).first()
    print(active_subject.subject_name)

    if subject_name["subject_name"] != "None":
        active_subject.subject_name = subject_name["subject_name"]
        db.session.commit()

        return "Subject Activated"
    else:
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
#         return render_template("Dashboard_for_teachers/show-test.html", csrf=csrf)
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
    return render_template("Students/student_active_test.html")


# to show test page to student

@app.route("/students_test_page")
def students_test_page():
    csrf = LoginForm()
    return render_template("Students/student_test.html", csrf=csrf)


# active exam all questions

@app.route("/active-exam-questions")
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
@admin_only
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

