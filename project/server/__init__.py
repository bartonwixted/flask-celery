import os

from flask import Flask
from project.server.extensions import celery, db
from flask_login import LoginManager


DB_NAME = "database.db"


def create_app(script_info=None):

    # instantiate the app
    app = Flask(
        __name__,
        template_folder="../client/templates",
        static_folder="../client/static",
    )

    app.config['SECRET_KEY'] = 'TakeMeToChurch9'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    celery.init_app(app)
    # set config
    app_settings = os.getenv("APP_SETTINGS")
    app.config.from_object(app_settings)

    # register blueprints
    from project.server.main.views import main_blueprint

    app.register_blueprint(main_blueprint)

    from project.server.main.models import User

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # shell context for flask cli
    app.shell_context_processor({"app": app})

    return app


def create_database(app):
    if not os.path.exists('server/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
