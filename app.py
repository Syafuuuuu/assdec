from datetime import date
from flask import Flask, jsonify, render_template , request, redirect, session, url_for, flash, redirect
from urllib.parse import urljoin
from werkzeug.utils import secure_filename
from sqlite3 import Error
import sqlite3
import os

UPLOAD_FOLDER = '\static\attachments'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}

app = Flask (__name__)
app.secret_key = 'flash_message'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = "flash_message"

#region --------------Database Start--------------------
# --- Database Connection ----
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('static/db/user.db')  # create a database connection
        return conn
    except Error as e:
        print(e)

    return conn

conn = create_connection()
cur = conn.cursor()

# --- Table Creation ---

# - Define the table creation query -
user_creation_query = '''
CREATE TABLE IF NOT EXISTS user (
userID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
email TEXT NOT NULL,
password TEXT NOT NULL,
fullname TEXT NOT NULL,
age INTEGER NOT NULL
);
'''
cur.execute(user_creation_query)

# - Define the table creation query -
admin_creation_query = '''
CREATE TABLE IF NOT EXISTS admin (
adminID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
email TEXT NOT NULL,
password TEXT NOT NULL
);
'''
cur.execute(admin_creation_query)

# - Define the table creation query -
asset_creation_query = '''
CREATE TABLE IF NOT EXISTS assets (
AssetID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
UserID INTEGER NOT NULL,
DateOfApp DATE NOT NULL,
AssDecType TEXT NOT NULL,
AssDecCat TEXT NOT NULL,
Description TEXT NOT NULL,
Address TEXT NOT NULL,
Owner TEXT NOT NULL,
RegCertNo TEXT NOT NULL,
DateOfOwnership DATE NOT NULL,
Quantity INTEGER NOT NULL,
Measurement TEXT NOT NULL,
AssAcqVAl REAL NOT NULL,
CurrAssVal REAL NOT NULL,
AcqMethod TEXT NOT NULL,
Attachment TEXT NOT NULL,
Review TEXT NOT NULL,
Status TEXT NOT NULL
);
'''
cur.execute(asset_creation_query)



#endregion ----------------------------------------------

#-----------Go to Login age-----------
@app.route('/')
def start():

    return render_template('loginPage.html')

#-----------Admin Page-----------
@app.route('/adminPage')
def adminPage():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.`AssetID`, a.`dateOfApp`, a.`AssDecType`, a.`AssDecCat`, a.`Description`, u.`fullname`
        FROM `assets` a
        JOIN `user` u ON a.`userID` = u.`userID`
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
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("""SELECT `AssetID`,`dateOfApp`,`AssDecType`,`AssDecCat`,`Description` FROM `assets` WHERE `userID` = ? """,(user,))
    data = cur.fetchall()
    cur.close()

    return render_template('home.html', appnts=data, usrnm = user)

#-----------View Assets-----------
@app.route('/viewAss/<string:assID>',methods=['POST','GET'])
def viewAss(assID):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("""SELECT * FROM `assets` WHERE `AssetID` = ? """,(assID,))
    rowdata = cur.fetchone()
    cur.close
    return render_template('viewAss.html', rowdata=rowdata)

