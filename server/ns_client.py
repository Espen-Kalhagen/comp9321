from flask import Flask, abort, jsonify, request, send_from_directory

from flask_restplus import Resource, Api, fields, Namespace

api = Namespace('client', description='Serves a client website')


@api.route('/')
class Client(Resource):

    def get(self):
        return send_from_directory('../client/', 'index.html')