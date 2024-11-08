from decouple import config
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from flask_swagger_ui import get_swaggerui_blueprint

from db import db
from resources.routes import routes


class ProductionConfig:
    FLASK_ENV = "prod"
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{config('DB_USER')}:{config('DB_PASSWORD')}"
        f"@{config('DB_HOST')}:{config('DB_PORT')}/{config('DB_NAME')}"
    )


class DevelopmentConfig:
    FLASK_ENV = "development"
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{config('DB_USER')}:{config('DB_PASSWORD')}"
        f"@{config('DB_HOST')}:{config('DB_PORT')}/{config('DB_NAME')}"
    )


class TestingConfig:
    FLASK_ENV = "testing"
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{config('DB_USER')}:{config('DB_PASSWORD')}"
        f"@localhost:{config('DB_PORT')}/{config('TEST_DB_NAME')}"
    )


def create_app(environment):
    app = Flask(__name__)
    app.config.from_object(environment)
    db.init_app(app)
    migrate = Migrate(app, db)
    api = Api(app)

    CORS(app)
    [api.add_resource(*route) for route in routes]

    # Define the Swagger UI blueprint
    SWAGGER_URL = '/swagger'
    API_URL = '/swagger.json'  # This should match where your Swagger JSON is served

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "Online Appointment Booking System"}
    )

    # Register the Swagger UI blueprint
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app
