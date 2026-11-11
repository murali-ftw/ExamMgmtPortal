# One shared database object; models and app.py all import db from here.
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
