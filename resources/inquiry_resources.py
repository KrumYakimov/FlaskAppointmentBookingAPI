from flask_restful import Resource
from flask import request
from werkzeug.exceptions import BadRequest
from manager.inquiry_manager import InquiryManager


class RegisterInquiry(Resource):
    @staticmethod
    def post():
        try:
            data = request.get_json()
            inquiry_id = InquiryManager.register_inquiry(data)
            return {"message": "Inquiry registered successfully", "inquiry_id": inquiry_id}, 201
        except BadRequest as e:
            return {"error": str(e)}, 400
