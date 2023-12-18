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

#-----------Admin Page-----------
@app.route('/adminPage')
def adminPage():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT a.`AssetID`, a.`dateOfApp`, a.`AssDecType`, a.`AssDecCat`, a.`Description`, u.`fullname`
        FROM `assets` a
        JOIN `user` u ON a.`username` = u.`username`
    """)
    data = cur.fetchall()
    cur.close()

    # Group assets by fullname
    assets_by_fullname = {}
    for row in data:
        fullname = row[5]  # Assuming fullname is at index 5
        if fullname not in assets_by_fullname:
            assets_by_fullname[fullname] = []
        assets_by_fullname[fullname].append(row)

    return render_template('adminpage.html', assets_by_fullname=assets_by_fullname)





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
    cur = mysql.connection.cursor()
    cur.execute("""SELECT * FROM `assets` WHERE `AssetID` = %s """,(assID,))
    rowdata = cur.fetchone()
    cur.close
    return render_template('viewAss.html', rowdata=rowdata)

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

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute('SELECT `username`,`password`,`is_admin` FROM `user` WHERE `username`= %s AND `password`=%s', (username,password))
        usr = cur.fetchone()
        cur.close()
        if usr:
            session['username'] = username
            session['Log'] = True
            if usr[2] == 1: # check if user is admin
                return redirect(url_for('adminPage'))
            else:
                return redirect(url_for('index'))
        else:
            return '<script>alert("Incorrect username or password."); window.location="/";</script>'
        
#-----------Delete Asset-----------
@app.route('/deleteAss/<string:assID>', methods=['GET'])
def deleteAss(assID):
    cur = mysql.connection.cursor()

    # Fetch asset data before deletion for confirmation or display
    cur.execute("""SELECT * FROM `assets` WHERE `AssetID` = %s AND (`username` = %s OR 1 = %s)""", (assID, session.get('username', None), session.get('is_admin', 0)))
    rowdata = cur.fetchone()

    if rowdata:
        # Delete the asset
        cur.execute("""DELETE FROM `assets` WHERE `AssetID` = %s""", (assID,))
        mysql.connection.commit()
        cur.close()

        flash("Asset Deleted Successfully")
    else:
        flash("Error: You don't have permission to delete this asset.")

    # Determine the redirect page based on the user's role
    if session.get('is_admin', 0):
        redirect_page = 'adminPage'
    else:
        redirect_page = 'index'

    # Optionally, you can redirect to a page or display a confirmation message.
    # In this example, I'm redirecting to the appropriate page based on the user's role.
    return redirect(url_for(redirect_page))

        
#-----------LogOut User-----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('loginPage'))

@app.route('/registerUser', methods=['GET', 'POST'])
def registerUser():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        age = request.form['age']
        is_admin = 'is_admin' in request.form

        try:
            # Check if the username already exists
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM user WHERE username = %s", (username,))
            existing_user = cur.fetchone()
            cur.close()

            if existing_user:
                flash("Username already exists. Please choose a different username.")
                return redirect(url_for('registerUser'))

            # Insert new user into the database
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO `user` (`username`, `password`, `fullname`, `age`, `is_admin`) VALUES (%s, %s, %s, %s, %s)",
                (username, password, fullname, age, is_admin)
            )
            mysql.connection.commit()
            cur.close()

            flash("User Registered Successfully")
            return redirect(url_for('registerUser'))  # Redirect to admin page after registration

        except Exception as e:
            print(f"Error during user registration: {str(e)}")
            flash("Error during user registration. Please try again.")
            return redirect(url_for('registerUser'))

    return render_template('registeruser.html')

if __name__ == '__main__':
    app.run(debug=True)
