from flask import Flask
from flask_restplus import Resource, Api, fields, Namespace
from server.security import *
from server.ns_prediction import api as ns_prediction
from server.ns_security import api as ns_security
from server.ns_analytics import api as ns_analytics
from server.ns_client import api as ns_client
from server.ns_statistics import api as ns_statistics

authorization = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

app = Flask(__name__, static_url_path='')
app.config.setdefault('RESTPLUS_MASK_SWAGGER', False)
app.app_context().push()
auth_init(app)
api = Api(app,
          title='Predict-a-thon',
          version='1.0',
          description="The goal of this API is to help users, developers and publishers understand rating and sales of"
                      "games through correlation using deep learning and data aggregation.",
          authorizations=authorization,
          security='apikey')

api.add_namespace(ns_security)
api.add_namespace(ns_analytics)
api.add_namespace(ns_prediction)
api.add_namespace(ns_client)
api.add_namespace(ns_statistics)


@api.route('/test')
class Test(Resource):

    @key_required
    @track_usage
    def get(self):
        """Returns a test message."""
        return {'test': 'ok'}


@app.after_request
def apply_cors(response):
    response.headers.set("Access-Control-Allow-Origin", "http://127.0.0.1:5000")
    response.headers.set("Access-Control-Allow-Credentials", "true")
    response.headers.set("Access-Control-Allow-Methods", "GET,HEAD,OPTIONS,POST,PUT")
    response.headers.set("Access-Control-Allow-Headers",
                       "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers")
    return response


if __name__ == '__main__':
    app.run(debug=True)
