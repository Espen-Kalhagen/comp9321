from server.security import *
from flask_restplus import Resource, fields, Namespace

api = Namespace('analytics', description='API usage analytics')

usage_model = api.model('usage', {
    'key_id': fields.String(description='key id'),
    'timestamp': fields.DateTime(description='timestamp'),
    'endpoint': fields.String(description='endpoint'),
    'method': fields.String(description='method')
})

stats_model = api.model('stats', {
    'key_id': fields.String(description='key id'),
    'timestamp': fields.String(description='timestamp'),
    'endpoint': fields.String(description='endpoint'),
    'method': fields.String(description='method'),
    'user_id': fields.String(description='username')
})

usage_parser = api.parser()
#usage_parser.add_argument()


@api.route('/usagelist')
class UsageList(Resource):
    @api.marshal_list_with(usage_model, envelope="data")
    def get(self):
        """Get usage log"""
        return get_usage()


@api.route('/usage')
class Usage(Resource):
    @api.marshal_list_with(stats_model, envelope="data")
    @token_required
    def get(self):
        """Get usage statistics"""
        data, _ = get_logged_in_user(request)
        user_id = data.get("data").get("user_id")
        return get_usage_user(user_id)
