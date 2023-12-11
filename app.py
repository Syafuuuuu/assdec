from datetime import date
from flask import Flask, render_template , request, redirect, session, url_for, flash, redirect
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

@app.route('/')
def start():

    return render_template('loginPage.html')

@app.route('/home')
def index():

    user = session.get('username', None)
    print(user)
    cur = mysql.connection.cursor()
    cur.execute("""SELECT `AssetID`,`dateOfApp`,`AssDecType`,`AssDecCat`,`Description` FROM `assets` WHERE `username` = %s """,(user,))
    data = cur.fetchall()
    cur.close()

    return render_template('home.html', appnts=data, usrnm = user)

@app.route('/insertAss', methods = ['POST'])
def insertTrmnt():
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

@app.route('/viewAss',methods=['POST','GET'])
def viewAss():
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        desc = request.form['desc']
        type = request.form['type']
        price = request.form['price']
        cur = mysql.connection.cursor()
        cur.execute("""
        UPDATE treatment
        SET trmntName=%s, trmntDesc=%s, trmntType=%s, trmntPrice=%s 
        WHERE trmntID=%s
        """, (name, desc, type, price, id))
        mysql.connection.commit()
        flash("Data Updated Successfully")
        return redirect(url_for('manageTrmnt'))

# @app.route('/customer_management')
# def manageCust():
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM`customer`")
#     data = cur.fetchall()
#     cur.close()

#     return render_template('customer_management.html', appnts=data)

# @app.route('/treatment_management')
# def manageTrmnt():
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM `treatment`")
#     data = cur.fetchall()
#     cur.close()

#     return render_template('treatment_management.html', appnts=data)

# @app.route('/appointment_management')
# def manageAppmnt():
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM `appointment`")
#     data = cur.fetchall()

#     CustCur = mysql.connection.cursor()
#     CustCur.execute("SELECT * FROM `customer`")
#     dataCust = CustCur.fetchall()

#     TrmntCur = mysql.connection.cursor()
#     TrmntCur.execute("SELECT * FROM `treatment`")
#     dataTrmnt = TrmntCur.fetchall()
#     TrmntCur.close()

#     return render_template('appointment_management.html', appnts=data, dataCust=dataCust, dataTrmnt=dataTrmnt)

#region Treatment

# @app.route('/insertTrmnt', methods = ['POST'])
# def insertTrmnt():
#     if request.method == "POST":
#         name = request.form['name']
#         desc = request.form['desc']
#         type = request.form['type']
#         price = request.form['price']
#         cur = mysql.connection.cursor()
#         cur.execute ("INSERT INTO treatment (trmntName, trmntDesc, trmntType, trmntPrice) VALUES (%s, %s, %s, %s)", (name, desc, type, price))
#         mysql.connection.commit()
#         flash("Data Inserted Successfully")
#         return redirect(url_for ('manageTrmnt'))

# @app.route('/updateTrmnt',methods=['POST','GET'])
# def updateTrmnt():
#     if request.method == 'POST':
#         id = request.form['id']
#         name = request.form['name']
#         desc = request.form['desc']
#         type = request.form['type']
#         price = request.form['price']
#         cur = mysql.connection.cursor()
#         cur.execute("""
#         UPDATE treatment
#         SET trmntName=%s, trmntDesc=%s, trmntType=%s, trmntPrice=%s 
#         WHERE trmntID=%s
#         """, (name, desc, type, price, id))
#         mysql.connection.commit()
#         flash("Data Updated Successfully")
#         return redirect(url_for('manageTrmnt'))

# @app.route('/deleteTrmnt/<string:id_data>', methods=['POST','GET'])
# def deleteTrmnt(id_data):
#     cur = mysql.connection.cursor()
#     cur.execute("DELETE FROM treatment WHERE trmntID=%s", (id_data,))
#     mysql.connection.commit()
#     flash("Record Has Been Deleted Successfully")
#     return redirect(url_for('manageTrmnt'))

#endregion

#region Customer
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

# @app.route('/updateCust',methods=['POST','GET'])
# def updateCust():
#     if request.method == 'POST':
#         id = request.form['id']
#         name = request.form['name']
#         phone = request.form['phone']
#         email = request.form['email']
#         cur = mysql.connection.cursor()
#         cur.execute("""
#         UPDATE customer
#         SET custName=%s, custPnum=%s, custEmail=%s
#         WHERE custID=%s
#         """, (name, phone, email, id))
#         mysql.connection.commit()
#         flash("Data Updated Successfully")
#         return redirect(url_for('manageCust'))

# @app.route('/deleteCust/<string:id_data>', methods=['POST','GET'])
# def deleteCust(id_data):
#     cur = mysql.connection.cursor()
#     cur.execute("DELETE FROM customer WHERE custID=%s", (id_data,))
#     mysql.connection.commit()
#     flash("Record Has Been Deleted Successfully")
#     return redirect(url_for('manageCust'))

#endregion

#region Appointment

# @app.route('/insertApp', methods = ['POST'])
# def insertApp():
#     if request.method == "POST":
#         datetime = request.form['datetime']
#         custid = request.form['custid']
#         trmntid = request.form['trmntid']
#         cur = mysql.connection.cursor()
#         cur.execute ("INSERT INTO appointment (appDateTime, custID, trmntiD) VALUES (%s, %s, %s)", (datetime, custid, trmntid))
#         mysql.connection.commit()
#         flash("Data Inserted Successfully")
#         return redirect(url_for ('manageAppmnt'))

# @app.route('/updateApp',methods=['POST','GET'])
# def updateApp():
#     if request.method == 'POST':
#         id = request.form['id']
#         datetime = request.form['datetime']
#         custid = request.form['custid']
#         trmntid = request.form['trmntid']
#         cur = mysql.connection.cursor()
#         cur.execute("""
#         UPDATE appointment
#         SET appDateTime=%s, custID=%s, trmntID=%s 
#         WHERE appID=%s
#         """, (datetime, custid, trmntid, id))
#         mysql.connection.commit()
#         flash("Data Updated Successfully")
#         return redirect(url_for('manageAppmnt'))

# @app.route('/deleteApp/<string:id_data>', methods=['POST','GET'])
# def deleteApp(id_data):
#     cur = mysql.connection.cursor()
#     cur.execute("DELETE FROM appointment WHERE appID=%s", (id_data))
#     mysql.connection.commit()
#     flash("Record Has Been Deleted Successfully")
#     return redirect(url_for('manageAppmnt'))

#endregion

@app.route('/loginPage')
def loginPage():

		return render_template('loginPage.html')

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