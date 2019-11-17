import uuid

from flask import Flask, request
from flask_restplus import Resource, Api, fields, reqparse
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer)
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
flask_bcrypt = Bcrypt()

app = Flask(__name__)
db.init_app(app)
flask_bcrypt.init_app(app)
api = Api(app)

app.app_context().push()

SECRET_KEY = "roflmao"


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(100))


db.create_all()


user_model = api.model('user', {
    'username': fields.String(required=True, description='user username'),
    'password': fields.String(required=True, description='user password')
})

#flask_bcrypt.check_password_hash(self.password_hash, password)

def save_new_user(data):
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        new_user = User(
            username=data['username'],
            password_hash=flask_bcrypt.generate_password_hash(data['password']).decode('utf-8')
        )
        save_changes(new_user)
        return {'message': 'Successfully registered.'}, 201
    else:
        return {'message': 'User already exists.'}, 409


def get_all_users():
    return User.query.all()


def get_a_user(username):
    return User.query.filter_by(username=username).first()


def save_changes(data):
    db.session.add(data)
    db.session.commit()


@api.route('/users')
class UserList(Resource):
    @api.doc('list_of_registered_users')
    @api.marshal_list_with(user_model, envelope='data')
    def get(self):
        """List all registered users"""
        return get_all_users()

    @api.response(201, 'User successfully created.')
    @api.doc('create a new user')
    @api.expect(user_model, validate=True)
    def post(self):
        """Creates a new User """
        data = request.json
        return save_new_user(data=data)


@api.route('/test')
class Test(Resource):
    def get(self):
        """Returns a test message."""
        return {'test': 'ok'}


@api.route("/register")
class Auth(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str)
        parser.add_argument('password', type=str)
        args = parser.parse_args()
        username = args.get("username")
        password = args.get("password")
        s = Serializer(SECRET_KEY, expires_in=600)
        token = s.dumps(username)
        if username == 'admin' and password == 'admin':
            return token.decode()
        return 404


if __name__ == '__main__':
    app.run(debug=True)