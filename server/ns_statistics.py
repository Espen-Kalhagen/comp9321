import sys
import traceback

from server.security import *
from flask_restplus import Resource, fields, Namespace, reqparse, inputs
import pandas as pd
import numpy as np
from server.features import generate_features
import json

api = Namespace('statistics', description='General statistics of the data.')

vgs_csv_file = './data/Video_Games_Sales_as_at_22_Dec_2016.csv'
vgs_df_global = pd.read_csv(vgs_csv_file)

gdp_csv_file = './data/GDP.csv'
gdp_df_global = pd.read_csv(gdp_csv_file, skiprows= 4)


def clean_vgs_df():
    global vgs_df_global
    global gdp_df_global

    vgs_df_global = vgs_df_global[np.isfinite(vgs_df_global['Year_of_Release'])]

    vgs_df_global['Year_of_Release'] = vgs_df_global['Year_of_Release'].apply(
        lambda x: int(x) if not pd.isna(x) else np.nan)


clean_vgs_df()

video_game_model = api.model('video_game', {
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

groupByParser = reqparse.RequestParser()
groupByParser.add_argument('category', required=True, choices=["year", "publisher", "genre", "platform", 'developer'], help="Category to group by")
groupByParser.add_argument('sum', required=False, default=True, type=inputs.boolean, help="Whether to display sum or average")
@api.route('/groupby')
class GroupBy(Resource):
    @api.response(500, 'Server Error')
    @api.response(404, 'Incorrect groupby given')
    @api.response(200, 'Success')
    @api.expect(groupByParser, validate=True)
    @key_required
    @track_usage
    def get(self):
        """Returns the sales ($USD millions) and ratings of video games grouped by a given category"""
        vgs_df = vgs_df_global.copy(deep=True)

        args = groupByParser.parse_args()

        # retrieve the query parameters
        groupBy = args.get('category')
        sumBool = args.get('sum')

        if groupBy == "year":
            column_to_groupBy = 'Year_of_Release'
        elif groupBy == "publisher":
            column_to_groupBy = 'Publisher'
        elif groupBy == "genre":
            column_to_groupBy = 'Genre'
        elif groupBy == "platform":
            column_to_groupBy = 'Platform'
        elif groupBy == 'developer':
            column_to_groupBy = 'Developer'
        else:
            return "Invalid groupBy provided", 404

        if sumBool:
            groupby_year_df = vgs_df.groupby(column_to_groupBy).sum()
        else:
            groupby_year_df = vgs_df.groupby(column_to_groupBy).mean()

        groupby_year_df = groupby_year_df[["Global_Sales", "Critic_Score"]]

        return groupby_year_df.to_dict(), 200

@api.route('/regional_sales')
class RegionalToGlobalSales(Resource):
    @api.response(500, 'Server Error')
    # @api.response(404, 'Invalid region given')
    @api.response(200, 'Success')
    @key_required
    @track_usage
    def get(self):
        """Returns the percentage of regional video games sales to global sales"""

        vgs_df = vgs_df_global.copy(deep=True)

        vgs_df = vgs_df.groupby('Year_of_Release').sum()
        vgs_df['NA_Proportion'] = vgs_df['NA_Sales']/vgs_df['Global_Sales']
        vgs_df['JP_Proportion'] = vgs_df['JP_Sales']/vgs_df['Global_Sales']
        vgs_df['EU_Proportion'] = vgs_df['EU_Sales']/vgs_df['Global_Sales']
        vgs_df['Other_Proportion'] = vgs_df['Other_Sales']/vgs_df['Global_Sales']

        vgs_df = vgs_df[['NA_Proportion', 'JP_Proportion', 'EU_Proportion', 'Other_Proportion']]

        return vgs_df.to_dict(), 200

idParser = reqparse.RequestParser()
idParser.add_argument('ID', required=True, type=int, help="ID of video game")
@api.route('/video_game')
class VideoGames(Resource):
    @api.response(500, 'Server Error')
    @api.response(404, 'Invalid ID given')
    @api.response(200, 'Success')
    @api.expect(idParser, validate=True)
    @key_required
    @track_usage
    def get(self):
        """Returns a video game given by an ID"""
        args = idParser.parse_args()
        ID = args.get('ID')
        try:
            temp = vgs_df_global.loc[int(ID)].to_dict()
        except KeyError:
            return "Invalid ID given", 404

        return str(temp), 200

    @api.response(500, 'Server Error')
    @api.response(400, 'Validation Error')
    @api.response(201, 'User successfully created.')
    @api.expect(video_game_model, validate=True)
    @key_required
    @track_usage
    def post(self):
        """Adds a video game to data set"""
        video_game = request.json

        newID = vgs_df_global.size

        # Put the values into the dataframe
        for key in video_game:
            if key not in video_game_model.keys():
                return {"message": "Property {} is invalid".format(key)}, 400

            vgs_df_global.loc[newID, key] = video_game[key]

        newID = vgs_df_global.size

        return {"message": "Video Game {} is created".format(newID)}, 201


    @api.response(500, 'Server Error')
    @api.response(404, 'Incorrect ID given')
    @api.response(200, 'User successfully deleted')
    @api.expect(idParser, validate=True)
    @key_required
    @track_usage
    def delete(self):
        """Deletes a video game by a given ID"""
        args = idParser.parse_args()

        ID = args.get('ID')

        if ID not in vgs_df_global.index:
            api.abort(404, "Video game {} doesn't exist".format(ID))

        vgs_df_global.drop(ID, inplace=True)
        return {"message": "Video game {} is removed.".format(ID)}, 200


GDPtoSalesParser = reqparse.RequestParser()
GDPtoSalesParser.add_argument('year', required=True, type=inputs.int_range(1994,2018), help="Year to compare, between 1994-2018")
GDPtoSalesParser.add_argument('country', required=True, choices=["US", "EU", "JP"], help="Region to compare")
@api.route('/GDP_to_sales')
class GDPtoSales(Resource):
    @api.response(500, 'Server Error')
    @api.response(404, 'Invalid year given')
    @api.response(400, 'Invalid country given')
    @api.response(200, 'Success')
    @api.expect(GDPtoSalesParser, validate=True)
    @key_required
    @track_usage
    def get(self):
        """Returns the percentage of a region's GDP to video games sales within a given year"""
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
            else:
                return 'Invalid country given', 400
        except KeyError:
            print ('-'*60)
            traceback.print_exc(file=sys.stdout)
            print ('-'*60)
            return 'Invalid year given or unavaliable GDP information about year', 404

        packet = {
            'percentage' : (VG_Sales/GDP*100),
            'sales' : VG_Sales,
            'GDP' : GDP
        }

        return packet, 200

@api.route('/descriptive')
class DescriptiveStatistics(Resource):
    @key_required
    @track_usage
    def get(self):
        return json.loads(generate_features()), 200
