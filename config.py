import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/recipe_db")
    # UPLOAD_FOLDER = 'app/static/uploads'  # Optional: for image uploads
