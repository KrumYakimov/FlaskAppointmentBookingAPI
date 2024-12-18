from resources.appointment_resourses import (
    CustomerAppointmentBooking,
    CustomerAppointmentEditing,
    CustomerAppointmentCancellation,
    CustomerAppointments, AvailableSlots, StaffAppointmentConfirmation, StaffAppointmentRejection,
    StaffAppointmentNoShow, StaffAppointmentCancellation, StaffAppointmentCompletion,
)
from resources.auth_resources import (
    ClientRegistration,
    Login,
    ChangePassword,
    ClientDeactivation,
    UserDeactivation,
    ClientEditing,
    UserRegistration,
    ClientProfile,
    UserEditing,
    UserProfile,
)
from resources.categories_resources import (
    CategoryRegistration,
    CategoryProfile,
    CategoryEditing,
    CategoryDeactivate,
)
from resources.inquiry_resources import (
    InquiryRegistration,
    InquiryApproval,
    InquiryRejection,
    InquiryNoShowStatus,
    Inquiries,
)
from resources.providers_resources import (
    ProviderRegistration,
    ProviderEditing,
    ProviderProfile,
    ProviderDeactivate,
)
from resources.services_resources import (
    ServiceRegistration,
    ServiceProfile,
    ServiceEditing,
    ServiceDeactivate,
)
from resources.subcategories_resources import (
    SubCategoryRegistration,
    SubCategoryProfile,
    SubCategoryEditing,
    SubCategoryDeactivate,
)
from resources.working_hours_resources import (
    WorkingHourProfile,
    WorkingHourRegistration,
    WorkingHourEditing,
    WorkingHourDeactivate,
)
from static.swagger import SwaggerJson

