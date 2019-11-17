from flask import Flask
from flask_restplus import Resource, Api, fields

app = Flask(__name__)
api = Api(app)


@api.route('/test')
class Test(Resource):
    def get(self):
        """Returns a test message."""
        return {'test': 'ok'}


if __name__ == '__main__':
    app.run(debug=True)