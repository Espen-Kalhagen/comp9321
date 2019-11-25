from flask_restplus import Resource, Api, fields, Namespace
from server.security import *
from server.neuralnet import *

api = Namespace('predict', description='Use neural net to predict sales or critic score')

neuralnet = Neuralnet()

region_choises = ('EU', 'NA','JP','Others')
year_choises = list(range(1994,2020))

rating_parser = api.parser()
rating_parser.add_argument('year', type=int, choices=year_choises, help='The games release year', required=True)
rating_parser.add_argument('region', choices=region_choises, help='The games sales numbers corresponding region', required=True)
rating_parser.add_argument('sales', type=int,choices=list(range(0,41)), help='The games sales number', required=True)


@api.route('/rating')
class Rating(Resource):

    @api.expect(rating_parser)
    @key_required
    @track_usage
    def get(self):
        """Returns prediction of avarage critic score"""
        args = rating_parser.parse_args(strict=True)

        rating = neuralnet.predictRating(args.year,args.region,args.sales)
        print(rating)
        return {'rating': rating}


sales_parser = api.parser()
sales_parser.add_argument('year', type=int, choices=year_choises, help='The games release year', required=True)
sales_parser.add_argument('region', choices=region_choises, help='The games sales numbers corresponding region', required=True)
sales_parser.add_argument('rating', type=int,choices=list(range(0,100)), help='The games avarage critics rating', required=True)


@api.route('/sales')
class Sales(Resource):

    @api.expect(sales_parser)
    @key_required
    @track_usage
    def get(self):
        """Returns prediction of number of sales"""
        args = sales_parser.parse_args(strict=True)

        sales = neuralnet.predictSales(year=args.year,region=args.region,rating=args.rating)
        print(sales)
    
        return {'sales': sales}