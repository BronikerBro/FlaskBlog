from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.exceptions import abort
from flask_mail import Message, Mail
import sqlite3
from random import choice
from string import digits
import hashlib

app = Flask(__name__)

app.secret_key = b'nyeNyalUBITlUBY'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'flask.blog.for.users'
app.config['MAIL_PASSWORD'] = 'fswzxjeiisyokvcx'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


def connect_db():
    connect = sqlite3.connect("blogs.db")
    # cursor = connect.cursor()
    # cursor.execute("INSERT INTO post(title, content) VALUES(?, ?)", ("HELLO", "Test post"))
    # connect.commit()
    with open('script.sql') as f:
        connect.executescript(f.read())
    connect.row_factory = sqlite3.Row
    return connect


@app.context_processor
def lib_versions():
    if session.get("name") != None:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM post WHERE author = ?", [session.get("name")])
        posts = cursor.fetchall()
        conn.close()
        return dict (
            u_posts_am=len(posts),
            u_posts = posts,
            user_name = session.get("name"),
            user_gmail = session.get("mail"),
            user_mw = session.get("mw")
        )
    else:
        return dict(
            u_posts_am = 0,
            u_posts="",
            user_name="Name",
            user_gmail = "",
            user_mw = ""
        )


def connect_us():
    connect = sqlite3.connect("users.db")
    # cursor = connect.cursor()
    # cursor.execute("INSERT INTO post(title, content) VALUES(?, ?)", ("HELLO", "Test post"))
    # connect.commit()
    with open('users.sql') as f:
        connect.executescript(f.read())
    # connect.row_factory = sqlite3.Row
    return connect

def check_user(name, gmail, code):
    print(name, gmail)
    mail = Mail(app)
    msg = Message((f"Hello, {name}"), sender="Flask Blog",recipients=[gmail])
    msg.body = "This is the code to complete registration"
    msg.html = f"""<b style = "font-size:30px;">This is the to complete registration</b>
    <br>
    <h1 style = "align-items: center;background-color: green; border-radius: .5rem;font-weight: 600;color:white;font-size:50px;">{code}</h1>"""
    mail.connect()
    mail.send(msg)
# {{url_for('index') }}
@app.route('/')
@app.route('/<name>')
def index(name="Name"):
    if session.get("name") != None:
        name = session.get("name")
    conn = connect_db()
    cursor = conn.cursor()
    # cursor.execute("DELETE FROM post WHERE id > 1")
    # conn.commit()
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


@app.route('/check_your_mail',methods=['GET', 'POST'])
def check_your_mail():
    error = ""
    need = [r_name, r_mail, r_passw, r_mw]
    print(need)
    if request.method == "POST":

        gcode = request.form.get("code")
        print(a_code, gcode)
        if gcode == a_code:
            print("ok")
            session["name"] = need[0]
            session["mail"] = need[1]
            session["passw"] = need[2]
            session["mw"] = need[3]
            hash = hashlib.sha256()
            need[2] = bytes(need[2], encoding='utf8')

            need[2] = hash.update(need[2])
            need[2] = hash.hexdigest()
            conn = connect_us()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user(name, gmail, password, mw) VALUES(?, ?, ?, ?)", (need[0], need[1], need[2], need[3]))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

        else:
            error = "!Your code isn't right"

    check_user(need[0], need[1], a_code)
    return render_template("checkyourmail.html", error = error)

@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post['author'] == session.get("name"):
        return render_template("post.html", post=post, href = url_for('edit', post_id = post['id']))
    else:
        return render_template("post.html", post=post, href="")