#-----------Insert Assets-----------
@app.route('/insertAss', methods = ['POST','GET'])
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
        attchmnt = request.files['file']
        print("Filenmae Below")
        print(attchmnt)
        print(attchmnt.filename)
        print("filename above")
        
        filename = secure_filename(attchmnt.filename)
        print("Filenmae Below")
        print(filename)
        print("filename above")

        conn = create_connection()
        cur = conn.cursor()
        cur.execute ("INSERT INTO assets (userID, dateOfApp, AssDecType, AssDecCat, Description, Address, Owner, RegCertNo, DateOfOwnership, Quantity, Measurement, AssAcqVal, CurrAssVal, AcqMethod, attachment, status, review) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (session.get('username', None), str(date.today()), assDecType, assDecCat, assDec, assAddr, assOwner, assCert, assDateOwn, assQuantity, assMeasurement, assAcqVal, assCurVal, assAcq, filename, "pending", ""))
        conn.commit()
        
        os.makedirs('static/attachment', exist_ok=True)  # Create the directory if it doesn't exist
        attchmnt.save(os.path.join('static/attachment', filename))
        
        flash("Data Inserted Successfully")
        return redirect(url_for ('index'))

#-----------Login Page-----------
@app.route('/loginPage')
def loginPage():

		return render_template('loginPage.html')

#-----------Login Process-------------------
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']
        conn = create_connection()
        cur = conn.cursor()
        cur.execute('SELECT `userID`,`email`,`password` FROM `user` WHERE `email`= ? AND `password`=?', (email,password))
        usr = cur.fetchone()
        cur.execute('SELECT `adminID`, `email`,`password` FROM `admin` WHERE `email`= ? AND `password`=?', (email,password))
        admin = cur.fetchone()
        cur.close()
        if usr:
            session['username'] = usr[0]
            session['Log'] = True
            return redirect(url_for('index'))
        elif admin:
            session['username'] = admin[0]
            session['Log'] = True
            return redirect(url_for('adminPage'))
        else:
            return '<script>alert("Incorrect email or password."); window.location="/";</script>'

#-----------Update Assets-----------
@app.route('/updateAss/<string:assID>', methods=['GET'])
def updateAss(assID):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("""SELECT * FROM `assets` WHERE `AssetID` = ? AND `username` = ?""", (assID, session.get('username', None)))
    rowdata = cur.fetchone()
    cur.close()

    # Check if the asset data is fetched
    if not rowdata:
        flash("Error: Asset not found or you don't have permission to update.")
        return redirect(url_for('index'))  # Redirect to the home page or another appropriate page

    # Prepare the data in a dictionary format
    asset_data = {
        'AssetID': rowdata[0],
        'AssDecType': rowdata[3],
        'AssDecCat': rowdata[4],
        'Description': rowdata[5],
        'Address': rowdata[6],  # You may need to split the address into parts as needed
        'Owner': rowdata[7],
        'RegCertNo': rowdata[8],
        'DateOfOwnership': rowdata[8],
        'Quantity': rowdata[10],
        'Measurement': rowdata[11],
        'AssAcqVal': rowdata[12],
        'CurrAssVal': rowdata[13],
        'AcqMethod': rowdata[14]
    }

    return render_template('updateAss.html', asset_data=asset_data)


@app.route('/performUpdateAss/<string:assID>', methods=['POST'])
def performUpdateAss(assID):
    # Extract updated values from the form submission
    assDecType = request.form['assType']
    assDecCat = request.form['assCat']
    assDec = request.form['assDec']
    assAddr = request.form['assAddr']
    assOwner = request.form['assOwner']
    assCert = request.form['assCert']
    assDateOwn = request.form['assDateOwn']
    assQuantity = request.form['assQuantity']
    assMeasurement = request.form['assMeasurement']
    assAcqVal = request.form['assAcqVal']
    assCurVal = request.form['assCurVal']
    assAcq = request.form['assAcq']

    # Update the corresponding asset in the database
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE `assets`
        SET AssDecType=?, AssDecCat=?, Description=?, Address=?, Owner=?, RegCertNo=?,
            DateOfOwnership=?, Quantity=?, Measurement=?, AssAcqVal=?, CurrAssVal=?, AcqMethod=?
            WHERE AssetID=? AND `username` = ?
    """, (assDecType, assDecCat, assDec, assAddr, assOwner, assCert, assDateOwn, assQuantity, assMeasurement, assAcqVal, assCurVal, assAcq, assID, session.get('username', None)))
    conn.commit()
    cur.close()

    flash("Asset Updated Successfully")

    # Redirect to the view page for the updated asset or any other appropriate page
    return redirect(url_for('index', assID=assID))  

#-----------Delete Asset-----------
@app.route('/deleteAss/<string:assID>', methods=['GET'])
def deleteAss(assID):
    conn = create_connection()
    cur = conn.cursor()

    # Fetch asset data before deletion for confirmation or display
    cur.execute("""SELECT * FROM `assets` WHERE `AssetID` = ? AND (`username` = ? OR 1 = ?)""", (assID, session.get('username', None), session.get('is_admin', 0)))
    rowdata = cur.fetchone()

    if rowdata:
        # Delete the asset
        cur.execute("""DELETE FROM `assets` WHERE `AssetID` = ?""", (assID,))
        conn = create_connection()
        cur = conn.cursor()
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
            conn = create_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM user WHERE username = ?", (username,))
            existing_user = cur.fetchone()
            cur.close()

            if existing_user:
                flash("Username already exists. Please choose a different username.")
                return redirect(url_for('registerUser'))

            # Insert new user into the database
            conn = create_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO `user` (`username`, `password`, `fullname`, `age`, `is_admin`) VALUES (?, ?, ?, ?, ?)",
                (username, password, fullname, age, is_admin)
            )
            conn.commit()
            cur.close()

            return redirect(url_for('registerUser'))  # Redirect to admin page after registration

        except Exception as e:
            print(f"Error during user registration: {str(e)}")
            return redirect(url_for('registerUser'))

    return render_template('registeruser.html')     

if __name__ == '__main__':
    app.run(debug=True)