routes = (
    # UserManagement API #
    (
        # POST to register a client
        ClientRegistration,
        "/clients",
    ),
    (
        # POST for user login
        Login,
        "/login",
    ),
    (
        # POST to change password
        ChangePassword,
        "/change-password",
    ),
    (
        # GET to view client profile
        ClientProfile,
        "/clients/profile",
    ),
    (
        # PUT to edit client profile
        ClientEditing,
        "/clients/profile/edit",
    ),
    (
        # PUT to deactivate client
        ClientDeactivation,
        "/clients/profile/deactivate",
    ),
    (
        # POST to register users
        UserRegistration,
        "/users",
    ),
    (
        # GET to view client profile
        UserProfile,
        "/users/profile",
        "/users/profile/<string:status>",
        "/users/profile/<int:user_id>",
    ),
    (
        # PUT to edit client profile
        UserEditing,
        "/users/<int:user_id>/edit/",
    ),
    (
        # PUT to deactivate a user by admin
        UserDeactivation,
        "/users/<int:user_id>/deactivate",
    ),
    # InquiryManagement API
    (
        # POST to register an inquiry
        InquiryRegistration,
        "/inquiries",
    ),
    (
        # GET for inquiries with optional status
        Inquiries,
        "/approver/inquiries",
        "/approver/inquiries/<string:status>",
    ),
    (
        # PUT to approve an inquiry
        InquiryApproval,
        "/approver/inquiries/<int:inquiry_id>/approval",
    ),
    (
        # PUT to reject an inquiry
        InquiryRejection,
        "/approver/inquiries/<int:inquiry_id>/rejection",
    ),
    (
        # PUT to mark an inquiry as no-show
        InquiryNoShowStatus,
        "/approver/inquiries/<int:inquiry_id>/no-show",
    ),
    # ServiceProviderManagement API
    (
        # POST to register a service provider by the approver
        ProviderRegistration,
        "/provider",
    ),
    (
        # GET to view provider profile by the approver
        ProviderProfile,
        "/providers/profile",
        "/providers/profile/<string:status>",
        "/providers/profile/<int:provider_id>",
    ),
    (
        # PUT to edit provider profile by the approver
        ProviderEditing,
        "/provider/<int:provider_id>/edit/",
    ),
    (
        # PUT to deactivate a provider by the approver
        ProviderDeactivate,
        "/provider/<int:provider_id>/deactivate",
    ),
    # ServiceManagement API
    (
        # POST to register a service by the approver
        ServiceRegistration,
        "/services",
    ),
    (
        # GET to view services by the approver
        ServiceProfile,
        "/services/profile",
        "/services/profile/<string:status>",
        "/services/profile/<int:service_id>",
    ),
    (
        # PUT to edit a service profile by the approver
        ServiceEditing,
        "/services/<int:service_id>/edit",
    ),
    (
        # PUT to deactivate a service by the approver
        ServiceDeactivate,
        "/services/<int:service_id>/deactivate",
    ),
    # ServiceCategoryManagement API
    (
        # POST to register a service category by the approver
        CategoryRegistration,
        "/categories",
    ),
    (
        # GET to view service categories by the approver
        CategoryProfile,
        "/categories/profile",
        "/categories/profile/<string:status>",
        "/categories/profile/<int:category_id>",
    ),
    (
        # PUT to edit a service category profile by the approver
        CategoryEditing,
        "/categories/<int:category_id>/edit",
    ),
    (
        # PUT to deactivate a service category by the approver
        CategoryDeactivate,
        "/categories/<int:category_id>/deactivate",
    ),
    # ServiceSubCategoryManagement API
    (
        # POST to register a service subcategory by the approver
        SubCategoryRegistration,
        "/subcategories",
    ),
    (
        # GET to view service subcategories by the approver
        SubCategoryProfile,
        "/subcategories/profile",
        "/subcategories/profile/<string:status>",
        "/subcategories/profile/<int:subcategory_id>",
    ),
    (
        # PUT to edit a service subcategory by the approver
        SubCategoryEditing,
        "/subcategories/<int:subcategory_id>/edit",
    ),
    (
        # PUT to deactivate a service subcategory by the approver
        SubCategoryDeactivate,
        "/subcategories/<int:subcategory_id>/deactivate",
    ),
    # WorkingHourManagement API
    (
        # POST to register a service subcategory by the approver
        WorkingHourProfile,
        "/working_hours/profile",
        "/working_hours/profile/provider/<int:provider_id>",
        "/working_hours/profile/employee/<int:employee_id>",
    ),
    (
        # POST to register working our for provider and staff
        WorkingHourRegistration,
        "/working_hours/register",
    ),
    (
        # PUT to edit a working hours
        WorkingHourEditing,
        "/working_hours/<int:working_hours_id>/edit",
    ),
    (
        # PUT to deactivate a working hours
        WorkingHourDeactivate,
        "/working_hours/<int:working_hours_id>/deactivate",
    ),
    # AppointmentManagement API
    (
        AvailableSlots,
        "/appointments/available_slots/<int:staff_id>/<int:service_id>/<string:date>"
    ),
    (
        CustomerAppointmentBooking,
        "/appointments"
    ),
    (
        CustomerAppointments,
        "/appointments/info"
    ),
    (
        CustomerAppointmentEditing,
        "/appointments/<int:appointment_id>/edit"
    ),
    (
        CustomerAppointmentCancellation,
        "/appointments/<int:appointment_id>/cancel"
    ),
    (
        StaffAppointmentConfirmation,
        "/appointments/<int:appointment_id>/confirm"
    ),

    (
        StaffAppointmentRejection,
        "/appointments/<int:appointment_id>/reject"
    ),

    (
        StaffAppointmentNoShow,
        "/appointments/<int:appointment_id>/no_show"
    ),

    (
        StaffAppointmentCancellation,
        "/appointments/<int:appointment_id>/cancel"
    ),
    (
        StaffAppointmentCompletion,
        "/appointments/<int:appointment_id>/complete"
    ),

    # Swagger
    (
        SwaggerJson,
        "/swagger.json"
    ),
)


