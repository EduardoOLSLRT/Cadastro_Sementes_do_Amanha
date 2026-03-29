import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me')
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'


class ProductionConfig(Config):
    ENV = 'production'


class TestingConfig(Config):
    TESTING = True
