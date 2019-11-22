from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import jwt
import datetime
from functools import wraps
from flask import request


SECRET_KEY = "g[}b-867T2-)fxQ.[KQ!NJH{"
db = SQLAlchemy()
flask_bcrypt = Bcrypt()


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(60))


def auth_init(app):
    db.init_app(app)
    db.create_all()
    flask_bcrypt.init_app(app)


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


def save_changes(data):
    db.session.add(data)
    db.session.commit()


def encode_auth_token(user_id):
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm='HS256'
        )
    except Exception as e:
        return e


def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, SECRET_KEY)
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'


def login_user(data):
    try:
        user = User.query.filter_by(username=data.get('username')).first()
        if user and flask_bcrypt.check_password_hash(user.password_hash, data.get('password')):
            auth_token = encode_auth_token(user.id)
            if auth_token:
                response_object = {
                    'status': 'success',
                    'message': 'Successfully logged in.',
                    'Authorization': auth_token.decode()
                }
                return response_object, 200
        else:
            response_object = {
                'status': 'fail',
                'message': 'email or password does not match.'
            }
            return response_object, 401

    except Exception as e:
        print(e)
        response_object = {
            'status': 'fail',
            'message': 'Try again'
        }
        return response_object, 500


def get_logged_in_user(new_request):
    invalid_resp = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }, 401
    auth_header = new_request.headers.get('Authorization')
    if not auth_header:
        return invalid_resp
    auth_header = auth_header.split()
    if len(auth_header) != 2:
        return invalid_resp
    auth_token = auth_header[1]
    if auth_token:
        resp = decode_auth_token(auth_token)
        if not isinstance(resp, str):
            user = User.query.filter_by(id=resp).first()
            response_object = {
                'status': 'success',
                'data': {
                    'user_id': user.id,
                    'username': user.username
                }
            }
            return response_object, 200
        response_object = {
            'status': 'fail',
            'message': resp
        }
        return response_object, 401
    else:
        return invalid_resp


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        data, status = get_logged_in_user(request)
        token = data.get('data')

        if not token:
            return data, status

        return f(*args, **kwargs)

    return decorated
