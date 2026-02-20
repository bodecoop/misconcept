from decouple import config

class Config:
    # Oracle Autonomous Database configuration
    DB_USER = config('DB_USER', cast=str)
    DB_PASSWORD = config('DB_PASSWORD', cast=str)
    DB_DSN = config('DB_DSN', cast=str)
    # DB_WALLET_LOCATION = config('DB_WALLET_LOCATION', cast=str)
    # DB_WALLET_PASSWORD = config('DB_WALLET_PASSWORD', cast=str)

    # JWT configuration
    SECRET_KEY = config('SECRET_KEY', cast=str)
    ALGORITHM = config('ALGORITHM', default='HS256', cast=str)
    ACCESS_TOKEN_EXPIRE_MINUTES = config('ACCESS_TOKEN_EXPIRE_MINUTES', default=30, cast=int)

    # Upload configuration
    UPLOAD_DIR = config('UPLOAD_DIR', default='uploads', cast=str)

config = Config()