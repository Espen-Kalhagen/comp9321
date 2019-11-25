from server.security import *
from flask_restplus import Resource, fields, Namespace

api = Namespace('security', description='Authorization and API key management')

key_model = api.model('key', {
    'key': fields.String(required=True, description='API key')
})

user_model = api.model('user', {
    'username': fields.String(required=True, description='user username'),
    'password': fields.String(required=True, description='user password')
})

auth_parser = api.parser()
auth_parser.add_argument('Authorization', type='str',
                         location='headers',
                         help='Bearer access token',
                         required=True,
                         default='Bearer ')


@api.route('/login')
class UserLogin(Resource):
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


@api.route('/keys')
class KeyList(Resource):

    @api.doc(parser=auth_parser)
    @token_required
    def post(self):
        """Create a new api key"""
        data, _ = get_logged_in_user(request)
        user_id = data.get("data").get("user_id")
        key = create_key(user_id)
        return {
                   "message": "Key successfully created.",
                   "key": key
               }, 201

    @api.doc(parser=auth_parser)
    @token_required
    @api.marshal_list_with(key_model, envelope="data")
    def get(self):
        """Get all api keys for the logged in user"""
        data, _ = get_logged_in_user(request)
        user_id = data.get("data").get("user_id")
        return get_keys(user_id)

    @api.doc(parser=auth_parser)
    @token_required
    def delete(self, key):
        """Remove a certain api key"""
        data, _ = get_logged_in_user(request)
        user_id = data.get("data").get("user_id")
        return delete_key(user_id, key)
