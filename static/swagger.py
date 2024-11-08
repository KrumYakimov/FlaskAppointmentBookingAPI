from flask_restful import Resource
from flask import send_from_directory


class SwaggerJson(Resource):
    @staticmethod
    def get():
        return send_from_directory('static', 'swagger.json')
