import datetime
import os

import mysql.connector
from mysql.connector import Error

#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect, flash, send_from_directory
from werkzeug.utils import secure_filename
import pymysql.cursors # for interacting with database


UPLOAD_FOLDER = '/Users/qinyingchen/Desktop/Databases-Project/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

#Initialize the app from Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       port = 8889,
                       user='root',
                       password='root',
                       db='FinstagramDB',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
    return render_template('index.html')

#Define route for login
@app.route('/login')
def login():
    return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
    return render_template('register.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM Person WHERE username = %s and password = %s'
    cursor.execute(query, (username, password))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        session['username'] = username
        return redirect(url_for('home'))
    else:
        #returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    email = request.form['email']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM Person WHERE username = %s'
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "User already exists"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO Person VALUES(%s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, password, firstName, lastName, email))
        conn.commit()
        cursor.close()
        return render_template('index.html')

@app.route('/home')
def home(error = ''):
    username = session['username']
    cursor = conn.cursor()

    query = 'SELECT pID, poster, filePath, caption, allFollowers, postingDate FROM Photo WHERE poster = %s ORDER BY postingDate DESC'
    cursor.execute(query, (username))
    data = cursor.fetchall()
    conn.commit()

    query2 = 'SELECT groupName, description FROM FriendGroup WHERE groupCreator = %s'
    cursor.execute(query2, (username))
    groups = cursor.fetchall()
    conn.commit()

    query3 = 'SELECT groupName, groupCreator FROM BelongTo WHERE username = %s'
    cursor.execute(query3, (username))
    groups2 = cursor.fetchall()
    conn.commit()

    cursor.close()

    if (error == ''):
        return render_template('home.html', username=username, posts=data, groups=groups, belongsToGroup=groups2)
    else:
        return render_template('home.html', username=username, posts=data, groups=groups, belongsToGroup=groups2, error=error)

# Create and return filename path
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# To check if filename is of appropriate type
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Convert digital data to binary format (used for BLOB)
def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def share_with_groups(filePath, caption, poster, groupNames):
    cursor = conn.cursor()

    query = 'SELECT LAST_INSERT_ID()'
    cursor.execute(query)
    pID = cursor.fetchone();

    for group in groupNames:
        # inserting to sharedWith
        ins2 = 'INSERT INTO SharedWith (pID, groupName, groupCreator) VALUES(%s, %s, %s)'
        cursor.execute(ins2, (pID['LAST_INSERT_ID()'], group, poster))
        conn.commit()
    
    cursor.close()
    return redirect(url_for('home'))

@app.route('/post', methods=['GET', 'POST'])
def post():
    if (request.method == 'POST'):
        poster = session['username']

        if 'filePath_img' not in request.files:
            flash('No file part')
            return redirect(url_for('home'))

        filePath = request.files['filePath_img']
        # if user does not select file, browser also
        # submit an empty part without filename
        if filePath.filename == '':
            flash('No selected file')
            return redirect(url_for('home'))
        if filePath and allowed_file(filePath.filename):
            filename = secure_filename(filePath.filename)
            filePath.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filePath = url_for('uploaded_file', filename=filename)
        
        # filePathDB = filePath.read()
        # filePathDB = convertToBinaryData(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        caption = request.form['caption']
        allFollowers_temp = request.form['allFollowers_temp']

        if(allFollowers_temp == 'followers'):
            allFollowers = 1 # all followers 
        else:
            allFollowers = 0 # members of friend group

        postingDate = datetime.datetime.now()

        groupNames = request.form.getlist('groups')

        cursor = conn.cursor()
        ins = 'INSERT INTO Photo (filePath, postingDate, allFollowers, caption, poster) VALUES(%s, %s, %s, %s, %s)'
        cursor.execute(ins, (filePath, postingDate, allFollowers, caption, poster))
        conn.commit()


        # try:
        #     cursor = conn.cursor()
        #     # ins = 'INSERT INTO Photo (filePath, postingDate, allFollowers, caption, poster) VALUES(%s, %s, %s, %s, %s)'
        #     # cursor.execute(ins, (filePath, postingDate, allFollowers, caption, poster))
        #     ins = 'INSERT INTO Photo (filePath, postingDate, allFollowers, caption, poster) VALUES(%s, %s, %s, %s, %s)'
        #     insert_blob_tuple = (filePath, postingDate, allFollowers, caption, poster)
        #     cursor.execute(ins, insert_blob_tuple)
        #     conn.commit()
        # except mysql.connector.Error as error:
        #     print("Failed inserting BLOB data into MySQL table {}".format(error))


        if (allFollowers == 0):
            share_with_groups(filePath, caption, poster, groupNames)

        cursor.close()

    return redirect(url_for('home'))

@app.route('/makeGroup', methods=['GET', 'POST'])
def makeGroup():
    username = session['username']
    groupName = request.form['groupName']
    description = request.form['description']
    
    cursor = conn.cursor()
    query = 'SELECT * FROM FriendGroup WHERE groupName = %s AND groupCreator = %s'
    cursor.execute(query, (groupName, username))
    data = cursor.fetchone()

    error = None
    if(data):
        error = 'INVALID: You have already created a group with this name!'
        cursor.close()
        return home(error)
    else:
        ins = 'INSERT INTO FriendGroup (groupName, groupCreator, description) VALUES(%s, %s, %s)'
        cursor.execute(ins, (groupName, username, description))
        conn.commit()

        ins = 'INSERT INTO BelongTo (username, groupName, groupCreator) VALUES(%s, %s, %s)'
        cursor.execute(ins, (username, groupName, username))
        conn.commit()

        cursor.close()
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')
        
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)
