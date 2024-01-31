import requests
from flask import Flask, jsonify, render_template , request, redirect, session, url_for, flash, redirect
from urllib.parse import urljoin
from werkzeug.utils import secure_filename
from flask_session import Session
from sqlite3 import Error

from datetime import date, datetime, timedelta
import sqlite3
import os
from flask_login import LoginManager, login_required, UserMixin, login_user, logout_user

import hashlib
from flask_simple_crypt import SimpleCrypt


UPLOAD_FOLDER = '\static\attachments'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}

app = Flask (__name__)
sess = Session()

SITE_KEY = '6LfaMWEpAAAAAAoCokW7UkLPMxpAsNjRD6nzJmCJ'
SECRET_KEY = '6LfaMWEpAAAAAPB932G61JU7Avky7STYGY8DD8UW'
VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'loginPage'
app.secret_key = 'flash_message'
app.config['FSC_EXPANSION_COUNT'] = 2048
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

cipher = SimpleCrypt()
cipher.init_app(app)


# Dictionary to store login attempts
login_attempts = {}

# Lockout duration
LOCKOUT_DURATION = timedelta(minutes=2)

#region --------------Database Start--------------------

# def formValidation(currVal, AcqVal, Quant, desc):
#     if float(currVal)>=1 and float(AcqVal)>=1 and float(Quant)>=1 and desc.isalnum():
#         return True
#     else:
#         return False

def formValidation(currVal, AcqVal, Quant):
    if float(currVal)>=1 and float(AcqVal)>=1 and float(Quant)>=1:
        return True
    else:
        return False
    
def decrypt(tupple, table):
    if(table=="buffer"):
        buffList = list(tupple)
        buffList[7] = cipher.decrypt(buffList[7]).decode('utf8')
        buffList[8] = cipher.decrypt(buffList[8]).decode('utf8')
        buffList[10] = cipher.decrypt(buffList[10]).decode('utf8')
        buffList[14] = cipher.decrypt(buffList[14]).decode('utf8')
        buffList[15] = cipher.decrypt(buffList[15]).decode('utf8')
        
        decryptedTupple = tuple(buffList)
        return decryptedTupple
    elif(table=="assets"):
        print(tupple)
        assList = list(tupple)
        print(assList)
        assList[5] = cipher.decrypt(assList[5]).decode('utf8')
        assList[6] = cipher.decrypt(assList[6]).decode('utf8')
        assList[8] = cipher.decrypt(assList[8]).decode('utf8')
        assList[12] = cipher.decrypt(assList[12]).decode('utf8')
        assList[13] = cipher.decrypt(assList[13]).decode('utf8')
        
        decryptedTupple = tuple(assList)
        return decryptedTupple
    elif(table=="adminBuff"):
        print("------------------WEEEE---------------")
        print(tupple)
        a = [list(item) for item in tupple] 
        count = 0
        for row in a:

            a[count][7] = cipher.decrypt(a[count][7]).decode("utf8")
            count = count + 1
        decryptedA = tuple(a)
        return decryptedA
    elif(table=="userBuff"):
        print("------------------WEEEE---------------")
        print(tupple)
        a = [list(item) for item in tupple] 
        count = 0
        for row in a:
            a[count][4] = cipher.decrypt(a[count][4]).decode("utf8")
            count = count + 1
        decryptedA = tuple(a)
        return decryptedA
        
        
        

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

# - User Table -
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

# - Admin Table -
admin_creation_query = '''
CREATE TABLE IF NOT EXISTS admin (
adminID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
email TEXT NOT NULL,
password TEXT NOT NULL
);
'''
cur.execute(admin_creation_query)

# - User Asset Table -
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

