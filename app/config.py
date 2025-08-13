import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///hospital.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Write auth
    DEVICE_MASTER_KEY = os.getenv("DEVICE_MASTER_KEY", "dev-master-key-123")

    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-prod")
    JSON_SORT_KEYS = False
    PREFERRED_URL_SCHEME = "https"
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
