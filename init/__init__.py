import configparser

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import Boolean, DateTime, Column, Integer, String, LargeBinary, Numeric
from sqlalchemy import ForeignKey, ForeignKeyConstraint

config = configparser.ConfigParser()
config.read('scm.ini')

config_db = config['DBCONNECTION']
connection_string = 'postgresql://@' + config_db['host'] + ':' + config_db['port'] + '/' + config_db['db_name']

app = Flask(__name__, static_url_path='/static')
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = config['APP_CONFIG']['SECRET_KEY']
app.config['SECURITY_PASSWORD_SALT'] = config['APP_CONFIG']['SECURITY_PASSWORD_SALT']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = connection_string

db = SQLAlchemy(app)

class Material(db.Model):
    __tablename__ = 'material'
    id = Column(Integer(), autoincrement=True, primary_key=True)
    name = Column(String(50))
    unit = Column(String(50))
    unit_price = Column(Numeric(10, 2))
