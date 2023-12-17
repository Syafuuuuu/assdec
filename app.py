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
    return jsonify(rowdata=rowdata)

#-----------Insert Assets-----------
@app.route('/insertAss', methods = ['POST'])
def insertAss():
    if request.method == "POST":
        assDecType = request.form['assType']
        assDecCat = request.form['assCat']
        assDec = request.form['assDec']
        assAddr = request.form['assAdd1'] + ", " + request.form['assAdd2'] + ", " + request.form['assPostCode'] + ", " + request.form['assCity'] + ", " + request.form['assState'] + ", Malaysia"
        assOwner = request.form['assOwner']
        assCert = request.form['assCert']
        assDateOwn = request.form['assDateOwn']
        assQuantity = request.form['assQuantity']
        assMeasurement = request.form['assMeasurement']
        assAcqVal = request.form['assAcqVal']
        assCurVal = request.form['assCurVal']
        assAcq = request.form['assAcq']

        cur = mysql.connection.cursor()
        cur.execute ("INSERT INTO assets (username, dateOfApp, AssDecType, AssDecCat, Description, Address, Owner, RegCertNo, DateOfOwnership, Quantity, Measurement, AssAcqVal, CurrAssVal, AcqMethod) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (session.get('username', None), str(date.today()), assDecType, assDecCat, assDec, assAddr, assOwner, assCert, assDateOwn, assQuantity, assMeasurement, assAcqVal, assCurVal, assAcq))
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