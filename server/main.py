from flask import Flask
from flask_restplus import Resource, Api, fields
from server.auth import *

app = Flask(__name__)
app.app_context().push()
auth_init(app)
api = Api(app)

user_model = api.model('user', {
    'username': fields.String(required=True, description='user username'),
    'password': fields.String(required=True, description='user password')
})


@api.route('/login')
class UserLogin(Resource):
    """
        User Login Resource
    """
    @api.doc('user login')
    @api.expect(user_model, validate=True)
    def post(self):
        """Returns a bearer token after successful authentication."""
        post_data = request.json
        return login_user(data=post_data)


@api.route('/users')
class UserList(Resource):
    @api.response(201, 'User successfully created.')
    @api.expect(user_model, validate=True)
    def post(self):
        """Creates a new User """
        data = request.json
        return save_new_user(data=data)


@api.route('/test')
class Test(Resource):

    @token_required
    def get(self):
        """Returns a test message."""
        return {'test': 'ok'}


if __name__ == '__main__':
    app.run(debug=True)