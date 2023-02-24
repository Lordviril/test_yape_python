from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_jwt import JWT, jwt_required, current_identity
from pymongo import MongoClient
from oauth2client import client
from bson import json_util
import uuid
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'
api = Api(app)

client = MongoClient("mongodb://Lordviril:Gorposi0717@100.26.132.234:27017/SeLeTiene")
db = client.get_database("SeLeTiene")
users = db["UsersTest"]
listTextSearch = db["ListTextSearchTest"]

def solve(s):
   pat = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
   if re.match(pat,s):
      return True
   return False

@app.route("/yape/api/registerOrAuth", methods=["POST"])
def create_user():   
    data = request.get_json()
    if not isinstance(data["email"], str) :
        return jsonify({"error": "el campo email debe ser un String"}), 400 
    if data["email"] == "" :
        return jsonify({"error": "el campo email no puede ir vacio"}), 400
    if not solve(data["email"]) :
        return jsonify({"error": "el campo email tiene que tener el formato correcto"}), 400
    if data["token"] != "" :
        userData = users.find_one({"email": data["email"]})
        if not userData :
            users.insert_one({"email": data["email"], "token": data["token"]})
        if userData["email"] != data["email"] :
            return jsonify({"error": "No fue posible autenticarse con las credenciales actuales"}), 400
        return jsonify({"message": "Complete", "data": {"email": data["email"], "token": data["token"]}}), 201
    
    if not isinstance(data["password"], str) :
        return jsonify({"error": "el campo password debe ser un String"}), 400 
    if data["password"] == "" :
        return jsonify({"error": "el campo password no puede ir vacio"}), 400
    if len(data["password"]) < 6 :
        return jsonify({"error": "el campo password debe tener como minimo 6 caracteres"}), 400
    
    userData = users.find_one({"email": data["email"]})
    if not userData :
        users.insert_one({"email": data["email"], "password": data["password"]})
    if userData["password"] != data["password"] :
        return jsonify({"error": "No fue posible autenticarse con las credenciales actuales"}), 400
    return jsonify({"message": "Complete", "data": {"email": data["email"], "password": data["password"]}}), 201

@app.route("/yape/api/addTextSearch", methods=["POST"])
def addTextSearch():   
    data = request.get_json()
    if not isinstance(data["text"], str) :
        return jsonify({"text": "el campo text debe ser un String"}), 400 
    if data["text"] == "" :
        return jsonify({"error": "el campo text no puede ir vacio"}), 400
    if not isinstance(data["idUser"], str) :
        return jsonify({"text": "el campo idUser debe ser un String"}), 400 
    if data["idUser"] == "" :
        return jsonify({"error": "el campo idUser no puede ir vacio"}), 400
    textDb = listTextSearch.find_one({"text": data["text"], "idUser": data["idUser"]})
    if not textDb :
        listTextSearch.insert_one({"text": data["text"], "idUser": data["idUser"]})
    return jsonify({"message": "Complete"}), 201

@app.route("/yape/api/getTextSearch", methods=["POST"])
def getListTextSearch():
    data = request.get_json()   
    listTextDb = listTextSearch.find_one({"text": data["text"], "idUser": data["idUser"]})
    listText = []
    for text in listTextDb :
        listText.append(text["text"])

    return jsonify({"data": listText}), 200

    

class User(object):
    def __init__(self, id, name, email, photo_url):
        self.id = id
        self.name = name
        self.email = email
        self.photo_url = photo_url

    def __str__(self):
        return "User(id='%s')" % self.id

def authenticate(token):
    try:
        idinfo = client.verify_id_token(token, None)
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        userid = idinfo['sub']
        name = idinfo['name']
        email = idinfo['email']
        photo_url = idinfo['picture']
        user = User(userid, name, email, photo_url)
        return user
    except Exception as e:
        return None

def identity(payload):
    user_id = payload['identity']
    return User(user_id, None, None, None)

jwt = JWT(app, authenticate, identity)

class UserResource(Resource):
    @jwt_required()
    def get(self):
        user = current_identity
        return {'name': user.name, 'email': user.email, 'photo_url': user.photo_url}

    @jwt_required()
    def post(self):
        user = current_identity
        users = db.users
        existing_user = users.find_one({'id': user.id})
        if existing_user:
            return {'message': 'User already exists'}, 400
        new_user = {'id': user.id, 'name': user.name, 'email': user.email, 'photo_url': user.photo_url}
        users.insert_one(new_user)
        return {'message': 'User created successfully'}

api.add_resource(UserResource, '/user')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)