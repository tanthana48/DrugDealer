from flask import Flask, render_template, request, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

from flask_mysqldb import MySQL
import yaml

app = Flask(__name__)
app.config['SECRET_KEY'] = "Never push this line to github public repo"

cred = yaml.load(open('cred.yaml'), Loader=yaml.Loader)
app.config['MYSQL_HOST'] = cred['mysql_host']
app.config['MYSQL_USER'] = cred['mysql_user']
app.config['MYSQL_PASSWORD'] = cred['mysql_password']
app.config['MYSQL_DB'] = cred['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.before_first_request
def initweb():
    cur = mysql.connection.cursor()
    queryStatement = f"SELECT * FROM role"
    result = cur.execute(queryStatement)
    print(result)
    if result == 0:
        createrole = (
                f"INSERT INTO "
                f"role(role_id, role_type, role_name) "
                f"VALUES(1, 'USER', 'user')"
            )
        createrole1 = (
                f"INSERT INTO "
                f"role(role_id, role_type, role_name) "
                f"VALUES(2, 'ADMIN', 'admin')"
            )
        cur.execute(createrole)
        cur.execute(createrole1)
        mysql.connection.commit()
    
    queryStatement = f"SELECT * FROM employee WHERE username = 'admin'"
    result1 = cur.execute(queryStatement)
    print(result1)
    if result1 == 0:
        hashed_pw = generate_password_hash('123456')
        queryStatement = (
                f"INSERT INTO "
                f"employee(username, password, firstname, lastname, email, employee_tel, role_id) "
                f"VALUES('admin', '{hashed_pw}', 'admin', 'admin', 'admin', '0000000000', 2)"
            )
        cur.execute(queryStatement)
        mysql.connection.commit()
    cur.close()

@app.route("/")
def index():
    if 'login' not in session:
        return redirect('login')
    elif session['userroleid'] == str(2):
    	return render_template("index_admin.html")
    else:
    	return render_template("index_employee.html")

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if 'login' in session:
        flash('You have already sign in', 'danger')
        return redirect('/')
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        loginForm = request.form
        username = loginForm['username']
        cur = mysql.connection.cursor()
        queryStatement = f"SELECT * FROM employee WHERE username = '{username}'"
        numRow = cur.execute(queryStatement)
        if numRow > 0:
            user =  cur.fetchone()
            if check_password_hash(user['password'], loginForm['password']):
                # Record session information
                session['login'] = True
                session['username'] = user['username']
                session['userroleid'] = str(user['role_id'])
                session['firstName'] = user['firstname']
                session['lastName'] = user['lastname']
                session['tel'] = user['employee_tel']
                session['email'] = user['email']
                print(session['username'] + " roleid: " + session['userroleid'] + " email: " + session['email'] + " phone number: " + session['tel'])
                flash('Welcome ' + session['firstName'], 'success')
                #flash("Log In successful",'success')
                return redirect('/')
            else:
                cur.close()
                flash("Password doesn't match", 'danger')
        else:
            cur.close()
            flash('User not found', 'danger')
            return render_template('login.html')
        cur.close()
        return redirect('/')
    return render_template('login.html')

@app.route('/member/')
def members():
    try:
        username = session['username']
    except:
        flash('Please sign in first', 'danger')
        return redirect('/login')

    cur = mysql.connection.cursor()
    queryStatement = f"SELECT * FROM member"
    print(queryStatement)
    result_value = cur.execute(queryStatement) 
    if result_value > 0:
        members = cur.fetchall()
        return render_template('member.html', members=members)
    else:
        return render_template('member.html')
    
@app.route('/user/')
def users():
    try:
        username = session['username']
    except:
        flash('Please sign in first', 'danger')
        return redirect('/login')

    cur = mysql.connection.cursor()
    queryStatement = f"SELECT * FROM employee"
    print(queryStatement)
    result_value = cur.execute(queryStatement) 
    if result_value > 0:
        users = cur.fetchall()
        return render_template('users.html', users=users)
    else:
        return render_template('users.html')

@app.route('/stock/', methods=['GET', 'POST'])
def stock():
    try:
        username = session['username']
    except:
        flash('Please sign in first', 'danger')
        return redirect('/login')
    cur = mysql.connection.cursor()
    queryStatement = f"SELECT * FROM medicine"
    cur.execute(queryStatement)
    medsList = cur.fetchall()
    if session['userroleid'] == str(2):
    	return render_template('stock-admin.html', medicines=medsList)
    else:
    	return render_template('stock-employee.html', medsList=medsList)

@app.route('/search/', methods=['GET', 'POST'])
def search():
    try:
        username = session['username']
    except:
        flash('Please sign in first', 'danger')
        return redirect('/login')

    s = request.form['search']
    cur = mysql.connection.cursor()
    queryStatement = f"SELECT * FROM medicine WHERE medicine_name like '%"+s+"%'"
    cur.execute(queryStatement)
    medsList = cur.fetchall()
    if session['userroleid'] == str(2):
        return render_template('stock-admin.html', medicines=medsList)
    else:
        return render_template('stock-employee.html', medsList=medsList)

    
    
# @app.route('/stock-admin/')
# def stock_admin():
#     try:
#         username = session['username']
#     except:
#         flash('Please sign in first', 'danger')
#         return redirect('/login')

#     cur = mysql.connection.cursor()
#     queryStatement = f"SELECT * FROM medicine"
#     print(queryStatement)
#     result_value = cur.execute(queryStatement) 
#     if result_value > 0:
#         medicines = cur.fetchall()
#         return render_template('stock-admin.html', medicines=medicines)
#     else:
#         return render_template('stock-admin.html')

@app.route('/addmed/', methods=['GET', 'POST'])
def addmed():
    try:
        username = session['username']
    except:
        flash('Please sign in first', 'danger')
        return redirect('/login')
    if request.method == 'GET':
        return render_template('new-medicine.html')
    elif request.method == 'POST':
        medDetails = request.form
        
        med1 = medDetails['medicine_name']
        med2 = medDetails['medicine_detail']
        med3 = medDetails['medicine_price']
        med4 = medDetails['medicine_stock']
        
        print(med1 + "," + med2 + "," + med3 + "," + med4)
        
        queryStatement = (
            f"INSERT INTO "
            f"medicine(medicine_name, medicine_detail, medicine_price, medicine_stock) "
            f"VALUES('{med1}', '{med2}', {med3}, {med4})"
        )
        print(queryStatement)
        cur = mysql.connection.cursor()
        cur.execute(queryStatement)
        mysql.connection.commit()
        cur.close()
        
        flash("Added Medicine Successfully.", "success")
        return redirect('/stock')    
    return render_template('new-medicine.html')

@app.route('/edit-medicine/<int:id>/', methods=['GET', 'POST'])
def edit_medicine(id):
    try:
        username = session['username']
    except:
        flash('Please sign in first', 'danger')
        return redirect('/login')
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        name = request.form['medicine_name']
        detail = request.form['medicine_detail']
        price = request.form['medicine_price']
        stock = request.form['medicine_stock']
        queryStatement = f"UPDATE medicine SET medicine_name= '{name}', medicine_detail = '{detail}', medicine_price = {price}, medicine_stock = {stock}  WHERE medicine_id = {id}"
        print(queryStatement)
        cur.execute(queryStatement)
        mysql.connection.commit()
        cur.close()
        flash('Medicine updated', 'success')
        return redirect('/stock')
    else:
        cur = mysql.connection.cursor()
        queryStatement = f"SELECT * FROM medicine WHERE medicine_id = {id}"
        print(queryStatement)
        result_value = cur.execute(queryStatement)
        if result_value > 0:
            medicine = cur.fetchone()
            medicine_form = {}
            medicine_form['medicine_id'] = medicine['medicine_id']
            medicine_form['medicine_name'] = medicine['medicine_name']
            medicine_form['medicine_detail'] = medicine['medicine_detail']
            medicine_form['medicine_price'] = medicine['medicine_price']
            medicine_form['medicine_stock'] = medicine['medicine_stock']
            return render_template('edit-medicine.html', medicine_form=medicine_form)

@app.route('/delete-medicine/<int:id>/', methods=['GET'])
def delete_medicine(id):
    try:
        username = session['username']
    except:
        flash('Please sign in first', 'danger')
        return redirect('/login')
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        queryStatement = f"DELETE FROM medicine WHERE medicine_id = {id}"
        print(queryStatement)
        cur.execute(queryStatement)
        mysql.connection.commit()
        cur.close()
        flash('Delete Medicine Successfully', 'success')
        return redirect('/stock/')
        

@app.route('/createmember/', methods=['GET', 'POST'])
def createmember():
    try:
        username = session['username']
    except:
        flash('Please sign in first', 'danger')
        return redirect('/login')
    if request.method == 'GET':
        return render_template('createmember.html')
    elif request.method == 'POST':
        memberDetails = request.form
        
        mem1 = memberDetails['member_name']
        mem2 = memberDetails['member_tel']
        
        print(mem1 + "," + mem2)
        
        queryStatement = (
            f"INSERT INTO "
            f"member(name, member_tel, member_point) "
            f"VALUES('{mem1}', '{mem2}', 0)"
        )
        print(queryStatement)
        cur = mysql.connection.cursor()
        cur.execute(queryStatement)
        mysql.connection.commit()
        cur.close()
        
        flash("Create Member Successfully.", "success")
        return redirect('/member')    
    return render_template('createmember.html')

@app.route('/edit-member/<int:id>/', methods=['GET', 'POST'])
def edit_member(id):
    try:
        username = session['username']
    except:
        flash('Please sign in first', 'danger')
        return redirect('/login')
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        point = request.form['member_point']
        tel = request.form['member_tel']
        queryStatement = f"UPDATE member SET member_point= '{point}', member_tel = '{tel}' WHERE member_id = {id}"
        print(queryStatement)
        cur.execute(queryStatement)
        mysql.connection.commit()
        cur.close()
        flash('Member updated', 'success')
        return redirect('/member')
    else:
        cur = mysql.connection.cursor()
        queryStatement = f"SELECT * FROM member WHERE member_id = {id}"
        print(queryStatement)
        result_value = cur.execute(queryStatement)
        if result_value > 0:
            member = cur.fetchone()
            member_form = {}
            member_form['member_tel'] = member['member_tel']
            member_form['member_point'] = member['member_point']
            member_form['member_name'] = member['name']
            return render_template('edit-member.html', member_form=member_form)

@app.route('/edit-user/<int:id>/', methods=['GET', 'POST'])
def edit_user(id):
    try:
        username = session['username']
    except:
        flash('Please sign in first', 'danger')
        return redirect('/login')
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        tel = request.form['employee_tel']
        role = request.form['role_id']
        queryStatement = f"UPDATE employee SET firstname = '{firstname}', lastname = '{lastname}', email = '{email}', employee_tel = '{tel}', role_id = {role} WHERE employee_id = {id}"
        print(queryStatement)
        cur.execute(queryStatement)
        mysql.connection.commit()
        cur.close()
        flash('User updated', 'success')
        return redirect('/user')
    else:
        cur = mysql.connection.cursor()
        queryStatement = f"SELECT * FROM employee WHERE employee_id = {id}"
        print(queryStatement)
        result_value = cur.execute(queryStatement)
        if result_value > 0:
            user = cur.fetchone()
            user_form = {}
            user_form['username'] = user['username']
            user_form['firstname'] = user['firstname']
            user_form['lastname'] = user['lastname']
            user_form['email'] = user['email']
            user_form['employee_tel'] = user['employee_tel']
            user_form['role_id'] = user['role_id']
            return render_template('edit-user.html', user_form=user_form)
        
@app.route('/delete-member/<int:id>/', methods=['GET'])
def delete_member(id):
    try:
        username = session['username']
    except:
        flash('Please sign in first', 'danger')
        return redirect('/login')
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        queryStatement = f"DELETE FROM member WHERE member_id = {id}"
        print(queryStatement)
        cur.execute(queryStatement)
        mysql.connection.commit()
        cur.close()
        flash('Delete Member Successfully', 'success')
        return redirect('/member/')

@app.route('/delete-user/<int:id>/', methods=['GET'])
def delete_user(id):
    try:
        username = session['username']
    except:
        flash('Please sign in first', 'danger')
        return redirect('/login')
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        queryStatement = f"DELETE FROM employee WHERE employee_id = {id}"
        print(queryStatement)
        cur.execute(queryStatement)
        mysql.connection.commit()
        cur.close()
        flash('Delete User Successfully', 'success')
        return redirect('/user/')

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if 'login' in session:
        flash('Logout first', 'danger')
        return redirect('/')
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        userDetails = request.form
        
         # Check the password and confirm password
        if userDetails['password'] != userDetails['confirm_password']:
            flash("Passwords do not match!", "danger")
            return render_template('register.html')
        p1 = userDetails['username']
        p2 = userDetails['password']
        p3 = userDetails['first_name']
        p4 = userDetails['last_name']
        p5 = userDetails['email']
        p6 = userDetails['tel']
        
        hashed_pw = generate_password_hash(p2)
        
        print(p1 + "," + p2 + "," + hashed_pw + "," + p3 + "," + p4 + "," + p5 + "," + p6)
        
        queryStatement = (
            f"INSERT INTO "
            f"employee(username, password, firstname, lastname, email, employee_tel, role_id) "
            f"VALUES('{p1}', '{hashed_pw}', '{p3}', '{p4}', '{p5}', '{p6}', 1)"
        )
        print(check_password_hash(hashed_pw, p2))
        print(queryStatement)
        cur = mysql.connection.cursor()
        cur.execute(queryStatement)
        mysql.connection.commit()
        cur.close()
        
        flash("Register Successfully.", "success")
        return redirect('/')    
    return render_template('register.html')

@app.route('/logout')
def logout():
    if 'login' not in session:
        flash('You have not logged in', 'danger')
        return redirect('/')
    session.clear()
    flash("You have been logged out", 'info')
    return redirect('/')

@app.route('/index_employee/')
def index_employee():
    return render_template('index_employee.html')

@app.route('/payment/', methods=['GET'])
def payment():
    try:
        username = session['username']
    except:
        flash('Please sign in first', 'danger')
        return redirect('/login')
    cur = mysql.connection.cursor()
    queryStatement = f"SELECT * FROM medicine"
    print(queryStatement)
    result_value = cur.execute(queryStatement) 
    if request.method == 'GET':
        if result_value > 0:
            medicines = cur.fetchall()
            return render_template('payment.html', medicines=medicines)
        else:
            return render_template('payment.html',mediciness=None)
    # elif request.method == 'POST':
    #     queryStatement = f"SELECT * FROM medicine"
    #     result_value = cur.execute(queryStatement) 
    #     medicines = cur.fetchall()
    #     drugsNumber = request.form
    #     for x in range(10):
    #         print(drugsNumber[x])
            
    
@app.route('/CheckOut/', methods=['POST'])
def CheckOut():
    try:
        username = session['username']
    except:
        flash('Please sign in first', 'danger')
        return redirect('/login')
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        queryStatement = f"SELECT * FROM medicine"
        result_value = cur.execute(queryStatement) 
        medicines = cur.fetchall()
        drugsNumber = request.form
        print(drugsNumber)
        length=len(medicines)
        print(medicines[1])
        total = 0;
        for i in range(length):
            if drugsNumber[medicines[i]['medicine_name']] != '':
                n = int(drugsNumber[medicines[i]['medicine_name']])
                if (medicines[i]['medicine_stock']<n):
                    flash('Are you stupid?', 'danger')
                    return redirect('/payment')
                total += n * medicines[i]['medicine_price']
                left = medicines[i]['medicine_stock']-n
                queryStatement = f"update medicine set medicine_stock = '{left}' where medicine_name = '{medicines[i]['medicine_name']}'"
                cur.execute(queryStatement)
                mysql.connection.commit()
                cur.close()
                flash('Stock updated', 'success')
                
    return render_template('proceedCheckOut.html', medicines=medicines, orders=drugsNumber, length=length, total=total)    

if __name__ == '__main__':
    app.run(debug=True)

    
