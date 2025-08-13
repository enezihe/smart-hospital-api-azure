import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///hospital.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEVICE_MASTER_KEY = os.getenv("DEVICE_MASTER_KEY", "dev-master-key-123")
