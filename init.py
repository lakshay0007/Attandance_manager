from flask import Flask,render_template,flash,request,url_for,redirect,session
from c_manage import Content
from dbconnect import connection
from wtforms import Form, BooleanField,TextField,PasswordField,validators #web template forms
from passlib.hash import sha256_crypt 
from pymysql import escape_string as thwart #prevent injection
import gc
import time
from functools import wraps
import botinclude
import re
import random



replies = {'Jack':'thanks',
               'Jane':'Nice content',
               'Erika':'Most definitely',
               'Bob':'wow',
               'Carl':'amazing!',}

TOPIC_DICT=Content()

app=Flask(__name__)
app.secret_key = 'super'

@app.route('/')
def homepage():
	return render_template("main.html")

@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html")
	

@app.route('/login/', methods=["GET","POST"])
def login_page():
    error = ''
    try:
        c, conn = connection()
        if request.method == "POST":

            data = c.execute("SELECT * FROM users WHERE username = (%s)",
                             thwart(request.form['username']))
            
            data = c.fetchone()[2]

            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in'] = True
                session['username'] = request.form['username']
                flash("You are now logged in")
                return redirect(url_for("dashboard"))               

            else:
                error = "Invalid credentials (password) , try again."
                flash(error)

        gc.collect()

        return render_template("login.html", error=error)
        

    except Exception as e:
        flash('Invalid credentials(username), try again')
        return render_template("login.html", error = error)  

# Focus here on this form:



class Registration(Form):
    username=TextField('Username',[validators.Length(min=4,max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated Aug 21, 2018)', [validators.DataRequired()])

@app.route('/register/', methods=["GET","POST"])
def register_page():
    try:
        form=Registration(request.form)
        if request.method=="POST" and form.validate():
            username=form.username.data
            email=form.email.data
            password=sha256_crypt.encrypt((str(form.password.data)))
            c,conn=connection()

            x = c.execute("SELECT * FROM users WHERE username = (%s)",(thwart(username)))

            if int(x) > 0:
                flash("That username is already taken, please choose another")
                return render_template("register.html", form=form)

            else:
                c.execute("INSERT INTO users (username, password, email, tracking) VALUES (%s, %s, %s, %s)",
                          (thwart(username), thwart(password), thwart(email), thwart("/introduction-to-python-programming/")))
                
            conn.commit() #save to database
            flash("Thanks for registering!")
            c.close()  #closes cursor
            conn.close() #close connection
            gc.collect() #garbage collector clears out unused cache memory

            session['logged_in'] = True #dictionary
            session['username'] = username

            return redirect(url_for('dashboard'))

        return render_template("register.html", form=form)   

    except Exception as e:
        return(str(e))
		



def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login_page'))

    return wrap


@app.route("/logout/")
@login_required                         # need to first define login_required function above
def logout():
    session.clear()
    flash('You have been logged out')
    gc.collect()
    return redirect(url_for('homepage'))   

@app.route('/include_example/')
def include_example():
    return render_template("includes_tutorial.html",replies=replies)


@app.route('/comment/', methods=['POST'])
def comment():
    replies = {'Jack':'Cool post',
               'Jane':'good content',
               'Bob':'wow',}

    #new_comment=request.form['text']

    replies['You']=request.form['text']
    return render_template("dashboard.html",replies=replies) 
    #return 'You entered: {}'.format(replies['You'])
    #return 'You entered: {}'.format(request.form['text'])         
    #return 'You entered: {}'.format(replies['You']) 

@app.route('/dashboard/')
def dashboard():
    return render_template("dashboard.html", TOPIC_DICT = TOPIC_DICT,replies=replies)

@app.route('/interactive/')
def interactive():
    return render_template('interactive.html')

@app.route('/background_process/',methods=['POST'])
def background_process():
    try:
      print("ELIZA-->Hello. How are you feeling today?")            
      lang = request.form['text1']
      ans="USER-->"+botinclude.analyze(lang)

      return render_template('interactive.html',ans=ans)
    except Exception as e:
        return str(e)        

if __name__=="__main__":
	app.secret_key = 'super'
	app.run(debug=1)

	