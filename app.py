from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)


# HOMEPAGE
@app.route("/")
def homepage():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("Dashboard_for_teachers/dashboard.html")


@app.route("/create_test")
def create_test():
    return render_template("Dashboard_for_teachers/create_test.html")



if __name__ == "__main__":
    app.run(debug=True)

