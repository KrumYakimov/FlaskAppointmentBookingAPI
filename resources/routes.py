from resources.auth_resources import ClientRegistration, Login, ChangePassword, ClientDeactivation, UserDeactivation, \
    ClientEditing, UserRegistration, ClientProfile, UserEditing, UserProfile
from resources.inquiry_resources import InquiryRegistration, InquiryApproval, InquiryRejection, InquiryNoShowStatus,Inquiries

routes = (

    # UserManagement API #

    (ClientRegistration, "/clients"),  # POST to register a client
    (Login, "/login"),  # POST for user login
    (ChangePassword, "/change-password"),  # POST to change password
    (ClientProfile, "/clients/profile"),  # GET to view client profile
    (ClientEditing, "/clients/profile/edit"),  # PUT to edit client profile
    (ClientDeactivation, "/clients/profile/deactivate"),  # PUT to deactivate client
    (UserRegistration, "/users"),  # POST to register users
    (UserProfile, "/users/profile", "/users/profile/<string:status>", "/users/profile/<int:user_id>"), # GET to view client profile
    (UserEditing, "/users/<int:user_id>/edit/"),  # PUT to edit client profile
    (UserDeactivation, "/users/<int:user_id>/deactivate"),  # PUT to deactivate a user by admin

    # InquiryManagement API

    (InquiryRegistration, "/inquiries"),  # POST to register an inquiry
    (Inquiries, "/approver/inquiries", "/approver/inquiries/<string:status>"),  # GET for inquiries with optional status
    (InquiryApproval, "/approver/inquiries/<int:inquiry_id>/approval"),  # PUT to approve an inquiry
    (InquiryRejection, "/approver/inquiries/<int:inquiry_id>/rejection"),  # PUT to reject an inquiry
    (InquiryNoShowStatus, "/approver/inquiries/<int:inquiry_id>/no-show")  # PUT to mark an inquiry as no-show
)



