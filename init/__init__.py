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
app.config['UPLOAD_FOLDER'] = config['APP_CONFIG']['UPLOAD_FOLDER']
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
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
    is_current = Column(Boolean, default=True)

class Taste(db.Model):
    __tablename__ = 'taste'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(50))
    description = Column(String(400))
    registered_on = Column(DateTime(), default=datetime.datetime.utcnow)    
    
class Formula(db.Model):
    __tablename__ = 'formula'
    id = Column(Integer, autoincrement=True, primary_key=True)
    taste_id = Column(Integer, ForeignKey(Taste.id))
    name = Column(String(50))
    description = Column(String(400))
    note = Column(String(5000))
    registered_on = Column(DateTime(), default=datetime.datetime.utcnow)

class MaterialFormula(db.Model):
    __tablename__ = 'material_formula'
    id = Column(Integer, autoincrement=True, primary_key=True)
    material_id = Column(Integer, ForeignKey(Material.id))
    formula_id = Column(Integer, ForeignKey(Formula.id))
    amount = Column(Numeric(10, 2))
    
class Topic(db.Model):
    __tablename__ = 'topic'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(50))
    description = Column(String(400))
    parent_id = Column(Integer, default=-1)

class DecorationForm(db.Model):
    __tablename__ = 'decoration_form'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(50))
    description = Column(String(400))

class DecorationTechnique(db.Model):
    __tablename__ = 'decoration_technique'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(50))
    description = Column(String(400))

class Decoration(db.Model):
    __tablename__ = 'decoration'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(50))
    description = Column(String(400))
    topic_id = Column(Integer, ForeignKey(Topic.id))
    decoration_form_id = Column(Integer, ForeignKey(DecorationForm.id))
    decoration_technique_id = Column(Integer, ForeignKey(DecorationTechnique.id))
    registered_on = Column(DateTime(), default=datetime.datetime.utcnow)    
    
class DecorationTemplatePath(db.Model):
    __tablename__ = 'decoration_template_path'
    id = Column(Integer, autoincrement=True, primary_key=True)
    decoration_id = Column(Integer, ForeignKey(Decoration.id))
    template_path = Column(String(400))
    
class Customer(db.Model):
    __tablename__ = 'customer'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(50))
    birthday = Column(DateTime())
    address = Column(String(200))
    phone = Column(String(50))
    email_address = Column(String(200))
    facebook = Column(String(200))    
    recommended_by = Column(Integer, default=-1)
    registered_on = Column(DateTime(), default=datetime.datetime.utcnow)
    note = Column(String(5000))

class DeliveryMethod(db.Model):
    __tablename__ = 'delivery_method'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(50))
    description = Column(String(400))

class SampleImagesGroup(db.Model):
    __tablename__ = 'sample_images_group'
    id = Column(Integer, autoincrement=True, primary_key=True)
    topic_id = Column(Integer, ForeignKey(Topic.id))
    name = Column(String(100))    

class SampleImagePath(db.Model):
    __tablename__ = 'sample_image_path'
    id = Column(Integer, autoincrement=True, primary_key=True)
    sample_images_group_id = Column(Integer, ForeignKey(SampleImagesGroup.id))
    file_path = Column(String(500))
    uploaded_on = Column(DateTime(), default=datetime.datetime.utcnow)

class Order(db.Model):
    __tablename__ = 'order'
    id = Column(Integer, autoincrement=True, primary_key=True)
    customer_id = Column(Integer, ForeignKey(Customer.id))
    registered_on = Column(DateTime(), default=datetime.datetime.utcnow)
    last_update_on = Column(DateTime(), default=datetime.datetime.utcnow)
    ordered_on = Column(DateTime(), default=datetime.datetime.utcnow)
    delivery_appointment = Column(DateTime())
    delivery_method_id = Column(Integer, ForeignKey(DeliveryMethod.id))
    message = Column(String(200))
    delivery_status = Column(Integer, default=0)
    delivered_on = Column(DateTime())
    payment_status = Column(Integer, default=0)    
    paid_on = Column(DateTime())    

class Product(db.Model):
    __tablename__ = 'product'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(100))
    order_id = Column(Integer, ForeignKey(Order.id))
    taste_id = Column(Integer, ForeignKey(Taste.id))
    decoration_form_id = Column(Integer, ForeignKey(DecorationForm.id))
    decoration_technique_id = Column(Integer, ForeignKey(DecorationTechnique.id))
    formula_id = Column(Integer, ForeignKey(Formula.id))
    sample_images_group_id = Column(Integer, ForeignKey(SampleImagesGroup.id))
    box_status = Column(Integer, default=0)
    box_returned_on = Column(DateTime())

class ProductImagePath(db.Model):
    __tablename__ = 'product_image_path'
    id = Column(Integer, autoincrement=True, primary_key=True)
    product_id = Column(Integer, ForeignKey(Product.id))
    file_path = Column(String(500))
    uploaded_on = Column(DateTime(), default=datetime.datetime.utcnow)
    
class CostEstimation(db.Model):
    __tablename__ = 'cost_estimation'
    id = Column(Integer, autoincrement=True, primary_key=True)
    formula_id = Column(Integer, ForeignKey(Formula.id))
    total_cost = Column(Numeric(10, 2))    

class MaterialVersionCostEstimation(db.Model):
    __tablename__ = 'material_version_cost_estimation'
    id = Column(Integer, autoincrement=True, primary_key=True)
    material_verion_id = Column(Integer, ForeignKey(MaterialVersion.id))
    cost_estimation_id = Column(Integer, ForeignKey(CostEstimation.id))
    ammount = Column(Numeric(10, 2))
    cost = Column(Numeric(10, 2))
