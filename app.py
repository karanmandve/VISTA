from flask import Flask, render_template, url_for, redirect,request
from flask_cors import CORS
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField, validators


app = Flask(__name__)
app.config["SECRET_KEY"] = "karan"

csrf = CSRFProtect(app)
cors = CORS(app)


DASHBOARD_LOGIN_ID = "root"
DASHBOARD_LOGIN_PASSWORD = "root"



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
    form_data = request.form.to_dict(flat=False)
    print(form_data)
        
    return render_template("Dashboard_for_teachers/dashboard.html")



if __name__ == "__main__":
    app.run(debug=True)

