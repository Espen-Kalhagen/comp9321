from server.security import *
from flask_restplus import Resource, fields, Namespace
import pandas as pd

api = Namespace('analytics', description='API usage analytics')

usage_model = api.model('usage', {
    'key_id': fields.String(description='key id'),
    'timestamp': fields.DateTime(description='timestamp'),
    'endpoint': fields.String(description='endpoint'),
    'method': fields.String(description='method')
})

auth_parser = api.parser()
auth_parser.add_argument('Authorization', type='str',
                         location='headers',
                         help='Bearer access token',
                         required=True,
                         default='Bearer ')


@api.route('/usagelist')
class UsageList(Resource):
    @api.marshal_list_with(usage_model, envelope="data")
    def get(self):
        """Get usage log"""
        return get_usage()


@api.route('/usage')
class Usage(Resource):
    @api.doc(parser=auth_parser)
    @token_required
    def get(self):
        """Get usage statistics"""
        data, _ = get_logged_in_user(request)
        user_id = data.get("data").get("user_id")
        usage = get_usage_user(user_id)

        df = pd.DataFrame(usage, columns=['key', 'endpoint', 'method', 'timestamp', 'user_id'])
        num_requests = len(df)
        by_endpoint = df.groupby(["endpoint"])['key'].count().to_dict()
        result = {
            "num_request": num_requests,
            "by_endpoint": by_endpoint
        }
        return result, 200
