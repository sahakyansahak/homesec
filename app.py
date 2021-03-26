from __future__ import unicode_literals
from flask import *
import sqlite3
import os
import flask
from flask_socketio import SocketIO, emit
import pafy, pyglet
import urllib.request
from urllib.parse import *
from bs4 import BeautifulSoup
import youtube_dl
import pygame
from pygame import *
from pydub import AudioSegment
import shutil
import subprocess
import psutil
import datetime
import subprocess
import ast

app = Flask(__name__)
app.secret_key = '1502'
socketio = SocketIO( app )
socketio.init_app(app, cors_allowed_origins="*")
#cmd = "python3 recognize_video.py --detector face_detection_model --embedding-model openface_nn4.small2.v1.t7 --recognizer output/recognizer.pickle --le output/le.pickle"
#cmd1 = "python3 read.py"
#cmd2 = "python3 solar.py"

#subprocess.Popen(cmd2, shell=True)
#subprocess.Popen(cmd1, shell=True)
#subprocess.Popen(cmd, shell=True)

#extrack_embedings
#train_model

temps = []
dict = {}
stoppp = 1
music_time_minute = 0
solar_temp = []
a = 0

@app.route('/', methods=['GET', 'POST'])
def index():
	#global send_uname
	#global new_uname
	if g.user:
		return redirect(url_for('home'))
	if request.method == 'POST':
		session.pop('user', None)
		conn = sqlite3.connect("DB/user.db")
		c = conn.cursor()
		if len(get_tables()) > 0:
			for i in get_tables():
				if request.form['password'] == c.execute("SELECT * FROM " + i[0]).fetchall()[0][1].strip() and request.form['username'] == c.execute("SELECT * FROM " + i[0]).fetchall()[0][0].strip():
					#send_uname = i[0]
					#new_uname = i[0]
					session['user'] = request.form['username']
					return redirect(url_for('home'))
		else:
			if request.form['password'] == 'admin' and request.form['username'] == 'admin':
				#sned_uname = "aaa"
				#new_uname = "Admin"гет
				print("Uname set")
				session['user'] = request.form['username']
				return redirect(url_for('f_login'))

	return render_template('login1.html')

@app.route("/home", methods=['GET', 'POST'])
def home():
	if g.user:
		return render_template('index.html')
	else:
		return index()

@app.route("/log", methods=['GET', 'POST'])
def log():
	return index()

@app.route("/f_login", methods=['GET', 'POST'])
def f_login():
	if (len(get_tables()) == 0):
		return render_template('create_us.html')
	else:
		return index()


@app.route("/climate", methods=['GET', 'POST'])
def climate():
	#if g.user:
	return render_template("climate.html")
	#else:
	#	return index()



@app.route('/s/<id>/<switch>/<state>', methods = ['POST', 'GET'])
def s(id, switch, state):
	print('State change')
	conn = sqlite3.connect("DB/evth.db")
	c = conn.cursor()
	data = ast.literal_eval(c.execute("SELECT * FROM hard").fetchall()[0][0])
	data["l" + str(switch)] = int(state)
	print('UPDATE hard SET data = ' + str(data) +  '"')
	c.execute('UPDATE hard SET data = "' + str(data) +  '"')
	conn.commit()
	return "11"

@app.route('/h/<id>/<heat>/<temp>', methods = ['POST', 'GET'])
def h(id, heat, temp):
	print('State change heating')
	conn = sqlite3.connect("DB/evth.db")
	c = conn.cursor()
	data = ast.literal_eval(c.execute("SELECT * FROM hard").fetchall()[0][0])
	data["heat" + str(heat)] = float(temp)
	print('UPDATE hard SET data = ' + str(data) +  '"')
	c.execute('UPDATE hard SET data = "' + str(data) +  '"')
	conn.commit()
	return "11"

@app.route("/gps", methods=['GET', 'POST'])
def gps():
	if g.user:
		return render_template("cords.html")
	else:
		return index()


@app.route("/camera", methods=['GET', 'POST'])
def camera():
	#if g.user:
		return render_template("camera.html")
	#else:
	#	return index()

@app.route("/main", methods=['GET', 'POST'])
def main():
	#if g.user:
		return render_template("main.html")
	#else:
	#	return index()

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

@app.route('/getsession')
def getsession():
    if 'user' in session:
        return session['user']

    return 'not'

@app.route('/get_curr_us', methods=['GET', 'POST'])
def get_curr_us():
	conn = sqlite3.connect("DB/user.db")
	c = conn.cursor()
	return jsonify(c.execute("SELECT * FROM " + getsession()).fetchall())




