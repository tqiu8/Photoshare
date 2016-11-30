######################################
# author ben lawson <balawson@bu.edu> 
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login
from urlparse import urlparse

#for image uploading
from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1211997'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users") 
users = cursor.fetchall()

temp_id = 0

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users") 
	return cursor.fetchall()

#def getUser()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	user.first_name=first_name
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd 
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']

	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out') 

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html') 

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')  

@app.route("/register", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
		first_name=request.form.get('first_name')
		last_name=request.form.get('last_name')
		dob=request.form.get('dob')
		hometown=request.form.get('hometown')
		gender=request.form.get('gender')
	except:
		print "couldn't find all tokens" #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print cursor.execute("INSERT INTO Users (email, password,first_name,last_name,dob,hometown,gender) VALUES ('{0}', '{1}', '{2}', '{3}','{4}','{5}','{6}')".format(email, password,first_name,last_name,dob,hometown,gender))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print "couldn't find all tokens"
		return flask.redirect(flask.url_for('register'))

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption, picture_id FROM Pictures WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getPhotoId(uid,photo):
	cursor=conn.cursor()
	cursor.exectue("SELECT picture_id FROM Pictures WHERE user_id='{0}' AND imgdata = '{1}'".format(uid,photo))
	return cursor.fetchone()[0]

def getUsersAlbums(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT album_id, name, date FROM Albums WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall()

def getAlbumsPhotos(uid,name):
	album_id = getAlbumId(uid,name)
	cursor=conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption, album_id, picture_id FROM Pictures WHERE user_id='{0}' AND album_id='{1}'".format(uid,album_id))
	return cursor.fetchall()

def getAlbumId(uid,name):
	cursor=conn.cursor()
	cursor.execute("SELECT album_id FROM Albums WHERE user_id='{0}' AND name='{1}'".format(uid,name))
	return cursor.fetchone()[0]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)): 
		#this means there are greater than zero entries with that email
		return False
	else:
		return True

