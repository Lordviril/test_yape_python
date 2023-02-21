from flask import Flask, request
from flask_restful import Resource, Api
from flask_jwt import JWT, jwt_required, current_identity
from pymongo import MongoClient
from oauth2client import client
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'
api = Api(app)

client = MongoClient("mongodb://Lordviril:Gorposi0717@100.26.132.234:27017/SeLeTiene")
db = client.get_database("SeLeTiene")
users = db["Users"]

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