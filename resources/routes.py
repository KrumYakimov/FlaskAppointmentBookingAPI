from resources.auth_resources import RegisterClient, LoginClient

routes = (
    (RegisterClient, "/register"),
    (LoginClient, "/login"),
)

