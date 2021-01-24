import flask
import jwt
import base64
from flask import request, jsonify
import mysql.connector
import uuid
import os
import requests

#create table files (id int not null auto_increment primary key, user varchar(256) not null, name varchar(256) not null, localname varchar(256) not null);


mydb = mysql.connector.connect(
  host="db_upload",
  user="root",
  password="1",
  database="api"
)

url={"getcountmessage":"http://apichat:5001/api/chat/countmessage/"}

def check_jwt(jwttest):
    try:
        data=jwt.decode(jwttest,app.config['SECRET_KEY'],algorithm='HS256');
        return {'logged':True,'user':data}
    except:
        return {'logged':False}
	

app = flask.Flask(__name__,template_folder='template_login')
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = '!@#super-secret-key!@#$asdadsd'

UPLOAD_FOLDER = '/filestorage/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return True
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/files', methods=['GET'])
def home():
    return flask.render_template("files.html")


@app.route('/api/files/upload', methods=['POST'])
def api_register():
    user_data = check_jwt(flask.request.headers.get("Authorization"));
    if not user_data["logged"]:
        return ""
    if 'file' not in request.files:
        return 'No file part';
        
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return 'No file part';
    if file and allowed_file(file.filename):
        filename = str(uuid.uuid4())
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        mycursor = mydb.cursor()
        mycursor.execute("INSERT INTO files (user,name,localname) values (%s,%s,%s)", (user_data["user"]["id"],file.filename,filename))
        mydb.commit()
        return 'Plik wysłany';
    else:
        return 'nie mozna wyslac';

@app.route('/api/files/info', methods=['GET'])
def api_info():
    user_data = check_jwt(flask.request.headers.get("Authorization"));
    file=[]
    if user_data["logged"]:
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM files where user=%s", (user_data["user"]["id"],));
        myresult = mycursor.fetchall()
        for x in myresult:
            response = requests.get(url['getcountmessage']+x[3],headers={'Authorization': flask.request.headers.get("Authorization")})
            json_response = response.json()
            y = []
            y.extend(x)
            y.extend(json_response['count']);
            file.append(y)



    return jsonify(file)
        

@app.route('/api/files/delete', methods=['DELETE'])
def api_delete():
    user_data = check_jwt(flask.request.headers.get("Authorization"));
    file=[]
    if user_data["logged"]:
        mycursor = mydb.cursor()
        mycursor.execute("UPDATE files set user=0 where localname=%s and user=%s", (request.form['id'],user_data["user"]["id"]));
        mydb.commit()

    return 'Plik usuniety';

@app.route('/api/files/download/<uuid>/<name>', methods=['GET'])
def api_download(uuid,name):
    return flask.send_file(UPLOAD_FOLDER+uuid, attachment_filename=name)


@app.route('/api/files/bulk_info', methods=['POST'])
def api_bulk_info():
    user_data = check_jwt(flask.request.headers.get("Authorization"));
    if not user_data["logged"]:
        return ""
    files = request.get_json(force=True)
    return_data={}
    for filex in files:
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM files where localname=%s", (filex,));
        myresult = mycursor.fetchall()
        for x in myresult:
            return_data[filex]={'name':x[2],'user':x[1]}
    return jsonify(return_data)


app.run(host="0.0.0.0",port=5002)