# - Buffer Table -
buffer_creation_query = '''
CREATE TABLE IF NOT EXISTS buffer (
ReviewID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
ReviewType TEXT NOT NULL,
AssetID INTEGER,
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
cur.execute(buffer_creation_query)

#endregion ----------------------------------------------

class User(UserMixin):
    def __init__(self, id, fullname, pswrd):
        self.id = id
        self.fullname = fullname
        self.pswrd = pswrd

@login_manager.user_loader
def load_user(user_id):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE userID=?", (user_id,))
    user = cur.fetchone()
    if user:
        return User(*user)
    return None

@login_manager.user_loader
def load_user(admin_id):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM admin WHERE adminID=?", (admin_id,))
    user = cur.fetchone()
    if user:
        return User(*user)
    return None


def hash_route(route_name):
    route_hash = hashlib.sha256(route_name.encode()).hexdigest()
    return "/"+route_hash[:8]  # Take the first 8 characters of the hash as the obfuscated route


#-----------Go to Login age-----------
@app.route('/')
def start():

    return render_template('loginPage.html')

#-----------Admin Page-----------

@app.route(hash_route('/adminPage'))

@login_required
def adminPage():
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT a.`ReviewID`, a.`ReviewType`,  a.`AssetID`, u.`fullname`, a.`dateOfApp`, a.`AssDecType`, a.`AssDecCat`, a.`Description`
            FROM `buffer` a
            JOIN `user` u ON a.`userID` = u.`userID`
            WHERE a.`Status` = "Pending"
        """)
        pending = cur.fetchall()
        cur.execute("""
            SELECT a.`ReviewID`, a.`ReviewType`,  a.`AssetID`, u.`fullname`, a.`dateOfApp`, a.`AssDecType`, a.`AssDecCat`, a.`Description`
            FROM `buffer` a
            JOIN `user` u ON a.`userID` = u.`userID`
            WHERE a.`Status` = "Approved"
        """)
        completed = cur.fetchall()
        cur.close()

    except:
        flash("An Exception Occured!")

    return render_template('adminpage.html', review=decrypt(pending,"adminBuff"), completed=decrypt(completed,"adminBuff"))

#-----------Home-----------

@app.route(hash_route('/home'))
@login_required
def index():

    try:
        user = session.get('username', None)
        print(user)
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("""SELECT `AssetID`,`dateOfApp`,`AssDecType`,`AssDecCat`,`Description`, `Status` FROM `assets` WHERE `userID` = ? """,(user,))
        data = cur.fetchall()
        cur.execute("""SELECT `ReviewID`,`dateOfApp`,`AssDecType`,`AssDecCat`,`Description`, `Status` FROM `buffer` WHERE `userID` = ? AND (`Status` = "Pending" OR `Status` = "Rejected") """,(user,))
        pendingdata = cur.fetchall()
        cur.close()
        return render_template('home.html', appnts=decrypt(data,"userBuff"), usrnm = user, pendingdata=decrypt(pendingdata,"userBuff"))
    except:
        flash("An Exception Occured!")

    return render_template('loginPage.html')

#-----------View Assets-----------
@app.route('/viewAss/<string:assID>',methods=['POST','GET'])
@login_required
def viewAss(assID):
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("""SELECT * FROM `assets` WHERE `AssetID` = ? """,(assID,))
        rowdata = cur.fetchone()
        cur.close
        return render_template('viewAss.html', rowdata=decrypt(rowdata, "assets"))
    except:
        flash("An Exception Occured!")
        return render_template('loginPage.html')

#-----------View Buffer-----------
@app.route('/viewBuffer/<string:assID>',methods=['POST','GET'])
@login_required
def viewBuffer(assID):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("""SELECT * FROM `buffer` WHERE `ReviewID` = ? """,(assID,))
    rowdata = cur.fetchone()
    print(rowdata)
    
    newRowData = decrypt(rowdata, "buffer")
    
    cur.close
    return render_template('viewBuffer.html', rowdata=newRowData)

#-----------View Buffer-----------
@app.route('/viewComplete/<string:assID>',methods=['POST','GET'])
@login_required
def viewComplete(assID):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("""SELECT * FROM `buffer` WHERE `ReviewID` = ? """,(assID,))
    rowdata = cur.fetchone()
    cur.close
    return render_template('viewComplete.html', rowdata=decrypt(rowdata,"buffer"))

#-----------View Application-----------
@app.route('/viewApplication/<string:assID>',methods=['POST','GET'])
@login_required
def viewApplciation(assID):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("""SELECT * FROM `buffer` WHERE `ReviewID` = ? """,(assID,))
    rowdata = cur.fetchone()
    cur.close
    return render_template('viewApplication.html', rowdata=decrypt(rowdata,"buffer"))

#-----------Insert Assets-----------
@app.route('/insertAss', methods = ['POST','GET'])
@login_required
def insertAss():
    if request.method == "POST":
        secret_response = request.form['g-recaptcha-response']

        verify_response = requests.post(url=f'{VERIFY_URL}?secret={SECRET_KEY}&response={secret_response}').json()

        if verify_response['success'] == False or verify_response['score'] < 0.5:


            # Process the form data here
            assDecType = request.form['assType']
            assDecCat = request.form['assCat']
            assDec = request.form['assDec']
            assAddr = request.form['assAdd1'] + ", " + request.form['assAdd2'] + ", " + request.form['assPostCode'] + "," + request.form['assCity'] + ", " + request.form['assState'] + ", Malaysia"
            assOwner = request.form['assOwner']
            assCert = request.form['assCert']
            assDateOwn = request.form['assDateOwn']
            assQuantity = request.form['assQuantity']
            assMeasurement = request.form['assMeasurement']
            assAcqVal = request.form['assAcqVal']
            assCurVal = request.form['assCurVal']
            assAcq = request.form['assAcq']
            attchmnt = request.files['file']
            filename = secure_filename(attchmnt.filename)
            
            print(assDec)
            print(assDec.isalnum())
            print(assDec.isalnum)


            if formValidation(assCurVal, assAcqVal, assQuantity):
                conn = create_connection()
                cur = conn.cursor()
                
                assDec = cipher.encrypt(assDec)
                assAddr = cipher.encrypt(assAddr)
                assCert = cipher.encrypt(assCert)
                assAcqVal = cipher.encrypt(assAcqVal)
                assCurVal = cipher.encrypt(assCurVal)
                
                cur.execute ("INSERT INTO buffer (reviewType, userID, dateOfApp, AssDecType, AssDecCat, Description, Address, Owner, RegCertNo, DateOfOwnership, Quantity, Measurement, AssAcqVal, CurrAssVal, AcqMethod, attachment, status, review) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ("Addition", session.get('username', None), str(date.today()), assDecType, assDecCat, assDec, assAddr, assOwner, assCert, assDateOwn, assQuantity, assMeasurement, assAcqVal, assCurVal, assAcq, filename, "Pending", ""))
                conn.commit()

                os.makedirs('static/attachment', exist_ok=True)  # Create the directory if it doesn't exist
                attchmnt.save(os.path.join('static/attachment', filename))

                flash("Request to add asset sent!")
            else:   
                flash("Check your inputs!")
        else:
            flash("Data Not Inserted!")
        return redirect(url_for ('index'))
    else:
        return redirect(url_for ('index'))

#-----------Login Page-----------
@app.route('/loginPage')
def loginPage():

		return render_template('loginPage.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Check if the user is still locked out
        if 'lockout_end_time' in session:
            remaining_time = session['lockout_end_time'] - datetime.now()
            if remaining_time > timedelta():
                return '<script>alert("Too many login attempts. Please try again later."); window.location="/";</script>'
            else:
                # Clear lockout session variables
                session.pop('lockout_end_time', None)
                session.pop('lockout_email', None)

        return render_template('login.html')  # Assuming you have a login page template

    elif request.method == 'POST':
        # Get the reCAPTCHA response from the form submission
        recaptcha_response = request.form.get('g-recaptcha-response')

        # Verify the reCAPTCHA response with the reCAPTCHA API
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': '6LfWL2ApAAAAAHLENlTceAIFXsyuf7XKAjGAldU8',
                'response': recaptcha_response
            }
        )
        result = response.json()

        # Check if the reCAPTCHA was successful
        if not result['success']:
            return redirect(url_for('loginPage'))

        email = request.form['username']
        password = request.form['password']

        # Get the user from the database
        conn = create_connection()
        cur = conn.cursor()
        cur.execute('SELECT `userID`, `email`, `password` FROM `user` WHERE `email` = ? AND `password` = ?', (email, password))
        user = cur.fetchone()
        print("----------------- USER DEBUG ----------------")
        print(user)
        print("----------------- USER DEBUG ----------------")
        cur.execute('SELECT `adminID`, `email`, `password` FROM `admin` WHERE `email` = ? AND `password` = ?', (email, password))
        admin = cur.fetchone()
        cur.close()

        if user:
            session['username'] = user[0]
            session['Log'] = True
            session['userType'] = "user"
            login_user(User(*user))
            return redirect(url_for('index'))
        elif admin:
            session['username'] = admin[0]
            session['Log'] = True
            session['userType'] = "admin"
            login_user(User(*admin))
            return redirect(url_for('adminPage'))
        else:
            # Increment login attempts for the given email
            login_attempts[email] = login_attempts.get(email, []) + [datetime.now()]

            # Check if the user has exceeded the login attempt limit within a minute
            if len(login_attempts[email]) > 3:
                # Check if the earliest attempt is within the lockout duration
                if datetime.now() - login_attempts[email][0] < LOCKOUT_DURATION:
                    # Set lockout session variables
                    session['lockout_end_time'] = datetime.now() + LOCKOUT_DURATION
                    session['lockout_email'] = email
                    return redirect(url_for('login'))  # Redirect to GET /login route
                else:
                    # Clear login attempts if the lockout duration has passed
                    login_attempts[email] = [datetime.now()]
            else:
                return '<script>alert("Incorrect email or password."); window.location="/";</script>'

#-----------Update Assets-----------
@app.route('/updateAss/<string:assID>', methods=['GET'])
@login_required
def updateAss(assID):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("""SELECT * FROM `assets` WHERE `AssetID` = ? AND `userID` = ?""", (assID, session.get('username', None)))
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
        'Description': cipher.decrypt(rowdata[5]).decode("utf8"),
        'Address': cipher.decrypt(rowdata[6]).decode("utf8"),  # You may need to split the address into parts as needed
        'Owner': rowdata[7],
        'RegCertNo': cipher.decrypt(rowdata[8]).decode("utf8"),
        'DateOfOwnership': rowdata[8],
        'Quantity': rowdata[10],
        'Measurement': rowdata[11],
        'AssAcqVal': cipher.decrypt(rowdata[12]).decode("utf8"),
        'CurrAssVal': cipher.decrypt(rowdata[13]).decode("utf8"),
        'AcqMethod': rowdata[14],
        'Attachment': rowdata[15],
        'Review': rowdata[16],
        'Status': rowdata[17]

    }

    return render_template('updateAss.html', asset_data=asset_data)

@app.route('/performUpdateAss/<string:assID>', methods=['POST'])
@login_required
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
    attachment = request.files['attachment']
    filename = secure_filename(attachment.filename)
    review = request.form['review']
    status = "Pending"

    if formValidation(assCurVal, assAcqVal, assQuantity):
    # Update the corresponding asset in the database
        conn = create_connection()
        cur = conn.cursor()
        
        assDec = cipher.encrypt(assDec)
        assAddr = cipher.encrypt(assAddr)
        assCert = cipher.encrypt(assCert)
        assAcqVal = cipher.encrypt(assAcqVal)
        assCurVal = cipher.encrypt(assCurVal)
        
        cur.execute ("UPDATE assets SET status = ? WHERE AssetID = ?", (status, assID))
        conn.commit()
        cur.execute ("INSERT INTO buffer (reviewType, AssetID, userID, dateOfApp, AssDecType, AssDecCat, Description, Address, Owner, RegCertNo, DateOfOwnership, Quantity, Measurement, AssAcqVal, CurrAssVal, AcqMethod, attachment, status, review) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ("Edit", assID, session.get('username', None), str(date.today()), assDecType, assDecCat, assDec, assAddr, assOwner, assCert, assDateOwn, assQuantity, assMeasurement, assAcqVal, assCurVal, assAcq, filename, status, review))
        conn.commit()

        os.makedirs('static/attachment', exist_ok=True)  # Create the directory if it doesn't exist
        attachment.save(os.path.join('static/attachment', filename))

        flash("Update Request Sent!")
    else:
        flash("Check your inputs!")

    # Redirect to the view page for the updated asset or any other appropriate page
    return redirect(url_for('index', assID=assID))

#----------Approve Request---------
@app.route('/processApp/<string:appID>/<string:type>', methods=['POST','GET'])
@login_required
def processApp(appID,type):
    print("It has eneterd")

    if(request.form['action']=="Approve"):
        if(type=="Addition"):

            # Update the corresponding asset in the database
            conn = create_connection()
            cur = conn.cursor()
            cur.execute("""SELECT * FROM `buffer` WHERE `ReviewID` = ? """,(appID,))
            bufferData = cur.fetchone()
            cur.close()

            print("Got the info")
            review = request.form['review']

            conn = create_connection()
            cur = conn.cursor()
            cur.execute ("INSERT INTO assets (userID, dateOfApp, AssDecType, AssDecCat, Description, Address, Owner, RegCertNo, DateOfOwnership, Quantity, Measurement, AssAcqVal, CurrAssVal, AcqMethod, attachment, status, review) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (bufferData[3], bufferData[4], bufferData[5], bufferData[6], bufferData[7], bufferData[8], bufferData[9], bufferData[10], bufferData[11], bufferData[12], bufferData[13], bufferData[14], bufferData[15], bufferData[16], bufferData[17], "Approved", review))
            conn.commit()
            cur.close()

            print("Sent info")
            conn = create_connection()
            cur = conn.cursor()
            cur.execute ("UPDATE buffer SET status = ?, review =? where ReviewID = ?", ("Approved", review, appID))
            conn.commit()
            cur.close()


            conn = create_connection()
            cur = conn.cursor()


            flash("Asset Added Successfully")

            # Redirect to the view page for the updated asset or any other appropriate page
            return redirect(url_for('adminPage'))

        elif(type=="Edit"):
            # Update the corresponding asset in the database
            conn = create_connection()
            cur = conn.cursor()
            cur.execute("""SELECT * FROM `buffer` WHERE `ReviewID` = ? """,(appID,))
            bufferData = cur.fetchone()
            cur.close()

            print("Got the info")
            review = request.form['review']

            conn = create_connection()
            cur = conn.cursor()
            cur.execute ("UPDATE assets SET userID = ?, dateOfApp = ?, AssDecType = ?, AssDecCat = ?, Description = ?, Address = ?, Owner = ?, RegCertNo = ?, DateOfOwnership = ?, Quantity = ?, Measurement = ?, AssAcqVal = ?, CurrAssVal = ?, AcqMethod = ?, attachment = ?, status = ?, review = ? WHERE AssetID = ?", (bufferData[3], bufferData[4], bufferData[5], bufferData[6], bufferData[7], bufferData[8], bufferData[9], bufferData[10], bufferData[11], bufferData[12], bufferData[13], bufferData[14], bufferData[15], bufferData[16], bufferData[17], "Approved", review, bufferData[2]))
            conn.commit()
            cur.close()

            print("Sent info")
            conn = create_connection()
            cur = conn.cursor()
            cur.execute ("UPDATE buffer SET status = ?, review =? where ReviewID = ?", ("Approved", review, appID))
            conn.commit()
            cur.close()

            flash("Asset Updated Successfully")

            # Redirect to the view page for the updated asset or any other appropriate page
            return redirect(url_for('adminPage'))
        elif(type=="Deletion"):

            conn = create_connection()
            cur = conn.cursor()
            cur.execute("""SELECT * FROM `buffer` WHERE `ReviewID` = ? """,(appID,))
            bufferData = cur.fetchone()
            cur.close()

            print("Got the info")
            review = request.form['review']

            conn = create_connection()
            cur = conn.cursor()
            cur.execute ("DELETE FROM assets WHERE assetID = ?", (bufferData[2],))
            conn.commit()
            cur.close()

            print("Sent info")
            conn = create_connection()
            cur = conn.cursor()
            cur.execute ("UPDATE buffer SET status = ?, review =? where ReviewID = ?", ("Approved", review, appID))
            conn.commit()
            cur.close()

            return redirect(url_for('adminPage'))
        else:
            flash("Something went wrong")
            print("SHITTTTTTTTTT")
            return redirect(url_for('adminPage'))
    if(request.form['action']=="Reject"):
        if(type=="Addition" or type=="Edit" or type=="Deletion"):

            # Update the corresponding asset in the database
            conn = create_connection()
            cur = conn.cursor()
            cur.execute("""SELECT * FROM `buffer` WHERE `ReviewID` = ? """,(appID,))
            bufferData = cur.fetchone()
            cur.close()

            print("Got the info")
            review = request.form['review']

            print("Sent info")
            conn = create_connection()
            cur = conn.cursor()
            cur.execute ("UPDATE buffer SET Status = ?, review =? where ReviewID = ?", ("Rejected", review, appID))
            
            cur.execute("""SELECT `AssetID` FROM `buffer` WHERE `ReviewID` = ? """,(appID,))
            ResetAsset = cur.fetchone()
            if ResetAsset != None:
                cur.execute ("UPDATE assets SET Status = ? WHERE AssetID = ?", ("Approved", ResetAsset[0]))
            conn.commit()
            cur.close()


            conn = create_connection()
            cur = conn.cursor()


            flash("Asset Reviewed Successfully")

            # Redirect to the view page for the updated asset or any other appropriate page
            return redirect(url_for('adminPage'))

        else:
            flash("Something went wrong")
            print("SHITTTTTTTTTT")
            return redirect(url_for('adminPage'))
    else:
        flash("Something went wrong")
        print("SHITTTTTTTTTT")
        return redirect(url_for('adminPage'))

#----------Reject Request---------
@app.route('/rejectApp/<string:appID>/<string:type>', methods=['POST','GET'])
@login_required
def rejectApp(appID,type):
    print("It has eneterd")
    if(type=="Addition" or type=="Edit" or type=="Deletion"):

        # Update the corresponding asset in the database
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("""SELECT * FROM `buffer` WHERE `ReviewID` = ? """,(appID,))
        bufferData = cur.fetchone()
        cur.close()

        print("Got the info")
        review = request.form['review']

        print("Sent info")
        conn = create_connection()
        cur = conn.cursor()
        cur.execute ("UPDATE buffer SET Status = ?, review =? where ReviewID = ?", ("Rejected", review, appID))
        conn.commit()
        cur.close()


        conn = create_connection()
        cur = conn.cursor()


        flash("Asset Reviewed Successfully")

        # Redirect to the view page for the updated asset or any other appropriate page
        return redirect(url_for('adminPage'))

    else:
        flash("Something went wrong")
        print("SHITTTTTTTTTT")
        return redirect(url_for('adminPage'))

#----------Approve Update----------
@app.route('/ApproveUpdate/<string:appID>', methods=['POST'])
@login_required
def ApproveUpdate(appID):
    # Update the corresponding asset in the database
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("""SELECT * FROM `buffer` WHERE `ReviewID` = ? """,(appID,))
    bufferData = cur.fetchone()
    cur.close()

    print("Got the info")
    review = request.form['review']

    conn = create_connection()
    cur = conn.cursor()
    cur.execute ("UPDATE assets SET userID = ?, dateOfApp = ?, AssDecType = ?, AssDecCat = ?, Description = ?, Address = ?, Owner = ?, RegCertNo = ?, DateOfOwnership = ?, Quantity = ?, Measurement = ?, AssAcqVal = ?, CurrAssVal = ?, AcqMethod = ?, attachment = ?, status = ?, review = ? WHERE AssetID = ?", (bufferData[3], bufferData[4], bufferData[5], bufferData[6], bufferData[7], bufferData[8], bufferData[9], bufferData[10], bufferData[11], bufferData[12], bufferData[13], bufferData[14], bufferData[15], bufferData[16], bufferData[17], "Approved", review, bufferData[2]))
    conn.commit()
    cur.close()

    print("Sent info")
    conn = create_connection()
    cur = conn.cursor()
    cur.execute ("UPDATE buffer SET status = ?, review =? where ReviewID = ?", ("Approved", review, appID))
    conn.commit()
    cur.close()


    conn = create_connection()
    cur = conn.cursor()


    flash("Asset Updated Successfully")

    flash("Asset Updated Successfully")

    # Redirect to the view page for the updated asset or any other appropriate page
    return redirect(url_for('adminPage'))

#-----------Delete Asset-----------
@app.route('/deleteAss/<string:assID>', methods=['GET'])
@login_required
def deleteAss(assID):
    conn = create_connection()
    cur = conn.cursor()

    # Fetch asset data before deletion for confirmation or display
    cur.execute("""SELECT * FROM `assets` WHERE `AssetID` = ? AND `userID` = ?""", (assID, session.get('username', None)))
    rowdata = cur.fetchone()

    if rowdata:
        # Delete the asset
        # Update the corresponding asset in the database
        cur.execute ("UPDATE assets SET status = ? WHERE AssetID = ?", ("Pending", assID))
        conn.commit()
        cur.execute ("INSERT INTO buffer (reviewType, AssetID, userID, dateOfApp, AssDecType, AssDecCat, Description, Address, Owner, RegCertNo, DateOfOwnership, Quantity, Measurement, AssAcqVal, CurrAssVal, AcqMethod, attachment, status, review) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ("Deletion", assID, session.get('username', None), rowdata[2], rowdata[3], rowdata[4], rowdata[5], rowdata[6], rowdata[7], rowdata[8], rowdata[9], rowdata[10], rowdata[11], rowdata[12], rowdata[13], rowdata[14], rowdata[15], "Pending", rowdata[16]))
        conn.commit()
        # cur.execute("""DELETE FROM `assets` WHERE `AssetID` = ?""", (assID,))
        # conn = create_connection()
        cur = conn.cursor()
        cur.close()

        flash("Deletion request sent")
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
@login_required
def logout():
    session.clear()
    print("--------------Attempt to logout------------")
    logout_user()
    print(logout_user())
    print("---------------------logout-------------------")
    return redirect(url_for('loginPage'))

if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    sess.init_app(app)
    app.run(debug=True)
    