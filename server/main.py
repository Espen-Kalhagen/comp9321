from flask import Flask, jsonify
from flask_restplus import Resource, Api, fields
import json

app = Flask(__name__)
api = Api(app)


@api.route('/rating/<region>/<sales>')
@api.doc(params={'region': 'Region for sales of given video game', 'sales':'Sales for given video game'})
class Rating(Resource):
    def get(self, region, sales):
        """Returns the rating."""

        return {'rating': '60'}

@api.route('/sales/<region>/<rating>')
@api.doc(params={'region': 'Region for sales of given video game', 'rating':'Rating for given video game'})
class Sales(Resource):
    def get(self, region, rating):
        """Returns the sales."""

        return {'sales': '12345'}


if __name__ == '__main__':
    app.run(debug=True)