def getName(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT first_name FROM Users WHERE user_id='{0}'".format(uid))
	return cursor.fetchone()

def getPhoto(photo_id):
	cursor=conn.cursor()
	cursor.execute("SELECT imgdata, caption, picture_id FROM Pictures where picture_id = '{0}'".format(photo_id))
	return cursor.fetchone()

def getPhotoOwner(photo_id):
	cursor=conn.cursor()
	cursor.execute("SELECT email FROM Users U, Pictures P WHERE picture_id= '{0}' AND P.user_id=U.user_id".format(photo_id))
	return cursor.fetchone()

def getUserInfo(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT email, first_name,last_name, dob, hometown, gender FROM Users WHERE user_id='{0}'".format(uid))
	return cursor.fetchall()

def getTags(photo):
	cursor = conn.cursor()
	cursor.execute("SELECT word FROM Tags WHERE picture_id = '{0}'".format(photo))
	return cursor.fetchall()
#end login code

def most_popularTags():
	cursor=conn.cursor()
	cursor.execute("SELECT word FROM Tags GROUP BY word ORDER BY COUNT(picture_id) DESC LIMIT 5")
	return cursor.fetchall()

def likes(photo):
	cursor=conn.cursor()
	cursor.execute("SELECT COUNT(user_id) FROM Likes WHERE picture_id='{0}'".format(photo))
	return cursor.fetchone()[0]

def like_users(photo):
	cursor=conn.cursor()
	cursor.execute("SELECT email FROM Likes L, Users U WHERE picture_id='{0}' AND U.user_id = L.user_id".format(photo))
	return cursor.fetchall()

def getComments(photo):
	cursor=conn.cursor()
	cursor.execute("SELECT text, email, date FROM Comments C, Users U WHERE picture_id = '{0}' AND C.user_id = U.user_id".format(photo))
	return cursor.fetchall()

def searchAll(tag):
	cursor=conn.cursor()
	cursor.execute("SELECT imgdata, caption, P.picture_id FROM Pictures P, Tags T WHERE T.word='{0}' AND P.picture_id = T.picture_id".format(tag))
	return cursor.fetchall()

def photo_rec(uid):
	cursor=conn.cursor()
	cursor.execute("SELECT imgdata, caption, P.picture_id from Pictures P, Tags T WHERE P.picture_id=T.picture_id AND P.picture_id!= '{0}' AND word IN(SELECT word FROM Tags T, Pictures P WHERE P.picture_id=T.picture_id GROUP BY word ORDER BY COUNT(T.picture_id) DESC) GROUP BY P.picture_id ORDER BY COUNT(P.picture_id) DESC LIMIT 5".format(uid))
	return cursor.fetchall()

def tag_rec(list):
	list=list.replace(',',' ').split()
	query="word='{0}'".format(list[0])
	for token in list[1:]:
		query+=" OR word='{0}'".format(token)
	search ="SELECT word from Tags WHERE picture_id IN (SELECT DISTINCT P.picture_id from Pictures P, Tags T WHERE P.picture_id=T.picture_id AND ({0})) AND word NOT IN (SELECT word FROM Tags WHERE {0}) GROUP BY word ORDER BY COUNT(picture_id) DESC LIMIT 5".format(query)
	cursor=conn.cursor()
	cursor.execute(search)
	return cursor.fetchall()

def activeUsers():
	cursor=conn.cursor()
	cursor.execute("SELECT U.email, (COUNT(P.picture_id)+COUNT(comment_id)) FROM Users U, Pictures P, Comments C WHERE U.user_id = C.user_id AND C.picture_id=P.picture_id GROUP BY U.user_id ORDER BY (COUNT(P.picture_id)+COUNT(comment_id)) DESC LIMIT 10")
	return cursor.fetchall()

@app.route('/profile')
@flask_login.login_required
def protected():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	info=getUserInfo(uid)
	albums = getUsersAlbums(uid)
	return render_template('profile.html', name=flask_login.current_user.id, info=info, albums=albums, message="User Profile", photos=getUsersPhotos(uid))

#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/friends',methods=['GET','POST'])
@flask_login.login_required
def search_friends():
	name=request.form.get('name')
	name=name.split(' ')
	first_name=name[0]
	last_name=name[1]
	cursor=conn.cursor()
	cursor.execute("SELECT user_id, first_name, last_name FROM Users WHERE first_name='{0}' AND last_name='{1}'".format(first_name,last_name))
	users=cursor.fetchall()
	return render_template('friends.html',users=users, message="Search results")

@app.route('/addfriend/<user>', methods=['GET'])
@flask_login.login_required
def add_friends(user):
	try:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		cursor=conn.cursor()
		cursor.execute("INSERT INTO Friends (user_1, user_2) VALUES ('{0}' , '{1}')".format(uid,user))
		conn.commit()
		return render_template('hello.html',message="You have successfully added a new friend!")
	except:
		return render_template('hello.html',message="This user is already your friend!")

@app.route('/allfriends', methods=['GET'])
@flask_login.login_required
def list_all_friends():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor=conn.cursor()
	cursor.execute("SELECT U.first_name,U.last_name,email from Users U, Friends F where F.user_1='{0}' AND F.user_2=U.user_id OR F.user_2='{0}' AND F.user_1=U.user_id".format(uid))
	friends=cursor.fetchall()
	return render_template('friends.html',friends=friends, message="Current Friends")

#Creates new albums
@app.route('/albums',methods=['GET','POST'])
@flask_login.login_required
def create_album():
	if request.method=='POST':
		uid=getUserIdFromEmail(flask_login.current_user.id)
		name=request.form.get('name')
		date=request.form.get('date')
		cursor=conn.cursor()
		cursor.execute("INSERT INTO Albums (name,date,user_id) VALUES ('{0}', '{1}', '{2}')".format(name,date,uid))
		conn.commit()
		return render_template('profile.html', albums=getUsersAlbums(uid))
	else:
		return render_template('albums.html')

#Opens up albums
@app.route("/open/<name>", methods=['GET'])
@flask_login.login_required
def open_album(name):
	uid=getUserIdFromEmail(flask_login.current_user.id)
	return render_template('open.html',pictures=getAlbumsPhotos(uid,name),message='Photos in '+name)

@app.route("/deletealbum/<album>", methods=['GET'])
@flask_login.login_required
def delete_album(album):
	uid=getUserIdFromEmail(flask_login.current_user.id)
	cursor=conn.cursor()
	cursor.execute("DELETE FROM Albums WHERE user_id='{0}' AND album_id='{1}'".format(uid,album))
	conn.commit()
	return render_template('profile.html', message='Album deleted!')

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		album_name = request.form.get('album_name')
		cursor=conn.cursor()
		album_id = getAlbumId(uid,album_name)
		print caption
		photo_data = base64.standard_b64encode(imgfile.read())
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Pictures (imgdata, user_id, caption, album_id) VALUES ('{0}', '{1}', '{2}', '{3}')".format(photo_data,uid, caption,album_id))
		conn.commit()
		return render_template('profile.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid) )
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html')
#end photo uploading code 

@app.route('/delete/<photo>', methods=['GET'])
@flask_login.login_required
def delete_photo(photo):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor=conn.cursor()
	cursor.execute("DELETE FROM Pictures WHERE user_id='{0}' AND picture_id='{1}'".format(uid,photo))
	conn.commit()
	return render_template('open.html', message='Photo deleted!')

@app.route('/photo/<photo>', methods=['GET','POST'])
@flask_login.login_required
def choose_photo(photo):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	picture=getPhoto(photo)
	return render_template('photo.html', picture=picture, tags=getTags(photo), likes=likes(photo), users=like_users(photo), owner=getPhotoOwner(photo), comments=getComments(photo))

@app.route('/like/<photo>', methods=['GET','POST'])
@flask_login.login_required
def like_photo(photo):
	try:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		cursor=conn.cursor()
		cursor.execute("INSERT INTO Likes (user_id, picture_id) VALUES ('{0}', '{1}')".format(uid,photo))
		conn.commit()
		return render_template('photo.html',picture=getPhoto(photo), tags=getTags(photo), likes=likes(photo), users=like_users(photo), owner=getPhotoOwner(photo), comments=getComments(photo), message="Liked!")
	except:
		return render_template('photo.html',picture=getPhoto(photo), tags=getTags(photo), likes=likes(photo), users=like_users(photo), comments=getComments(photo),message="You've already liked this photo!", owner=getPhotoOwner(photo))

@app.route('/comment/<photo>', methods=['GET','POST'])
def comment(photo):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	comment=request.form.get("comment")
	comment=comment.replace('\'','\'\'')
	date=request.form.get('date')
	cursor=conn.cursor()
	cursor.execute("SELECT user_id FROM Pictures WHERE picture_id='{0}'".format(photo))
	owner=cursor.fetchone()[0]
	if owner!= uid:
		cursor.execute("INSERT INTO Comments(user_id, picture_id, text, date) VALUES ('{0}', '{1}', '{2}', '{3}')".format(uid, photo, comment, date))
		conn.commit()
		return render_template('photo.html', owner=getPhotoOwner(photo), picture=getPhoto(photo), tags=getTags(photo), likes=likes(photo), users=like_users(photo), comments=getComments(photo))
	else:
		return render_template('photo.html', owner=getPhotoOwner(photo), picture=getPhoto(photo), tags=getTags(photo), likes=likes(photo), users=like_users(photo), comments=getComments(photo),message="You can't comment on your own photo")

@app.route('/tag/<photo>',methods=['POST'])
@flask_login.login_required
def add_tag(photo):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	tag = request.form.get('tag')
	cursor=conn.cursor()
	cursor.execute("INSERT INTO Tags (word, picture_id) VALUES ('{0}', '{1}')".format(tag,photo))
	conn.commit()
	return render_template('photo.html', owner=getPhotoOwner(photo), picture=getPhoto(photo), tags=getTags(photo), message='Tagged as '+tag, likes=likes(photo), users=like_users(photo), comments=getComments(photo))

@app.route('/rectags/<photo>',methods=['POST'])
@flask_login.login_required
def recTags(photo):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	search=request.form.get('query')
	return render_template('photo.html', owner=getPhotoOwner(photo), picture=getPhoto(photo), tags=getTags(photo), message='Here are some tags you could use!', likes=likes(photo), users=like_users(photo), comments=getComments(photo), recs=tag_rec(search))

@app.route('/<tag>',methods=['GET'])
def tag(tag):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor=conn.cursor()
	pictures=cursor.execute("SELECT imgdata, caption, P.picture_id FROM Pictures P, Tags T WHERE T.word='{0}' AND P.picture_id = T.picture_id AND P.user_id='{1}'".format(tag,uid))
	pictures=cursor.fetchall()
	return render_template('hello.html', name=getName(uid), photos=pictures,message="Here are all your photos with the tag: " +tag, other=tag)

@app.route('/all/<tag>', methods=['GET'])
def all(tag):
	pictures=searchAll(tag)
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('hello.html', name=getName(uid), photos=pictures,message="Here are all photos tagged with: "+tag)


@app.route('/search', methods=['POST'])
def search():
	query = request.form.get('query')
	query = query.split(' ')
	cursor=conn.cursor()
	search =""
	for token in query:
		search += "AND P.picture_id IN (SELECT picture_id FROM Tags WHERE word = '{0}')".format(token)
	search = "SELECT DISTINCT imgdata, caption, P.picture_id FROM Pictures P, Tags T WHERE P.picture_id =T.picture_id " + search
	print search
	result=cursor.execute(search)
	result=cursor.fetchall()
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('hello.html', name=getName(uid), photos=result, message="Search results:")



#default page  
@app.route("/", methods=['GET'])
def hello():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	popular = most_popularTags()
	users = activeUsers()
	return render_template('hello.html', name=getName(uid), message='Welcome to Photoshare', popular=popular, users=users, home=True, recs=photo_rec(uid))


if __name__ == "__main__":
	#this is invoked when in the shell  you run 
	#$ python app.py 
	app.run(port=5000, debug=True)
