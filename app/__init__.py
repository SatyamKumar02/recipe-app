from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from pymongo import MongoClient
from app.models import User
from config import Config

# from app.routes.auth import auth as auth_blueprint
# from app.routes.views import views as views_blueprint

csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"

db = None  # Global DB variable

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # MongoDB
    client = MongoClient(app.config["MONGO_URI"])
    global db
    db = client.get_default_database()

    # Extensions
    csrf.init_app(app)
    login_manager.init_app(app)

    # Blueprints
    from app.routes.auth import auth as auth_blueprint
    from app.routes.views import views as views_blueprint

    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    app.register_blueprint(views_blueprint)

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User  # ensure circular import doesn't break
    return User.get_by_id(db, user_id)
