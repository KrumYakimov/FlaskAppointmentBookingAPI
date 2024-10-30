from flask import request
from flask_restful import Resource
from werkzeug.exceptions import BadRequest

from managers.auth_manager import auth
from managers.inquiry_manager import InquiryManager
from models import RoleType
from schemas.request.inquiry_request_schema import InquiryRegistrationRequestSchema
from schemas.response.inquiry_response_schema import InquiryResponseSchema
from utils.decorators import permission_required, validate_schema


class Inquiries(Resource):
    @auth.login_required
    @permission_required(RoleType.APPROVER)
    def get(self, status=None):
        inquiries = InquiryManager.get_inquiries(status)
        return {"inquiries": InquiryResponseSchema().dump(inquiries, many=True)}, 200


class InquiryRegistration(Resource):
    @staticmethod
    @validate_schema(InquiryRegistrationRequestSchema)
    def post():
        try:
            data = request.get_json()
            inquiry_id = InquiryManager.register_inquiry(data)
            return {
                "message": "Inquiry registered successfully",
                "inquiry_id": inquiry_id,
            }, 201
        except BadRequest as e:
            return {"error": str(e)}, 400


class InquiryApproval(Resource):
    @auth.login_required
    @permission_required(RoleType.APPROVER)
    def put(self, inquiry_id):
        InquiryManager.approve_inquiry(inquiry_id)
        return {"message": "Inquiry approved successfully"}, 200


class InquiryRejection(Resource):
    @auth.login_required
    @permission_required(RoleType.APPROVER)
    def put(self, inquiry_id):
        InquiryManager.reject_inquiry(inquiry_id)
        return {"message": "Inquiry rejected successfully"}, 200


class InquiryNoShowStatus(Resource):
    @auth.login_required
    @permission_required(RoleType.APPROVER)
    def put(self, inquiry_id):
        InquiryManager.no_show_inquiry(inquiry_id)
        return {"message": "Inquiry no showed successfully"}, 200
