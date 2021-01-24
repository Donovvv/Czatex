import flask
import jwt
import base64
from flask import request, jsonify
import mysql.connector
import uuid
import os
import requests

#create table chat (id int not null auto_increment primary key, user varchar(256) not null, file varchar(256), message varchar(256) not null);

mydb = mysql.connector.connect(
  host="db_chat",
  user="root",
  password="1",
  database="api"
)

url={"getuserfiles":"http://apiupload:5002/api/files/info",
     "getfilenames":"http://apiupload:5002/api/files/bulk_info",
     "getusername":"http://apilogowanie:5000/api/user/bulk_info"}

def check_jwt(jwttest):
    try:
        data=jwt.decode(jwttest,app.config['SECRET_KEY'],algorithm='HS256');
        return {'logged':True,'user':data}
    except:
        return {'logged':False}
	

app = flask.Flask(__name__,template_folder='template_login')
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = '!@#super-secret-key!@#$asdadsd'


@app.route('/chat', methods=['GET'])
def home():
    return flask.render_template("chat.html")


@app.route('/api/chat/send', methods=['POST'])
def api_msg():
    user_data = check_jwt(flask.request.headers.get("Authorization"));
    filex=request.form['file']
    msg=request.form['msg']
    
    mycursor = mydb.cursor()
    mycursor.execute("INSERT INTO chat (user,file,message) values (%s,%s,%s)", (user_data["user"]["id"],filex,msg))
    mydb.commit()
    return "ok";


@app.route('/api/chat/get', methods=['GET'])
def api_info():
    user_data = check_jwt(flask.request.headers.get("Authorization"));
    chat=[]
    if user_data["logged"]:
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM chat order by id desc limit 10");
        myresult = mycursor.fetchall()
        for x in myresult:
            chat.append({"user":x[1],"file":x[2],"filename":x[2],"msg":x[3]});

    file_name=[]
    user_name=[]
    for a in chat:
        user_name.append(a['user']);
        if len(a['file'])>0:
            file_name.append(a['file']);

    if len(file_name)>0:
        response = requests.post(url['getfilenames'],json=file_name,headers={'Authorization': flask.request.headers.get("Authorization")})
        json_response = response.json()
        for a in chat:
            if len(a['file'])>0:
                a['filename']=json_response[a['file']]


    if len(user_name)>0:
        response = requests.post(url['getusername'],json=user_name,headers={'Authorization': flask.request.headers.get("Authorization")})
        json_response = response.json()
        for a in chat:
            a['user']=json_response[a['user']]

    response = requests.get(url['getuserfiles'],headers={'Authorization': flask.request.headers.get("Authorization")})
    json_response = response.json()
    files=[]
    for a in json_response:
        files.append((a[3],a[2]))

    return jsonify({"chat":chat,"files":files});
        

@app.route('/api/chat/lastmessage', methods=['GET'])
def api_lastmessage():
    user_data = check_jwt(flask.request.headers.get("Authorization"));
    chat={"msg":""}
    if user_data["logged"]:
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM chat where user=%s order by id desc limit 1",(user_data['user']['id'],));
        myresult = mycursor.fetchall()
        for x in myresult:
            chat={"user":x[1],"file":x[2],"filename":x[2],"msg":x[3]};
    return jsonify(chat)


@app.route('/api/chat/countmessage/<id>', methods=['GET'])
def api_countmessage(id):
    user_data = check_jwt(flask.request.headers.get("Authorization"));
    returnx={"count":0}
    if user_data["logged"]:
        mycursor = mydb.cursor()
        mycursor.execute("SELECT count(*) FROM chat where file=%s",(id,));
        myresult = mycursor.fetchall()
        for x in myresult:
            returnx={"count":x}
    return jsonify(returnx)

app.run(host="0.0.0.0",port=5001)
