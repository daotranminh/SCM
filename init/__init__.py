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
    name = Column(String(200))
    description = Column(String(400))
    unit_amount = Column(Numeric(10, 2))
    unit = Column(String(50))
    is_organic = Column(Boolean)
    latest_version = Column(Integer, default=0)

class MaterialVersion(db.Model):
    __tablename__ = 'material_version'
    id = Column(Integer, autoincrement=True, primary_key=True)
    material_id = Column(Integer, ForeignKey(Material.id))
    unit_price = Column(Numeric(10, 2))
    version = Column(Integer)
    registered_on = Column(DateTime(), default=datetime.datetime.utcnow)
    is_current = Column(Boolean, default=True)

class Taste(db.Model):
    __tablename__ = 'taste'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(200))
    description = Column(String(400))
    registered_on = Column(DateTime(), default=datetime.datetime.utcnow)    
    
class SubFormula(db.Model):
    __tablename__ = 'subformula'
    id = Column(Integer, autoincrement=True, primary_key=True)
    taste_id = Column(Integer, ForeignKey(Taste.id))
    subformula_type = Column(Integer)
    name = Column(String(200))
    description = Column(String(400))
    note = Column(String(10000))
    total_cost = Column(Numeric(10, 2))
    has_up_to_date_cost_estimation = Column(Boolean, default=False)
    registered_on = Column(DateTime(), default=datetime.datetime.utcnow)

class Formula(db.Model):
    __tablename__ = 'formula'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(200))    
    description = Column(String(400))
    note = Column(String(10000))
    total_cost = Column(Numeric(10, 2), default=0)
    has_up_to_date_cost_estimation = Column(Boolean, default=False)
    registered_on = Column(DateTime(), default=datetime.datetime.utcnow)

class FormulaSubFormula(db.Model):
    __tablename__ = 'formula_subformula'
    id = Column(Integer, autoincrement=True, primary_key=True)
    formula_id = Column(Integer, ForeignKey(Formula.id))
    subformula_id = Column(Integer, ForeignKey(SubFormula.id))
    count = Column(Integer, default=1)

class MaterialSubFormula(db.Model):
    __tablename__ = 'material_subformula'
    id = Column(Integer, autoincrement=True, primary_key=True)
    material_id = Column(Integer, ForeignKey(Material.id))
    subformula_id = Column(Integer, ForeignKey(SubFormula.id))
    amount = Column(Numeric(10, 2))

class CostEstimation(db.Model):
    __tablename__ = 'cost_estimation'
    id = Column(Integer, autoincrement=True, primary_key=True)
    subformula_id = Column(Integer, ForeignKey(SubFormula.id))
    generated_on = Column(DateTime(), default=datetime.datetime.utcnow)
    total_cost = Column(Numeric(10, 2))
    is_current = Column(Boolean, default=True)

class MaterialVersionCostEstimation(db.Model):
    __tablename__ = 'material_version_cost_estimation'
    id = Column(Integer, autoincrement=True, primary_key=True)
    material_id = Column(Integer, ForeignKey(Material.id))
    material_version_id = Column(Integer, ForeignKey(MaterialVersion.id))
    cost_estimation_id = Column(Integer, ForeignKey(CostEstimation.id))
    unit_amount = Column(Numeric(10, 2))
    unit = Column(String(50))
    unit_price = Column(Numeric(10, 2))
    amount = Column(Numeric(10, 2))
    cost = Column(Numeric(10, 2))
    
class Topic(db.Model):
    __tablename__ = 'topic'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(200))
    description = Column(String(400))
    parent_id = Column(Integer, default=-1)

class DecorationForm(db.Model):
    __tablename__ = 'decoration_form'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(200))
    description = Column(String(400))

class DecorationTechnique(db.Model):
    __tablename__ = 'decoration_technique'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(200))
    description = Column(String(400))
  
