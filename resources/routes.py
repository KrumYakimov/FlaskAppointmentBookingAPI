from resources.auth_resources import RegisterClient, LoginClient
from resources.inquiry_resources import RegisterInquiry

routes = (
    (RegisterClient, "/register"),
    (LoginClient, "/login"),
    (RegisterInquiry, "/register/inquiry"),
)

