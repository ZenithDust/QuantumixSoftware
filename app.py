from flask import Flask, render_template, render_template_string, request, redirect, url_for, g, Response, flash, abort, jsonify, send_file
from pymongo import MongoClient
from user.forms import KeySystem, KeyCaptcha
from datetime import datetime 
import time
import requests
import socket
import threading
import random
import string

# App Configs
app = Flask(__name__)
app.config['SECRET_KEY'] = "hello"
# Recaptcha WTForms
app.config['RECAPTCHA_PUBLIC_KEY'] = "6LdsSUYnAAAAADo-3dvTLieJMM5NVgHf4H4zVs9D"
app.config['RECAPTCHA_PRIVATE_KEY'] = "6LdsSUYnAAAAAM7P_L8Mvzj3M0j8Z90cT48aTnny"
app.config['RECAPTCHA_DATA_ATTRS'] = {'theme': 'dark'}

# MongoDB Connection
MongoURI = MongoClient('mongodb+srv://Zenith:ejaybaog@quantumix.smje85r.mongodb.net/?retryWrites=true&w=majority')
Database = MongoURI['Quantumix']
DataDocument = Database['Data']
KeyDocument = Database['Users']
ScriptDocument = Database['Scripts']
#KeyDocument.create_index("createdAt", expireAfterSeconds=120)
#ScriptDocument.create_index([("Name", "text"), ("Uploader", "text"), ("GameName", "text")])

# Error Handling
@app.errorhandler(404)
def not_found(e):
  errorType = "NotFound"
  return render_template('error-handler.html', errorType=errorType)

@app.errorhandler(500)
def internal_error(e):
  errorType = "InternalError"
  return render_template('error-handler.html', errorType=errorType)

# Function
def generate_key():
  return ''.join(random.choices(string.ascii_letters + string.digits, k=20))

def get_players_executed():
  user_data = DataDocument.find_one({"_id": "players"})
  if user_data:
    user_data.get("count", 1)
  return 1

def increment_players_executed():
  DataDocument.update_one({"_id": "players"}, {"$inc": {"count": 1}}, upsert=True)

def increment_hwid(inserted):
  KeyDocument.insert_one({"hwid": inserted})

# Routes
  
@app.route('/get/scripts', methods=['GET'])
def api_scripts():
  return 'Hello World'

@app.route('/', methods=["GET", "POST"])
def home():
  #ip = socket.gethostbyname(socket.gethostname())
  players_executed = DataDocument.find_one({"_id": "players"})
  total = players_executed['count']
  DBDocument = KeyDocument.find_one({"_id": "recentExecute"})
  DataCheckpoint = 1 
  
  return render_template('home.html', DataCheckpoint=DataCheckpoint, total=total, Data=DBDocument)

@app.route('/scripts', methods=["GET"])
def scripts():
  scriptID = request.args.get('id', "")
  search_query = request.args.get('search', "")
  page = int(request.args.get('page', 1))
  search_result = []
  
  items_per_page = 5
  total_items = ScriptDocument.count_documents({})
  total_pages = (total_items + items_per_page - 1) // items_per_page  # Calculate total page
  offset = (page - 1) * items_per_page
  data = ScriptDocument.find().skip(offset).limit(items_per_page)
  pagination_range = range(max(1, page - 2), min(page + 3, total_pages + 1))
  
  if search_query:
    search_result = ScriptDocument.find({"$text": {"$search": search_query}})
  
  max_range = min(page + 3, total_pages + 1)
  min_range = max(1, max_range - 5)
  pagination_range = range(min_range, max_range)
  
  return render_template('scripts.html', data=data, page=page, total_pages=total_pages, pagination_range=pagination_range, query=search_query, results=search_result, scriptID=scriptID)

@app.route('/pagination')
def pagination():
  abort(500)
  page = int(request.args.get('page', 1))
  items_per_page = 3
  total_items = ScriptDocument.count_documents({})  # Count total items in collection
  total_pages = (total_items + items_per_page - 1) // items_per_page  # Calculate total page
  offset = (page - 1) * items_per_page
  data = ScriptDocument.find().skip(offset).limit(items_per_page)
  pagination_range = range(max(1, page - 2), min(page + 3, total_pages + 1))
  return render_template('pagination.html', data=data, page=page, total_pages=total_pages, pagination_range=pagination_range)