@app.route("/<int:post_id>/edit/delete_blog_ok")
def delete_blog_ok(post_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM post WHERE id = ?",[post_id])
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route("/user_account/logout_ok")
def logout_ok():
    session["name"] = "Name"
    session["mail"] = ""
    session["passw"] = ""
    session["mw"] = ""
    return redirect(url_for('index'))


@app.route("/user_account")
def edit_account():
    return render_template("user_account.html")

@app.route("/user_account/logout")
def logout():
    return render_template("logout.html")

@app.route("/<int:post_id>/edit/delete_blog")
def delete_blog(post_id):
    post = get_post(post_id)
    return render_template("delete.html",post=post)

@app.route("/<int:post_id>/edit", methods=["GET", "POST"])
def edit(post_id, error = "", title="", content=""):
    post = get_post(post_id)
    if request.method =="POST":
        if request.form['submit_button'] == "Edit":
            title, content = request.form.get("title"), request.form.get("content")
            if title != "" and content != "":
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("UPDATE post SET title = (?), content = (?) WHERE id = (?)", [title, content, post_id])
                conn.commit()
                conn.close()
                return redirect(url_for('index'))
            elif (title == "" and content == "") or title == "" or content == "":
                return render_template("edit.html", error="!It looks like one of your forms is empty", title=title, content=content)
        elif request.form['submit_button'] == "Delete":
            print("Delete")
            return redirect(url_for('delete_blog', post_id=post_id))
    return render_template("edit.html", post=post)

@app.route('/login/', methods=['GET', 'POST'])
def login(i = {"error": "", "name": "","passw": ""}):
    if request.method == "POST":
        l_mail = request.form.get("mail")
        password = request.form.get("inputPassword")
        hash = hashlib.sha256()
        conn = connect_us()
        cursor = conn.cursor()
        cursor.execute("SELECT gmail FROM user")
        mails = cursor.fetchall()
        mails = [i[0] for i in mails]
        if l_mail in mails:
            l_password = bytes(password, encoding='utf8')
            l_password = hash.update(l_password)
            l_password = hash.hexdigest()
            conn = connect_us()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user WHERE gmail = ?", [l_mail])
            l_user_g = cursor.fetchall()
            l_user_g = [i for i in l_user_g]
            l_user = []
            for i in l_user_g:
                for el in i:
                    l_user.append(el)
            if l_password == l_user[3]:
                session["name"] = l_user[1]
                session["mail"] = l_user[2]
                session["passw"] = password
                session["mw"] = l_user[4]
                return redirect(url_for('index'))
            else:
                return render_template("login.html", i={"error": "! This password is incorrect",
                                                        "mail": l_mail, "passw": password})
        else:
            return render_template("login.html", i={"error": "! This mail doesn`t exists, please register at first", "mail": l_mail, "passw": password})
    return render_template("login.html", i = {"error": "", "mail": "","passw": ""})

@app.route("/check_your_mail_to_change_password/",methods=['GET', 'POST'])
def change_password_check():
    error = ""
    if request.method == "POST":
        g_code = request.form.get('code')
        if g_code == c_code:
            session["passw"] = c_passw
            conn = connect_us()
            cursor = conn.cursor()
            cursor.execute("UPDATE user SET password = (?) WHERE gmail = (?)", [c_passw_s, c_mail])
            conn.commit()
            return redirect(url_for('index'))
        else:
            error = "!Your code isn`t right"
    check_user(c_user[1], c_mail, c_code)
    return render_template("checkyourmail1.html", error = error)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password(i = {"error": "","mail":"","passw": "", "cpassw": ""}):
    if request.method == "POST":
        global c_mail, c_passw
        c_mail = request.form.get("mail")
        c_passw = request.form.get("inputPassword1")
        c_cpassw = request.form.get("checkPassword1")
        print(c_passw)
        if len(c_passw) >= 9:
            if c_passw == c_cpassw:
                conn = connect_us()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM user WHERE gmail = ?", [c_mail])
                c_user_g = cursor.fetchall()
                c_user_g = [i for i in c_user_g]
                global c_user
                c_user = []
                for i in c_user_g:
                    for el in i:
                        c_user.append(el)
                hash = hashlib.sha256()
                global c_passw_s
                c_passw_s = bytes(c_passw, encoding='utf8')
                c_passw_s = hash.update(c_passw_s)
                c_passw_s = hash.hexdigest()
                if c_passw_s == c_user[3]:
                    return render_template("change_passw.html",
                                           i={"error": "!This is your password already", "mail": c_mail, "passw": c_passw,
                                              "cpassw": c_cpassw})
                else:
                    global c_code
                    c_code = list()
                    for i in range(9):
                        c_code.append(choice(digits))
                    c_code = ''.join(c_code)
                    return redirect(url_for('change_password_check'))
            else:
                return render_template("change_passw.html",
                                       i={"error": "!Your passwords aren`t same", "mail": c_mail, "passw": c_passw, "cpassw": c_cpassw})
        else:
            return render_template("change_passw.html", i={"error": "!Your password is too short", "mail":c_mail, "passw": c_passw, "cpassw": c_cpassw})
    return render_template("change_passw.html", i = {"error": "", "mail":"", "passw": "", "cpassw": ""})

@app.route('/register/', methods=['GET', 'POST'])
def register(i={"error": "", "name": "", "mail": "", "passw": "", "mw": ""}):
    if request.method =="POST":
        checked_m = ""
        checked_w = ""
        global r_name, r_mail, r_passw, r_mw
        hash = hashlib.sha256()
        hash1 = hashlib.sha256()
        r_name, r_mail,  r_mw = request.form.get("name"), request.form.get("mail"), request.form.get("inlineRadioOptions")
        r_passw = request.form.get("inputPassword")
        r_passc = request.form.get("confPassword")
        conn = connect_us()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM user")
        names = cursor.fetchall()
        names = [i[0] for i in names]
        cursor.execute("SELECT gmail FROM user")
        mails = cursor.fetchall()
        mails = [i[0] for i in mails]
        conn.close()
        print(names, mails)
        if not (r_name in names or r_mail in mails):
            if not len(r_passw) < 9:
                if r_mw == "man":
                    checked_m = "checked"
                    checked_w = ""
                elif r_mw == "woman":
                    checked_m = ""
                    checked_w = "checked"
                if r_passw == r_passc and r_passw != "" and r_name != "" and r_mail != "" and r_passw != "" and r_passc != "" and r_mw  != None:
                    global a_code
                    a_code = list()
                    for i in range(9):
                        a_code.append(choice(digits))
                    a_code = ''.join(a_code)
                    return redirect(url_for('check_your_mail'))
                elif r_name == "" or r_mail == "" or r_passw == "" or r_passc == "" or r_mw  == None:
                    return render_template("register.html", i={"error": "! Please check your form", "name":r_name, "mail":r_mail, "passw":r_passw, "passc":r_passc,"checked_w":checked_w, "checked_m": checked_m})

                elif r_passw != r_passc:
                    print("error")
                    return render_template("register.html", i={"error": "! Please check your password", "name":r_name, "mail":r_mail, "passw":r_passw, "passc":"","checked_w":checked_w, "checked_m": checked_m})
            else:
                return render_template("register.html",
                                       i={"error": "! Your password is too short", "name": r_name, "mail": r_mail,
                                          "passw": r_passw, "passc": "", "checked_w": checked_w, "checked_m": checked_m})
        else:
            return render_template("register.html",
                                   i={"error": "! This name or mail is already exists", "name": r_name, "mail": r_mail,
                                      "passw": r_passw, "passc": "", "checked_w": checked_w, "checked_m": checked_m})

    return render_template("register.html", i={"error": "", "name": "", "mail": "","passc":"", "passw": "", "mw": ""})

@app.route("/create/", methods=['GET', 'POST'])
def new_post(error = "", title="", content=""):
    if request.method =="POST":
        title, content = request.form.get("title"), request.form.get("content")
        if title != "" and content != "" and session.get("name") != None:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO post(title, content, author) VALUES(?, ?, ?)", (title, content, session["name"]))
            title, content = "", ""
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        elif session.get("name") == None:
            return render_template("create.html", error="!You need to have an account to create blogs", title=title,content=content)
        elif (title == "" and content == "") or title == "" or content == "":
            return render_template("create.html", error="!It looks like one of your forms is empty", title=title,
                                   content=content)
    return render_template("create.html", error = "", title="", content="")

app.run(debug = True)

# # cursor = connect.cursor()
# # # cursor.execute("DROP TABLE post")
# # cursor.execute("INSERT INTO post(title,content) VALUES (?,?)", ["Welcome to FlaskBlog", "Here you can login, create you own blogs, and be a BLOG STAR!"])
# connect.commit()
# # connect.close()