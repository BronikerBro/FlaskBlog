from flask import Flask, render_template, request
from werkzeug.exceptions import abort
import sqlite3

app = Flask(__name__)

def connect_db():
    connect = sqlite3.connect("blogs.db")
    with open('script.sql') as f:
        connect.executescript(f.read())
    connect.row_factory = sqlite3.Row
    return connect

@app.route('/')
@app.route('/<name>')
def index(name="Name"):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM post")
    posts = cursor.fetchall()
    conn.close()
    return render_template("index.html", name=name , posts=posts)

def get_post(id_post):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM post WHERE id = (?)", [id_post])
    post = cursor.fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template("post.html", post=post)

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method =="GET":
        print(request.args.get)
    elif request.method =="POST":
        checked_m = ""
        checked_w = ""
        name, mail, passw, passc, mw =  request.form.get("name"), request.form.get("mail"), request.form.get("inputPassword"), request.form.get("confPassword"), request.form.get("inlineRadioOptions")
        if mw == "man":
            checked_m = "checked"
            checked_w = ""
        elif mw == "woman":
            checked_m = ""
            checked_w = "checked"
        if passw == passc and passw != "" and name != "" and mail != "" and passw != "" and passc != "" and mw  != None:
            return render_template("index.html", name=name)
        elif name == "" or mail == "" or passw == "" or passc == "" or mw  == None:
            return render_template("register.html", i={"error": "! Please check your form", "name":name, "mail":mail, "passw":passw, "checked_w":checked_w, "checked_m": checked_m})

        else:
            print("error")
            return render_template("register.html", i={"error": "! Please check your password", "name":name, "mail":mail, "passw":passw, "checked_w":checked_w, "checked_m": checked_m})
    return render_template("register.html", i={"error": "", "name": "", "mail": "", "passw": "", "mw": ""})

app.run(debug = True)

# cursor = connect.cursor()
# # cursor.execute("DROP TABLE post")
# cursor.execute("INSERT INTO post(title,content) VALUES (?,?)", ["Welcome to FlaskBlog", "Here you can login, create you own blogs, and be a BLOG STAR!"])
# connect.commit()
# connect.close()