@app.route('/check', methods=['GET', 'POST'])
def check():
  Referer = request.headers.get("Referer")
  UsrData = KeyDocument.find_one({"ip": request.remote_addr})
  DataCheckpoint = 0
  key = None
  
  if UsrData:
    DataCheckpoint = UsrData['checkpoint']
  
  if Referer == 'https://linkvertise.com/' and DataCheckpoint == 3:
    key = generate_key()
    KeyDocument.update_one({"ip": request.remote_addr}, {"$set": {"key": key}})
    return redirect(url_for('key', userKey=key))
  elif Referer == 'https://linkvertise.com/' and DataCheckpoint == 2:
    KeyDocument.update_one({"ip": request.remote_addr}, {"$inc": {"checkpoint": 1}})
    return render_template('check.html', DataCheckpoint=DataCheckpoint, redirect_url=url_for('getkey', checkpoint=DataCheckpoint + 1), countdown_seconds=10)
  elif Referer == 'https://linkvertise.com/' and DataCheckpoint == 1:
    KeyDocument.update_one({"ip": request.remote_addr}, {"$inc": {"checkpoint": 1}})
    return render_template('check.html', DataCheckpoint=DataCheckpoint, redirect_url=url_for('getkey', checkpoint=DataCheckpoint + 1), countdown_seconds=10)
  else:
    flash("Don't try to bypass or you will get banned from our software!")
    return render_template('check.html', redirect_url=url_for('getkey'), countdown_seconds=10)
    #return redirect(url_for('getkey', checkpoint=DataCheckpoint))
  
  return 'Nothing In Here!'

@app.route('/getkey/<int:checkpoint>', methods=['GET', 'POST'])
def getkey(checkpoint):
  form = KeySystem()
  HWID = request.args.get('hwid', "")
  Users = KeyDocument.find_one({"ip": request.remote_addr})
  current_checkpoint = 0
  checkpointURL = ['https://link-target.net/885916/title-referrer-lol', 'https://direct-link.net/885916/kikeboboka', 'https://link-target.net/885916/kikey-borichy']
  
  if Users:
    current_checkpoint = Users['checkpoint']
  else:
    KeyDocument.insert_one({"ip": request.remote_addr, "hwid": HWID, "checkpoint": 1, "key": "none", "IsPremium": False,"createdAt": datetime.utcnow()})
    current_checkpoint = 1
  
  if checkpoint > current_checkpoint and checkpoint < current_checkpoint:
    abort(404)
  else:
    # Check if summited
    if form.validate_on_submit():
      if current_checkpoint == 3:
        return redirect(checkpointURL[2])
      elif current_checkpoint == 2:
        return redirect(checkpointURL[1])
      elif current_checkpoint == 1:
        return redirect(checkpointURL[0])
    return render_template('checkpoint.html', currentCheckpoint=current_checkpoint, form=form)
  return 'Nothing Here'

@app.route('/key/<userKey>', methods=['GET', 'POST'])
def key(userKey):
  Document = KeyDocument.find_one({"ip": request.remote_addr})
  timedKey = userKey
  key = None
  captchaDone = False
  captchaForm = KeyCaptcha()
  
  if Document and Document['checkpoint'] == 3 and timedKey == Document['key']:
    if captchaForm.validate_on_submit():
      captchaDone = True 
      key = timedKey
  else:
    flash("Don't try to bypass or you will get banned from our software!")
    return redirect(url_for('getkey', checkpoint=1))
  return render_template('key.html', key=key, captchaForm=captchaForm, captchaDone=captchaDone, DBCheckpoint=Document['checkpoint'])

@app.route('/redirect/getkey')
def getkeyredirect():
  return render_template('getkey.html')
  
@app.route('/raw/<script>', methods=['GET'])
def raw(script):
  name = script
  if name:
    scriptName = ScriptDocument.find_one({"Name": name})
    script = scriptName['Script'].__str__()
    response = Response(script, content_type='text/plain')
    return response

# Api
@app.route('/api/quantumix/executed', methods=['POST'])
def increment_players():
  if (request.data):
    readData = request.get_json(force=False, silent=False, cache=True)
    username = readData['username']
    userid = readData['userid']
    avatar = readData['avatar']
    if username and userid and avatar:
      KeyDocument.update_one({"_id": "recentExecute"}, {'$set': {'username': username, 'userid': userid, 'avatar': avatar}})
      increment_players_executed()
      return jsonify({'message': 'succes'})
    else:
      return 'No Data', 404

@app.route('/api/executes', methods=['GET'])
def executes():
  data = DataDocument.find_one({'_id': "players"})
  return jsonify({"executes": data['count']})

@app.route('/download')
def download():
  path = ""