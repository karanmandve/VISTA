
from flask import Flask, render_template, request
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)

# HOMEPAGE
@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/teacher")
def teacher():
    return render_template("Teachers/login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("Dashboard_for_teachers/dashboard.html")
    
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
