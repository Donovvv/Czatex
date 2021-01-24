import flask
import jwt
import base64
from flask import request, jsonify
import mysql.connector
import requests

#create table users (id int not null auto_increment primary key, login varchar(256) not null, pass varchar(256) not null);

mydb = mysql.connector.connect(
  host="db_logowanie",
  user="root",
  password="1",
  database="api"
)


url={"getuserfiles":"http://apiupload:5002/api/files/info",
     "getlastmessage":"http://apichat:5001/api/chat/lastmessage"}

def check_jwt(jwttest):
    try:
        data=jwt.decode(jwttest,app.config['SECRET_KEY'],algorithm='HS256');
        return {'logged':True,'user':data}
    except:
        return {'logged':False}
	

app = flask.Flask(__name__,template_folder='template_login')
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = '!@#super-secret-key!@#$asdadsd'

@app.route('/', methods=['GET'])
def home():
    return flask.render_template("login.html")

@app.route('/info', methods=['GET'])
def info():
    return flask.render_template("info.html")

@app.route('/register', methods=['GET'])
def register():
    return flask.render_template("register.html")



@app.route('/api/login', methods=['POST'])
def api_login():
    user={"login":request.form['login'],"pass":request.form['pass']}
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM users where login=%s and pass=%s", (user["login"],user["pass"]))
    myresult = mycursor.fetchall()
    user=None;
    for x in myresult:
       user=x
    if user!=None:
        return jsonify({'token':jwt.encode({'username': user[1],'id':user[0]}, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')});
    else:
        return "{}"

@app.route('/api/register', methods=['POST'])
def api_register():
    user={"login":request.form['login'],"pass":request.form['pass']}
    mycursor = mydb.cursor()
    print(user["login"]);
    mycursor.execute("SELECT * FROM users where login=%s -- -and pass=%s", (user["login"],user["pass"]))
    myresult = mycursor.fetchall()
    user2=None;
    for x in myresult:
       user2=x
    if user2!=None:
        return jsonify({'status':'Uzytkownik istnieje'});
    mycursor = mydb.cursor()
    mycursor.execute("INSERT INTO users (login,pass) values (%s,%s)", (user["login"],user["pass"]))
    mydb.commit()
    return jsonify({'status':'Prawidłowo zarejestrowano'});

@app.route('/api/info', methods=['GET'])
def api_info():
    jwt=check_jwt(flask.request.headers.get("Authorization"))
    if not jwt["logged"]:
        return ""
    response = requests.get(url['getuserfiles'],headers={'Authorization': flask.request.headers.get("Authorization")})
    json_response = response.json()
    jwt["countfiles"]=str(len(json_response));


    response = requests.get(url['getlastmessage'],headers={'Authorization': flask.request.headers.get("Authorization")})
    json_response = response.json()
    jwt["lastmessage"]=json_response['msg'];
    return jwt;


@app.route('/api/user/bulk_info', methods=['POST'])
def api_bulk_info():
    user_data = check_jwt(flask.request.headers.get("Authorization"));
    if not user_data["logged"]:
        return ""
    userlist = request.get_json(force=True)
    return_data={}
    for userx in userlist:
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM users where id=%s", (userx,));
        myresult = mycursor.fetchall()
        for x in myresult:
            return_data[userx]=x[1]


    return jsonify(return_data)

app.run(host='0.0.0.0')
