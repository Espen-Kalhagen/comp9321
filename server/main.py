from flask import Flask
from flask_restplus import Resource, Api, fields
from server.security import *
from server.ns_security import api as ns_security
from server.ns_analytics import api as ns_analytics

authorization = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

app = Flask(__name__)
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

key_parser = api.parser()
key_parser.add_argument('API Key', type='str',
                        location='headers',
                        help='API key',
                        required=True)


@api.route('/rating/<region>/<sales>')
@api.doc(params={'region': 'Region for sales of given video game', 'sales': 'Sales for given video game'})
class Rating(Resource):
    def get(self, region, sales):
        """Returns the rating."""

        # rating = getFromML(region,sales)
        rating = 60

        return {'rating': rating}


@api.route('/sales/<region>/<rating>')
@api.doc(params={'region': 'Region for sales of given video game', 'rating': 'Rating for given video game'})
class Sales(Resource):
    def get(self, region, rating):
        """Returns the sales."""

        # sales = getFromML(region, rating)
        sales = 12345

        return {'sales': sales}


@api.route('/test')
class Test(Resource):

    @key_required
    @track_usage
    def get(self):
        """Returns a test message."""
        return {'test': 'ok'}


if __name__ == '__main__':
    app.run(debug=True)
