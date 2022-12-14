from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
from flask_wtf.csrf import CSRFProtect
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = "whatever"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.abspath(os.getcwd()+'\storage.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['UPLOAD_PATH'] = "static\\uploads\\posts"
app.config['AVATAR_UPLOAD_PATH'] = "static\\uploads\\avatars"
app.config['ALLOWED_IMAGE_EXTENSIONS'] = [".png", ".jpg", ".jpeg", ".gif"]

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
moment = Moment(app)
csrf = CSRFProtect(app)

from app.auth import auth
from app.core import core
from app.errors import errors

app.register_blueprint(auth)
app.register_blueprint(core)
app.register_blueprint(errors)

from app import models
