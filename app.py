from flask import Flask, render_template, url_for, redirect
from flask_cors import CORS
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField, validators


app = Flask(__name__)
app.config["SECRET_KEY"] = "karan"

csrf = CSRFProtect(app)
cors = CORS(app)


DASHBOARD_LOGIN_ID = "root"
DASHBOARD_LOGIN_PASSOWRD = "root"



class LoginForm(FlaskForm):
    id = StringField(label="id", validators=[validators.data_required()])
    password = PasswordField(label="password", validators=[validators.data_required()])
    submit = SubmitField(label="Log In")


# HOMEPAGE
@app.route("/")
def homepage():
    return render_template("index.html")


@app.route("/teacher-login", methods=["GET"])
def teacher():
    dashboard_login_form = LoginForm()

    return render_template("Teachers/teacher-login.html", dashboard_login_form=dashboard_login_form)


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    dashboard_login_form = LoginForm()

    if dashboard_login_form.validate_on_submit():
        if dashboard_login_form.id.data == "root" and dashboard_login_form.password.data == "root":
            return render_template("Dashboard_for_teachers/dashboard.html")

    return redirect(url_for('teacher'))
    

@app.route("/create_test")
def create_test():
    return render_template("Dashboard_for_teachers/create_test.html")

@app.route("/form_submit", methods=["POST"])
def form_submit():
    # print(request.form)
    print(request.form["test_title"]) #test name
    print(request.form["test_desc"]) #test description
    no=(len(request.form)-2)//6
    for x in range(1,no+1):
        print(request.form["q"+str(x)]) #question
        print(request.form[str(x)+"option1"]) #option
        print(request.form[str(x)+"option2"]) #option
        print(request.form[str(x)+"option3"]) #option
        print(request.form[str(x)+"option4"]) #option
        print('anser is : '+ request.form[str(x)+"answer"]) #answer
        
    return render_template("Dashboard_for_teachers/dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)

