from flask import Flask,render_template,request,redirect,flash,session
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
import re

EMAIL_REGEX=re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app=Flask(__name__)
bcrypt=Bcrypt(app)
app.secret_key='thisissecret'

@app.route('/')
def start():
    print(session)
    return render_template('login.html')

@app.route('/registration', methods=["POST"])
def regi():
    if len(request.form['fname'])<1:
        flash("First name cannot be empty","flashfname")
    elif request.form['fname'].isalpha() == False:
        flash("Invalid, number input not valid in first name","flashfname")
    if len(request.form['lname'])<1:
        flash("Last name cannot be empty", "flashlname")
    elif request.form['lname'].isalpha() == False:
        flash("Invalid, number input not valid in last name","flashlname")
    mysql=connectToMySQL("wishes")
    query= "Select * from users where email = %(email)s;"
    data={ "email": request.form["email"]}
    checkingforduplicateemails=mysql.query_db(query,data)
    if len(checkingforduplicateemails) != 0:
        flash("Email name already exists","flashemail")
    elif len(request.form['email']) <1:
        flash("Email cannot be left empty","flashemail")
    elif not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email, must follow name@domain.com","flashemail")
    if len(request.form['password'])<8:
        flash("Password must be at least 8 characters long","flashpassword")
    elif len(request.form['password'])>15:
        flash("Password must be less than 15 characters long","flashpassword")
    elif request.form['password'] != request.form['pconfirm']:
        flash("Password and Password Confirmation do not match","flashpassword")
    else:
        hashedpass=bcrypt.generate_password_hash(request.form['password'])
    if '_flashes' in session.keys():
        return redirect('/')
    else:
        mysql=connectToMySQL("wishes")
        query="insert into users (fname,lname,email,password,created_at) values (%(fname)s,%(lname)s,%(email)s,%(password_hash)s,NOW());"
        data={
            "fname":request.form["fname"],
            "lname":request.form["lname"],
            "email":request.form["email"],
            "password_hash":hashedpass
        }
        mysql.query_db(query,data)

        mysql=connectToMySQL("wishes")
        query= "Select * from users where email = %(email)s;"
        data={ "email": request.form["email"]}
        answers=mysql.query_db(query,data)
        session['usernameid']=answers[0]['id']
        print(session['usernameid'])
        return redirect('/wishes')

@app.route('/login', methods=["POST"])
def log():
    if len(request.form['loginemail'])<1:
        flash("Invalid User name","flashloginemail")
    mysql=connectToMySQL("wishes")
    query= "Select * from users where email = %(email)s;"
    data={ "email": request.form["loginemail"]}
    answers=mysql.query_db(query,data)
    if len(answers)==0:
        flash("Account does not exist","flashloginemail")
    if answers:
        if bcrypt.check_password_hash(answers[0]["password"],request.form["loginpassword"]):
            session['usernameid']=answers[0]['id']
            print(session['usernameid'])
        else:
            flash("Incorrect password","flashloginpassword")
    if '_flashes' in session.keys():
        return redirect('/')
    else:
        return redirect('/wishes')

@app.route('/wishes')
def wishupona():

    mysql=connectToMySQL("wishes")
    query="Select users.id,concat(users.fname,' ',users.lname) as full_name, wishes.id, wishes.name, wishes.description, wishes.granted, wishes.created_at from users left join wishes on users.id= wishes.user_id where users.id= %(id)s;"
    data={
        "id":session['usernameid']
    }
    mywishes=mysql.query_db(query,data)
    session['currentuserinfo']=mywishes

    mysql=connectToMySQL("wishes")
    query="Select concat(users.fname,' ',users.lname) as full_name, wishes.name, wishes.created_at, wishes.updated_at, wishes.description, wishes.granted from users left join wishes on users.id= wishes.user_id;"
    data={
        "id":session['usernameid']
    }
    notmywishes=mysql.query_db(query,data)
    print(notmywishes)
    print('\n\n\n\n',session['currentuserinfo'],'\n\n\n\n\n')

    return render_template('wishes.html',mywishes=mywishes,notmywishes=notmywishes)

@app.route('/addto')
def addto():
    return render_template('add.html', mywishes=session['currentuserinfo'])

@app.route('/add', methods=["POST"])
def addtolist():
    if len(request.form['description'])<1:
        flash("Must provide a wish description","flashwishdescription")
    elif len(request.form['wishname'])<3:
        flash("Must provide a wish longer than 3 characters","flashwishname")
    if '_flashes' in session.keys():
        return redirect('/addto')
    else:
        mysql=connectToMySQL("wishes")
        query="insert into wishes (name,description,user_id,created_at) values (%(wishname)s,%(description)s,%(user_id)s,NOW());"
        data={
            "wishname":request.form["wishname"],
            "description":request.form["description"],
            "user_id":session['currentuserinfo'][0]['id'],
        }
        mysql.query_db(query,data)
        flash("Congratulations, wish added","flashsuccess")
        return redirect('/addto')

@app.route('/edit')
def edittttt():
    return render_template('edit.html',mywishes=session['currentuserinfo'])


@app.route('/editvalue', methods=["POST"])
def value():
    session['editvalue']=request.form['editvalue']
    print(session['editvalue'])
    return redirect('/edit')


@app.route('/editthis', methods=["POST"])
def edit():
    if len(request.form['editdescription'])<3:
        flash("Must provide a wish description longer than 3 characters","flashededitdescription")
    if len(request.form['editwish'])<3:
        flash("Must provide a wish name longer than 3 characters","flasheditwish")
    if '_flashes' in session.keys():
        return redirect('/edit')
    else:
        mysql=connectToMySQL("wishes")
        query="update wishes set name=%(editwish)s, description=%(editdescription)s where wishes.id = %(wishid)s;"
        data={
            'editwish':request.form['editwish'],
            'editdescription':request.form['editdescription'],
            'wishid':session['editvalue']
        }
        worked=mysql.query_db(query,data)
        print(worked)
        flash("Congratulations, wish updated","flasheditsuccess")
        return redirect('/edit')

@app.route('/remove', methods=["POST"])
def remove():
    mysql=connectToMySQL("wishes")
    query="delete from wishes.wishes where wishes.id= %(delete)s;"
    data={
        'delete':request.form["delete"]
    }
    mysql.query_db(query,data)
    return redirect('/wishes')
    
@app.route('/granted', methods=["POST"])
def granted():
    mysql=connectToMySQL('wishes')
    query="update wishes set granted='True' where wishes.id =%(wishid)s;"
    data={
        'wishid':request.form['granted']
    }
    granted=mysql.query_db(query,data)
    print(granted)
    return redirect('/wishes')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__=="__main__":
    app.run(debug=True)