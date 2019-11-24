import secrets

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_bcrypt import Bcrypt
import jwt
import datetime
from functools import wraps
from flask import request


SECRET_KEY = "g[}b-867T2-)fxQ.[KQ!NJH{"
db = SQLAlchemy()
flask_bcrypt = Bcrypt()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(60))


class Key(db.Model):
    __tablename__ = "keys"

    key = db.Column(db.String(60), primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    #key_user = db.relationship('User', backref='keys')


class Usage(db.Model):
    __tablename__ = "usages"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key_id = db.Column(db.String(60), db.ForeignKey('keys.key'), nullable=False)
    timestamp = db.Column(db.DateTime)#, default=datetime.datetime.utcnow
    endpoint = db.Column(db.String(60))
    method = db.Column(db.String(60))

    #key_usage = db.relationship('Key',backref='usages')


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


def create_key(user_id):
    key_exists = True
    while key_exists:
        secret = secrets.token_urlsafe(32)
        found_key = Key.query.filter_by(key=secret).first()
        if not found_key:
            key_exists = False

    new_key = Key(
        key=secret,
        user_id=user_id
    )
    save_changes(new_key)
    return secret


def delete_key(user_id, key):
    return Key.query.filter_by(user_id=user_id).filter_by(key=key).delete()


def get_keys(user_id):
    return Key.query.filter_by(user_id=user_id).all()


def get_usage():
    return Usage.query.all()


def get_usage_user(user_id):
    return []
    #return Usage.query\
    #    .join(Key, Key.key == Usage.key_id)\
    #    .add_columns(Usage.method, Usage.endpoint, Usage.method, Usage.key_id, Usage.timestamp, Key.user_id)\
    #    .all()
#.filter(Key.user_id==user_id)\

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        data, status = get_logged_in_user(request)
        token = data.get('data')

        if not token:
            return data, status

        return f(*args, **kwargs)

    return decorated


def key_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        response_fail = {
            'status': 'fail',
            'message': 'Provide a valid api key.'
        }, 401

        api_key = request.headers.get('X-API-KEY')
        if api_key:
            key = Key.query.filter_by(key=api_key).first()
            if not key:
                return response_fail

            return f(*args, **kwargs)
        else:
            return response_fail

    return decorated


def track_usage(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        new_usage = Usage(
            key_id=request.headers.get("X-API-KEY"),
            endpoint=str(request.url_rule),
            method=request.method,
            timestamp=datetime.datetime.now()
        )
        save_changes(new_usage)
        return f(*args, **kwargs)

    return decorated



