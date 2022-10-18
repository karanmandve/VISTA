from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)

# HOMEPAGE
@app.route("/")
def homepage():
    return render_template("index.html")\

@app.route("/dashboard")
def dashboard():
    return render_template("./dashboard_for_teachers/dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)
