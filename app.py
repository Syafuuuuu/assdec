from datetime import date
from flask import Flask, jsonify, render_template , request, redirect, session, url_for, flash, redirect
from urllib.parse import urljoin

from flask_mysqldb import MySQL

app = Flask (__name__)
app.secret_key = 'flash_message'

app.config ['MYSQL_HOST'] = 'localhost'
app.config ['MYSQL_USER'] = 'root'
app.config ['MYSQL_PASSWORD'] = ''
app.config ['MYSQL_DB'] = 'assdec'

mysql = MySQL(app)
app.secret_key = "flash_message"


#-----------Go to Login age-----------
@app.route('/')
def start():

    return render_template('loginPage.html')

#-----------Home-----------
@app.route('/home')
def index():

    user = session.get('username', None)
    print(user)
    cur = mysql.connection.cursor()
    cur.execute("""SELECT `AssetID`,`dateOfApp`,`AssDecType`,`AssDecCat`,`Description` FROM `assets` WHERE `username` = %s """,(user,))
    data = cur.fetchall()
    cur.close()

    return render_template('home.html', appnts=data, usrnm = user)

#-----------View Assets-----------
@app.route('/viewAss/<string:assID>',methods=['POST','GET'])
def viewAss(assID):
    print(assID)
    cur = mysql.connection.cursor()
    cur.execute("""SELECT * FROM `assets` WHERE `AssetID` = %s """,(assID,))
    rowdata = cur.fetchone()
    cur.close
    print(rowdata)
    return jsonify(rowdata)

#-----------Insert Assets-----------
@app.route('/insertAss', methods = ['POST'])
def insertAss():
    if request.method == "POST":
        id = request.form['id']
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute ("INSERT INTO customer (custID, custName, custPnum, custEmail) VALUES (%s, %s, %s, %s)", (id, name, phone, email))
        mysql.connection.commit()
        flash("Data Inserted Successfully")
        return redirect(url_for ('index'))

#-----------Login Page-----------
@app.route('/loginPage')
def loginPage():

		return render_template('loginPage.html')

#-----------Login Process-----------
@app.route('/login', methods=['POST'])
def login():
      if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute('SELECT `username`,`password` FROM `user` WHERE `username`= %s AND `password`=%s', (username,password))
        usr = cur.fetchone()
    
        if usr:
            session['username'] = username
            session['Log'] = True

            return redirect(url_for('index'))
        else:
            return '<script>alert("Incorrect username or password."); window.location="/";</script>'


if __name__ == '__main__':
    app.run(debug=True)