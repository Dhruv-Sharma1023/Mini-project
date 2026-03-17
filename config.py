import os

_BASE     = os.path.abspath(os.path.dirname(__file__))
_INSTANCE = os.path.join(_BASE, "instance")


class Config:
    SECRET_KEY  = os.environ.get("SECRET_KEY", "emailiq-secret-2025-change-me")
    DEBUG       = False
    TESTING     = False
    MODEL_DIR   = os.path.join(_BASE, "models")
    DB_PATH     = os.path.join(_INSTANCE, "emailiq.db")
    # Session cookie settings
    SESSION_COOKIE_HTTPONLY  = True
    SESSION_COOKIE_SAMESITE  = "Lax"
    PERMANENT_SESSION_LIFETIME = 3600   # 1 hour


class DevelopmentConfig(Config):
    DEBUG   = True
    DB_PATH = os.path.join(_INSTANCE, "emailiq_dev.db")


class ProductionConfig(Config):
    DEBUG      = False
    SECRET_KEY = os.environ.get("SECRET_KEY")
    DB_PATH    = os.environ.get("DB_PATH", os.path.join(_INSTANCE, "emailiq.db"))


class TestingConfig(Config):
    TESTING = True
    DEBUG   = True
    DB_PATH = os.path.join(_INSTANCE, "emailiq_test.db")


config = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "testing":     TestingConfig,
    "default":     DevelopmentConfig,
}
