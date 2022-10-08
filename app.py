from flask import Flask, render_template

app = Flask(__name__)

# HOMEPAGE
@app.route("/")
def homepage():
    return render_template("index.html")