class Customer(db.Model):
    __tablename__ = 'customer'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(200))
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
    name = Column(String(200))
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
    order_status = Column(Integer, default=0)
    delivered_on = Column(DateTime())
    payment_status = Column(Integer, default=0)    
    paid_on = Column(DateTime())
    is_fixed = Column(Boolean, default=False)
    total_cost = Column(Numeric(10, 2))
    has_up_to_date_cost_estimation = Column(Boolean, default=False)
    price_to_customer = Column(Numeric(10, 2))
    paid_by_customer = Column(Numeric(10, 2))

class Product(db.Model):
    __tablename__ = 'product'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(100))
    order_id = Column(Integer, ForeignKey(Order.id))    
    decoration_form_id = Column(Integer, ForeignKey(DecorationForm.id))
    decoration_technique_id = Column(Integer, ForeignKey(DecorationTechnique.id))
    formula_id = Column(Integer, ForeignKey(Formula.id))    
    sample_images_group_id = Column(Integer, ForeignKey(SampleImagesGroup.id))
    box_status = Column(Integer, default=0)
    box_returned_on = Column(DateTime())
    is_fixed = Column(Boolean, default=False)
    total_cost = Column(Numeric(10, 2))
    has_up_to_date_cost_estimation = Column(Boolean, default=False)
    price_to_customer = Column(Numeric(10, 2))
    amount = Column(Integer, default=1)

class ProductCostEstimation(db.Model):
    __tablename__ = 'product_cost_estimation'
    id = Column(Integer, autoincrement=True, primary_key=True)
    product_id = Column(Integer, ForeignKey(Product.id))
    cost_estimation_id = Column(Integer, ForeignKey(CostEstimation.id))
    last_updated_on = Column(DateTime(), default=datetime.datetime.utcnow)

class ProductImagePath(db.Model):
    __tablename__ = 'product_image_path'
    id = Column(Integer, autoincrement=True, primary_key=True)
    product_id = Column(Integer, ForeignKey(Product.id))
    file_path = Column(String(500))
    uploaded_on = Column(DateTime(), default=datetime.datetime.utcnow)

class FixedFormula(db.Model):
    __tablename__ = 'fixed_formula'
    id = Column(Integer, autoincrement=True, primary_key=True)
    product_id = Column(Integer, ForeignKey(Product.id))
    original_formula_id = Column(Integer, ForeignKey(Formula.id))
    name = Column(String(200))    
    description = Column(String(400))
    note = Column(String(10000))
    total_cost = Column(Numeric(10, 2), default=0)
    fixed_on = Column(DateTime(), default=datetime.datetime.utcnow)

class FixedSubFormula(db.Model):
    __tablename__ = 'fixed_subformula'
    id = Column(Integer, autoincrement=True, primary_key=True)
    fixed_formula_id = Column(Integer, ForeignKey(FixedFormula.id))
    original_subformula_id = Column(Integer, ForeignKey(SubFormula.id))
    taste_id = Column(Integer, ForeignKey(Taste.id))
    taste_name = Column(String(200))
    subformula_type = Column(Integer)
    name = Column(String(200))
    description = Column(String(400))
    note = Column(String(10000))
    total_cost = Column(Numeric(10, 2))
    count = Column(Integer)
    fixed_on = Column(DateTime(), default=datetime.datetime.utcnow)

class FixedMaterialSubFormula(db.Model):
    __tablename__ = 'fixed_material_subformula'
    id = Column(Integer, autoincrement=True, primary_key=True)
    fixed_subformula_id = Column(Integer, ForeignKey(FixedSubFormula.id))
    material_id = Column(Integer, ForeignKey(Material.id))
    material_version_id = Column(Integer, ForeignKey(MaterialVersion.id))
    name = Column(String(200))
    description = Column(String(400))
    is_organic = Column(Boolean)
    unit_amount = Column(Numeric(10, 2))
    unit = Column(String(50))
    unit_price = Column(Numeric(10, 2))
    amount = Column(Numeric(10, 2))
    cost = Column(Numeric(10, 2))
    fixed_on = Column(DateTime(), default=datetime.datetime.utcnow)
