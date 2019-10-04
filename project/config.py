import datetime
import os

class BaseConfig:
    TESTING = False
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=1)


class DevConfig(BaseConfig):
    JWT_SECRET_KEY = os.getenv('SECRET_KEY')


class TestConfig(BaseConfig):
    TESTING = True
    JWT_SECRET_KEY = 'super secret test key wooo'