@app.route('/messages', methods=['GET', 'POST'])
def messages():
	conn = sqlite3.connect("DB/evth.db")
	c = conn.cursor()
	return jsonify(c.execute("SELECT * FROM mess").fetchall())

@app.route('/s_sys', methods=['GET', 'POST'])
def s_sys():
	global solar_temp
	a = solar_temp
	solar_temp = []
	if 1:
		print(ast.literal_eval(sqlite3.connect("DB/evth.db").cursor().execute("SELECT * FROM hard").fetchall()[0][0]))
		return jsonify(a, 
			ast.literal_eval(sqlite3.connect("DB/evth.db").cursor().execute("SELECT * FROM hard").fetchall()[0][0]), 
			sqlite3.connect("DB/evth.db").cursor().execute("SELECT * FROM sc_s").fetchall()[0][0],
			#sqlite3.connect("DB/evth.db").cursor().execute("SELECT * FROM rci").fetchall()[0][0]
			)
	else:
		return "0"

#c.execute('INSERT INTO hard VALUES ("' + str(a) +  '")')

@app.route('/new_day_code', methods=['GET', 'POST'])
def new_day_code():
	global temps
	print(temps, "New Dat")
	a = temps
	temps = []
	return jsonify(str(a).replace("'", '"'))


@app.route('/new_day/<my_day>', methods=['GET', 'POST'])
def new_day(my_day):
	global temps
	print(my_day)
	conn = sqlite3.connect("DB/evth.db")
	c = conn.cursor()
	get_day = my_day.split(" ")[0].split("&")
	print(get_day)
	for i in c.execute("SELECT * FROM t1").fetchall():

		day = i[0].split("/")
		#print(int(day[1]) == int(get_day[1]), int(day[2]) == int(get_day[0]), int(day[3]) == int(get_day[2]))
		if int(day[1]) == int(get_day[1]) and int(day[2]) == int(get_day[2]) and int(day[0]) == int(get_day[0]):
			temps.append(i[1])

	print(temps)
	return "11"


@app.route('/add_mess/<my_mess>/<ad_user>', methods=['GET', 'POST'])
def add_mess(my_mess, ad_user):
	conn = sqlite3.connect('DB/evth.db')
	c = conn.cursor()
	c.execute("INSERT INTO mess VALUES ('" + ad_user + "', '" + my_mess + "')")
	conn.commit()
	return "11"

@socketio.on( 'Get message' )
def handle_my_custom_event( *user):
	print("Here")
	if 1:
		print( user)
		conn = sqlite3.connect('DB/evth.db')
		c = conn.cursor()
		c.execute("INSERT INTO mess VALUES ('" + user[0]['user_name'] + "', '" + user[0]['message'] + "')")
		conn.commit()
	else :
		print("Error")
	socketio.emit( 'my response', c.execute("SELECT * FROM mess").fetchall())


@socketio.on( 'my solar' )
def handle_my_custom_solar( json ):
	global solar_temp
	print( 'recived my event: ' + str( json ) )
	conn = sqlite3.connect('DB/evth.db')
	c = conn.cursor()
	try:
		login = json['user_name']
		passw = json['message']
		my_values = []
		print("LOGIN IS:   " + login)
		print("PASS IS:    " + passw)
		#c.execute("INSERT INTO mess VALUES ('" + json['user_name'] + "', '" + json['message'] + "')")
		if len(c.execute("SELECT * FROM solar1").fetchall()) > 1:
			print("DETECTED VALUES")
			for i in c.execute("SELECT * FROM solar1").fetchall():
				if i[0] == login:
					my_values = [i[2], i[3], i[4], i[5], i[6], i[7], i[8]]
					break
		else:
			print("DETECTED NO VALUES")
			c.execute("INSERT INTO solar_do VALUES ('1','" + login + "', '" + passw +"')")
			conn.commit()
			while_ = 0
			while c.execute("SELECT * FROM solar_do WHERE passw = '" + passw +"'").fetchall()[0][0] != "0":
				if while_ == 0:
					print("IN WHILE")
				while_ = 1
			print("OUT FROM WHILE")
			my_dat = c.execute("SELECT * FROM solar1 WHERE pass = '" + passw + "'").fetchall()[0]
			print(my_dat)
			my_values = [my_dat[2], my_dat[3], my_dat[4], my_dat[5], my_dat[6], my_dat[7], my_dat[8]]
			solar_temp = my_values
		print(my_values)
		print("WANT TO SEND")
		print("DATA SENT")
		conn.commit()
		socketio.emit( 'my resp', str("aaaaaaa"))

	
	except:
		pass

@app.route('/valod', methods=['GET', 'POST'])
def valod():
    print(1)
    while getsession() != 'not':
        session.pop('user', None)
    print(1)
    return "11"

