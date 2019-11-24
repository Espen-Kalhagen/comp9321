from flask import Flask, abort
from flask_restplus import Resource, Api, fields, reqparse
import numpy as np
import sys, traceback
# from security import *

import pandas as pd

app = Flask(__name__)
app.app_context().push()
# auth_init(app)
api = Api(app)

vgs_csv_file = '../Video_Games_Sales_as_at_22_Dec_2016.csv'
vgs_df_global = pd.read_csv(vgs_csv_file)

gdp_csv_file = '../GDP.csv'
gdp_df_global = pd.read_csv(gdp_csv_file)

def clean_vgs_df():
    global vgs_df_global
    global gdp_df_global

    vgs_df_global = vgs_df_global[np.isfinite(vgs_df_global['Year_of_Release'])]

    vgs_df_global['Year_of_Release'] = vgs_df_global['Year_of_Release'].apply(
        lambda x: int(x) if not pd.isna(x) else np.nan)

clean_vgs_df()

# ns_security = api.namespace('security', description='Authorization and API key management')

# user_model = api.model('user', {
#     'username': fields.String(required=True, description='user username'),
#     'password': fields.String(required=True, description='user password')
# })

# key_model = api.model('key', {
#     'key': fields.String(required=True, description='API key')
# })

video_game_model = api.model('key', {
    'Name' : fields.String(required=True, description='Name of video game'),
    'Platform' : fields.String(required=False, description='Platform of video game'),
    'Year_of_Release' : fields.Integer(required=True, description='Year of video game\'s release'),
    'Genre' : fields.String(required=False, description='Genre of video game'),
    'Publisher' : fields.String(required=False, description='Publisher of video game'),
    'NA_Sales' : fields.Float(required=True, description='North American sales of video game'),
    'EU_Sales' : fields.Float(required=True, description='European Union sales of video game'),
    'JP_Sales' : fields.Float(required=True, description='Japanese sales of video game'),
    'Other_Sales' : fields.Float(required=True, description='Other countries sales of video game'),
    'Global_Sales' : fields.Float(required=True, description='Global sales of video game'),
    'Critic_Score' : fields.Float(required=True, description='Critical score of video game'),
    'Critic_Count' : fields.Integer(required=True, description='Critic count of video game'),
    'User_Score' : fields.Float(required=True, description='User score of video game'),
    'User_Count' : fields.Integer(required=True, description='User count of video game'),
    'Developer' : fields.String(required=False, description='Developer of video game'),
    'Rating' : fields.String(required=False, description='Rating of video game')
})

# @ns_security.route('/login')
# class UserLogin(Resource):
#     """
#         User Login Resource
#     """
#     @api.doc('user login')
#     @api.expect(user_model, validate=True)
#     def post(self):
#         """Returns a bearer token after successful authentication."""
#         post_data = request.json
#         return login_user(data=post_data)


# @ns_security.route('/users')
# class UserList(Resource):
#     @api.response(201, 'User successfully created.')
#     @api.expect(user_model, validate=True)
#     def post(self):
#         """Creates a new User """
#         data = request.json
#         return save_new_user(data=data)


# @ns_security.route('/keys')
# class KeyList(Resource):

#     @token_required
#     def post(self):
#         """Create a new api key"""
#         data, _ = get_logged_in_user(request)
#         user_id = data.get("data").get("user_id")
#         key = create_key(user_id)
#         return {
#                    "message": "Key successfully created.",
#                    "data": {"key": key}
#                }, 201

#     @token_required
#     @api.marshal_list_with(key_model, envelope="data")
#     def get(self):
#         """Get all api keys for the logged in user"""
#         data, _ = get_logged_in_user(request)
#         user_id = data.get("data").get("user_id")
#         return get_keys(user_id)

#     @token_required
#     def delete(self, key):
#         """Remove a certain api key"""
#         data, _ = get_logged_in_user(request)
#         user_id = data.get("data").get("user_id")
#         return delete_key(user_id, key)

groupByParser = reqparse.RequestParser()
groupByParser.add_argument('category', required=True, default="year", choices=["year", "publisher"], help="Category must be year or publisher")
@api.route('/groupby')
@api.doc(params={'category': 'Category to group by, i.e. [year, publisher]'})
class GroupBy(Resource):
    def get(self):
        vgs_df = vgs_df_global.copy(deep=True)

        args = groupByParser.parse_args()

        # retrieve the query parameters
        groupBy = args.get('category')

        if groupBy == "year":
            groupby_year_df = vgs_df.groupby('Year_of_Release').mean()
            groupby_year_df = groupby_year_df[["Global_Sales", "Critic_Score"]]
        elif groupBy == "publisher":
            groupby_year_df = vgs_df.groupby('Publisher').mean()
            groupby_year_df = groupby_year_df[["Global_Sales", "Critic_Score"]]

        return groupby_year_df.to_dict()

GDPtoSalesParser = reqparse.RequestParser()
GDPtoSalesParser.add_argument('year', required=False, default=2000)
GDPtoSalesParser.add_argument('country', required=False, default="US", choices=["US", "EU", "JP"])
@api.route('/GDP_to_sales')
@api.doc(params={'year' : 'Year to compare', 'country' : 'Country to compare, i.e US (United Stares), EU (European Union), JP (Japan)'})
class GDPtoSales(Resource):
    def get(self):
        """Returns the percentage of GDP that the video game sales made up"""
        gdp_df = gdp_df_global.copy(deep=True) 
        vgs_df = vgs_df_global.copy(deep=True)

        args = GDPtoSalesParser.parse_args()

        country = args.get('country')
        year = args.get('year')

        gdp_df = gdp_df.set_index('Country Code')
        vgs_df = vgs_df.groupby('Year_of_Release').sum()

        try:
            if country == "US":
                VG_Sales = vgs_df.at[int(year), 'NA_Sales']*1000000
                GDP = gdp_df.at['USA',str(year)]
            elif country == "EU":
                VG_Sales = vgs_df.at[int(year), 'EU_Sales']*1000000
                GDP = gdp_df.at['EUU',str(year)]
            elif country == "JP":
                VG_Sales = vgs_df.at[int(year), 'JP_Sales']*1000000
                GDP = gdp_df.at['JPN',str(year)]
        except KeyError:
            print ('-'*60)
            traceback.print_exc(file=sys.stdout)
            print ('-'*60)
            abort(400, 'Invalid year')

        return {
            'percentage' : (VG_Sales/GDP*100),
            'sales' : VG_Sales,
            'GDP' : GDP
        }

#to put into video games
    # @api.response(201, 'User successfully created.')
    # @api.expect(video_game_model, validate=True)


@api.route('/rating/<region>/<sales>')
@api.doc(params={'region': 'Region for sales of given video game', 'sales':'Sales for given video game'})
class Rating(Resource):
    def get(self, region, sales):
        """Returns the rating."""

        # rating = getFromML(region,sales)
        rating = 60

        return {'rating': rating}


@api.route('/sales/<region>/<rating>')
@api.doc(params={'region': 'Region for sales of given video game', 'rating':'Rating for given video game'})
class Sales(Resource):
    def get(self, region, rating):
        """Returns the sales."""

        # sales = getFromML(region, rating)
        sales = 12345

        return {'sales': sales}


# @api.route('/test')
# class Test(Resource):

#     @key_required
#     def get(self):
#         """Returns a test message."""
#         return {'test': 'ok'}


if __name__ == '__main__':
    app.run(debug=True)