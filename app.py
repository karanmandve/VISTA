from flask import Flask, render_template, url_for, redirect, request, jsonify
from flask_cors import CORS
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField, validators


app = Flask(__name__)
app.config["SECRET_KEY"] = "karan"

csrf = CSRFProtect(app)
cors = CORS(app)


DASHBOARD_LOGIN_ID = "root"
DASHBOARD_LOGIN_PASSWORD = "root"
ACTIVE_SUBJECT = ""



class LoginForm(FlaskForm):
    id = StringField(label="id", validators=[validators.data_required()])
    password = PasswordField(label="password", validators=[validators.data_required()])
    submit = SubmitField(label="Log In")


# HOMEPAGE
@app.route("/")
def homepage():
    return render_template("index.html")


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
    all_exam["active_subject"] = exam_data["active_exam"]

    return jsonify(all_exams)


@app.route("/active-exam/<exam_title>")
def active_exam(exam_title):
    global ACTIVE_SUBJECT

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

    del exam_data[subject_name]

    with open("database.txt", "w") as file:
        file.write(f"{exam_data}")

    return "Subject Deleted"


@app.route("/subject_questions/<subject_name>")
def subject_questions(subject_name):
    with open("database.txt", "r") as file:
        exam_data = file.read()
        exam_data = eval(exam_data)

    return jsonify(exam_data[subject_name])


@app.route("/update_add_subject_questions", methods=["POST"])
def update_add_subject_questions():
    form_raw_data = request.form.to_dict(flat=False)
    
    with open("database.txt", "r") as file:
        exam_data = file.read()
        exam_data = eval(exam_data)

    exam_data[f"{form_raw_data['test_title'][0]}"] = form_raw_data

    with open("database.txt", "w") as file:
        file.write(f"{exam_data}")

    return redirect(url_for('dashboard'))
    


if __name__ == "__main__":
    app.run(debug=True)

