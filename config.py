# import os
# from dotenv import load_dotenv
# load_dotenv()


# class Config:
#     SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
#     SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///study_planner.db")
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
    
#     GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    
    # Database Configuration - prioritize production DATABASE_URL
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or os.environ.get("DATABASE_URL", "sqlite:///study_planner.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Gemini API Configuration
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    
    # Production settings
    DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
