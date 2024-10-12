from flask import request
from flask_restful import Resource

from manager.client_manager import ClientManager


class RegisterClient(Resource):
    @staticmethod
    def post():
        data = request.get_json()
        token = ClientManager.register(data)
        return {"token": token}, 201


class LoginClient(Resource):
    @staticmethod
    def post():
        data = request.get_json()
        token = ClientManager.login(data)
        return {"token": token}





