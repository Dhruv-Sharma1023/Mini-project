from flask import Flask
from config import config


def create_app(config_name: str = "default") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialise DB schema (idempotent)
    from app.database.schema import init_db
    init_db(db_path=app.config["DB_PATH"])

    # Blueprints
    from app.routes import main_bp
    from app.auth  import auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app
