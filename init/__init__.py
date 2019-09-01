import configparser
import datetime

from flask import Flask
from flask_babel import Babel
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
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(50))
    description = Column(String(400))
    unit = Column(String(50))
    is_organic = Column(Boolean)

class MaterialVersion(db.Model):
    __tablename__ = 'material_version'
    id = Column(Integer, autoincrement=True, primary_key=True)
    material_id = Column(Integer, ForeignKey(Material.id))
    unit_price = Column(Numeric(10, 2))
    registered_on = Column(DateTime(), default=datetime.datetime.utcnow)    

class Taste(db.Model):
    __tablename__ = 'taste'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(50))
    description = Column(String(400))
    
class Formula(db.Model):
    __tablename__ = 'formula'
    id = Column(Integer, autoincrement=True, primary_key=True)
    taste_id = Column(Integer, ForeignKey(Taste.id))
    name = Column(String(50))
    description = Column(String(400))

class MaterialVersionFormula(db.Model):
    __tablename__ = 'material_version_formula'
    id = Column(Integer, autoincrement=True, primary_key=True)
    material_version_id = Column(Integer, ForeignKey(MaterialVersion.id))
    formula_id = Column(Integer, ForeignKey(Formula.id))
    ammount = Column(Numeric(10, 2))
    cost = Column(Numeric(10, 2))
    
class Topic(db.Model):
    __tablename__ = 'topic'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(50))
    description = Column(String(400))
    
class Decoration(db.Model):
    __tablename__ = 'decoration'
    id = Column(Integer, autoincrement=True, primary_key=True)
    topic_id = Column(Integer, ForeignKey(Topic.id))
    form = Column(Integer)
    technique = Column(Integer)
    template_path = Column(String(400))
    
class Customer(db.Model):
    __tablename__ = 'customer'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(50))
    address = Column(String(200))
    phone = Column(String(50))
    email_address = Column(String(200))
    facebook = Column(String(200))    
    recommended_by = Column(Integer, default=-1)
    registered_on = Column(DateTime(), default=datetime.datetime.utcnow)

class Order(db.Model):
    __tablename__ = 'order'
    id = Column(Integer, autoincrement=True, primary_key=True)
    customer_id = Column(Integer, ForeignKey(Customer.id))
    taste_id = Column(Integer, ForeignKey(Taste.id))
    decoration_id = Column(Integer, ForeignKey(Decoration.id))
    message = Column(String(200))
    ordered_on = Column(DateTime(), default=datetime.datetime.utcnow)
    delivered_on = Column(DateTime())
    deliver_method = Column(Integer)

class Cake(db.Model):
    __tablename__ = 'cake'
    id = Column(Integer, autoincrement=True, primary_key=True)
    order_id = Column(Integer, ForeignKey(Order.id))
    formula_id = Column(Integer, ForeignKey(Formula.id))
    cost = Column(Numeric(10, 2))    
    photos_path = Column(String(400))