def us_db(uname):	
	conn = sqlite3.connect("DB/user.db")
	c = conn.cursor()
	c.execute("CREATE TABLE IF NOT EXISTS " + uname + " (uname TEXT, passwd TEXT, isdamin INT, cardid TEXT)")
	conn.commit()


def get_tables():
	conn = sqlite3.connect("DB/user.db")
	c = conn.cursor()
	return c.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()


@app.route('/new_us', methods=['POST', 'GET'])
def new_us():
	uname = request.form["uname"]
	passw = request.form["pass"]
	card = request.form["card"]
	#session['user'] = uname
	conn = sqlite3.connect("DB/user.db")
	c = conn.cursor()
	adm = 0
	os.system("mkdir dataset/" + uname)
	uploaded_files = flask.request.files.getlist("file[]")
	if len(get_tables()) == 0:
		adm = 1
	if str(uploaded_files[0])[15] != "'":
		i = 0
		for file in uploaded_files:
			file.save("static/dataset/" + str(uname) + "/" + str(i) + ".png")
			i += 1
			print(file)
		cmd = "python3 start_tarin.py"
		subprocess.Popen(cmd, shell=True)
	us_db(uname)
	c.execute("INSERT INTO " + uname + " VALUES('" + str(uname) + "', ' " + str(passw) + " ', ' " + str(adm) + "', '" + str(card) + "')")
	conn.commit()
	return home()


@app.route('/handle_data/<music_name>', methods=['POST'])
def handle_data(music_name):
	print(music_name)
	projectpath = music_name.split('-')
	print(projectpath)
	music_player(projectpath[0])
	print("Playing")
	return ('', 204)


@app.route('/door_open', methods=['POST', "GET"])
def door_open():
	conn = sqlite3.connect("DB/evth.db")
	c = conn.cursor()
	c.execute("UPDATE garage SET state = '1'")
	conn.commit()
	return "11"

@app.route('/lock_home', methods=['POST'])
def lock_home():
	conn = sqlite3.connect("DB/evth.db")
	c = conn.cursor()
	c.execute("UPDATE sc_s SET state = '1'")
	conn.commit()
	return ('', 204)

@app.route('/unlock_home', methods=['POST'])
def unlock_home():
	conn = sqlite3.connect("DB/evth.db")
	c = conn.cursor()
	c.execute("UPDATE sc_s SET state = '0'")
	conn.commit()
	return ('', 204)


@app.route('/player_stop', methods=['POST'])
def player_stop():
	global stoppp
	stoppp = 1
	PROCNAME = "chromium-browse"
	for proc in psutil.process_iter():
		# check whether the process name matches
		print(proc.name())
		if proc.name() == PROCNAME:
			try:
				proc.kill()
			except:
				pass
	print(stoppp)
	return ('', 204)


def music_player(command1):
	global dict
	global stoppp
	global music_time_minute
	stoppp = 0
	PROCNAME = "chromium-browse"
	for proc in psutil.process_iter():
		# check whether the process name matches
		print(proc.name())
		if proc.name() == PROCNAME:
			try:
				proc.kill()
			except:
				pass
	#filelist = [ f for f in os.listdir('/home/pi/flask') if f.endswith(".mp3") ]
	#for f in filelist:
	#	os.remove(os.path.join('/home/pi/flask', f))
	print(command1)
	def url_search(search_string, max_search):
		global dict
		textToSearch = search_string
		query = urllib.parse.quote(textToSearch)
		url = "https://www.youtube.com/results?search_query=" + query
		response = urllib.request.urlopen(url)
		html = response.read()
		soup = BeautifulSoup(html, 'lxml')
		i = 1
		dict = {}
		for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
			if len(dict) < max_search:
				dict[i] = 'https://www.youtube.com' + vid['href']
				i += 1
			else:
				break
		for vid1 in soup.findAll(attrs={'class':'yt-lockup-playlist-item-length'}):
			if True:
				return int(str(vid1)[-18]) + 1
				break


	long = url_search(command1, 1)
	print(dict)
	cmd = "DISPLAY=:0 chromium-browser --enable-gpu-vsync --enable-tcp-fast-open " + dict[1]
	subprocess.Popen(cmd, shell=True)
	x = datetime.datetime.now()
	ft = int(x.strftime("%M"))
	if ft + long > 60:
		music_time_minute = (ft + long) - 60
	else:
		music_time_minute = ft + long


if __name__ == "__main__":
	app.secret_key = '1502'
	socketio.run(app, host='0.0.0.0', debug=True, port=8080)
	#, ssl_context='adhoc'