import logging
import os
import datetime
import json
from decimal import Decimal

from flask import Flask, Response, render_template, request, flash, redirect, make_response, session, url_for
from werkzeug.utils import secure_filename

from init import app, db, config

from lib.repo.delivery_method_repository import DeliveryMethodRepository
from lib.repo.decoration_form_repository import DecorationFormRepository
from lib.repo.decoration_technique_repository import DecorationTechniqueRepository
from lib.repo.material_repository import MaterialRepository
from lib.repo.material_version_repository import MaterialVersionRepository
from lib.repo.material_subformula_repository import MaterialSubFormulaRepository
from lib.repo.material_version_cost_estimation_repository import MaterialVersionCostEstimationRepository
from lib.repo.cost_estimation_repository import CostEstimationRepository
from lib.repo.customer_repository import CustomerRepository
from lib.repo.taste_repository import TasteRepository
from lib.repo.topic_repository import TopicRepository
from lib.repo.subformula_repository import SubFormulaRepository
from lib.repo.formula_repository import FormulaRepository
from lib.repo.formula_subformula_repository import FormulaSubFormulaRepository
from lib.repo.order_repository import OrderRepository
from lib.repo.product_repository import ProductRepository
from lib.repo.product_image_path_repository import ProductImagePathRepository
from lib.repo.product_cost_estimation_repository import ProductCostEstimationRepository
from lib.repo.sample_image_path_repository import SampleImagePathRepository
from lib.repo.sample_images_group_repository import SampleImagesGroupRepository
from lib.repo.fixed_formula_repository import FixedFormulaRepository
from lib.repo.fixed_subformula_repository import FixedSubFormulaRepository
from lib.repo.fixed_material_subformula_repository import FixedMaterialSubFormulaRepository

from lib.managers.material_manager import MaterialManager
from lib.managers.customer_manager import CustomerManager
from lib.managers.topic_manager import TopicManager
from lib.managers.subformula_manager import SubFormulaManager
from lib.managers.formula_manager import FormulaManager
from lib.managers.order_manager import OrderManager
from lib.managers.product_manager import ProductManager
from lib.managers.sample_images_group_manager import SampleImagesGroupManager

from lib.directors.formula_director import FormulaDirector

from lib.ceos.product_ceo import ProductCEO

from lib.chairmans.order_chairman import OrderChairman

from utilities import scm_constants
from utilities.scm_enums import OrderStatus, PaymentStatus
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

logger = ScmLogger(__name__)

###################################################################################
# REPOSITORIES
###################################################################################
delivery_method_repo = DeliveryMethodRepository(db)
decoration_form_repo = DecorationFormRepository(db)
decoration_technique_repo = DecorationTechniqueRepository(db)
material_repo = MaterialRepository(db)
material_subformula_repo = MaterialSubFormulaRepository(db)
material_version_repo = MaterialVersionRepository(db)
material_version_cost_estimation_repo = MaterialVersionCostEstimationRepository(db)
cost_estimation_repo = CostEstimationRepository(db)
customer_repo = CustomerRepository(db)
taste_repo = TasteRepository(db)
topic_repo = TopicRepository(db)
subformula_repo = SubFormulaRepository(db)
formula_repo = FormulaRepository(db)
formula_subformula_repo = FormulaSubFormulaRepository(db)
order_repo = OrderRepository(db)
sample_image_path_repo = SampleImagePathRepository(db)
sample_images_group_repo = SampleImagesGroupRepository(db)
product_repo = ProductRepository(db)
product_image_path_repo = ProductImagePathRepository(db)
product_cost_estimation_repo = ProductCostEstimationRepository(db)
fixed_formula_repo = FixedFormulaRepository(db)
fixed_subformula_repo = FixedSubFormulaRepository(db)
fixed_material_subformula_repo = FixedMaterialSubFormulaRepository(db)

###################################################################################
# MANAGERS
###################################################################################
material_manager = MaterialManager(material_repo,
                                   material_version_repo,
                                   material_subformula_repo,
                                   subformula_repo,
                                   product_repo,
                                   order_repo,
                                   formula_subformula_repo,
                                   formula_repo)
customer_manager = CustomerManager(customer_repo)
topic_manager = TopicManager(topic_repo)
subformula_manager = SubFormulaManager(subformula_repo,
                                 material_subformula_repo,
                                 taste_repo,
                                 material_version_cost_estimation_repo,
                                 cost_estimation_repo,
                                 product_repo,
                                 order_repo,
                                 formula_subformula_repo,
                                 formula_repo)
formula_manager = FormulaManager(formula_repo,
                                 subformula_repo,
                                 formula_subformula_repo,
                                 material_subformula_repo)                                 
order_manager = OrderManager(order_repo,
                             product_repo)
sample_images_group_manager = SampleImagesGroupManager(sample_images_group_repo,
                                                       sample_image_path_repo)
product_manager = ProductManager(product_repo, 
                                 product_image_path_repo,
                                 sample_image_path_repo,
                                 cost_estimation_repo,
                                 order_repo,
                                 product_cost_estimation_repo,
                                 formula_repo,
                                 subformula_repo,
                                 material_version_cost_estimation_repo,
                                 material_repo,
                                 fixed_formula_repo,
                                 fixed_subformula_repo,
                                 fixed_material_subformula_repo)

###################################################################################
# DIRECTORS
###################################################################################
formula_director = FormulaDirector(formula_repo,
                                   formula_subformula_repo,
                                   product_repo,
                                   formula_manager,
                                   subformula_manager)

###################################################################################
# CEOS
###################################################################################
product_ceo = ProductCEO(product_repo,
                         formula_repo,
                         product_cost_estimation_repo,
                         product_image_path_repo,
                         cost_estimation_repo,
                         order_repo,
                         formula_director)

###################################################################################
# CHAIRMANS
###################################################################################
order_chairman = OrderChairman(order_repo,
                               product_repo,
                               product_ceo)

####################################################################################
# MENU
####################################################################################
@app.before_request
def menu_setup():
    production_funcs = [
        ['list_materials', 'List of materials'],
        ['list_subformulas', 'List of subformulas'],
        ['list_formulas', 'List of formulas'],
        ['list_decoration_forms', 'List of decoration forms'],
        ['list_decoration_techniques', 'List of decoration techniques'],        
        ['list_tastes', 'List of tastes']
    ]

    business_funcs = [
        ['list_customers', 'List of customers'],
        ['list_orders', 'List of orders'],
        ['list_delivery_methods', 'List of delivery methods']
    ]

    exhibition_funcs = [
        ['list_topics', 'List of topics'],
        ['list_sample_images', 'List of sample images']
    ]
    
    statistics_funcs = [
        ['statistics_order', 'Order'],
        ['statistics_income', 'Income']
    ]

    menu_configuration = {
        'Production': production_funcs,
        'Business': business_funcs,
        'Exhibition': exhibition_funcs,
        'Statistics': statistics_funcs
    }

    session[scm_constants.MENU_CONFIGURATION] = menu_configuration

####################################################################################
# HELPERS
####################################################################################
def render_scm_template(site_html, **kwargs):
    return render_template(site_html,
                           **kwargs,
                           menu_configuration=session[scm_constants.MENU_CONFIGURATION])

def render_scm_template_with_message(site_html,
                                     message,
                                     message_type,
                                     exception,
                                     **kwargs):
    if exception is not None:
        logger.error(message)
        logger.exception(exception)
    else:
        logger.info(message)

    flash(message, message_type)
    return render_template(site_html,
                           **kwargs,
                           menu_configuration=session[scm_constants.MENU_CONFIGURATION])

def redirect_with_message(url, message, message_type):
    flash(message, message_type)
    return redirect(url)

def render_error(error_message):
    logger.error(error_message)
    flash(error_message, 'danger')
    return render_scm_template('error.html')

####################################################################################
# TASTE
####################################################################################
@app.route('/add_taste', methods=['GET', 'POST'])
def add_taste():    
    if request.method == 'POST':
        try:
            name = request.form['name'].strip()
            description = request.form['description'].strip()
            taste_repo.add_taste(name=name, description=description)
            db.session.commit()
            
            message = 'Successfully added taste %s' % name
            logger.info(message)
            
            return redirect_with_message(url_for('list_tastes'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            
            message = 'Failed to add taste %s' % name
            logger.error(message)

            flash(message, 'danger')
            return render_scm_template('name_description.html',
                                        site_title='Add a new taste')
    else:
        return render_scm_template('name_description.html',
                                    site_title='Add a new taste')

@app.route('/update_taste/<int:taste_id>', methods=['GET', 'POST'])
def update_taste(taste_id):
    taste_rec = taste_repo.get_taste(taste_id)
    if request.method == 'GET':
        return render_scm_template('name_description.html',
                                    site_title='Update taste', 
                                    old_name=taste_rec.name,
                                    old_description=taste_rec.description)
    elif request.method == 'POST':
        try:
            name = request.form['name'].strip()
            description = request.form['description'].strip()
            taste_repo.update_taste(taste_id,
                                    name,
                                    description)
            db.session.commit()
            
            message = 'Successfully updated taste %s (%s)' % (name, taste_id)
            logger.info(message)
            
            return redirect_with_message(url_for('list_tastes'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('name_description.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    site_title='Update taste', 
                                                    old_name=taste_rec.name,
                                                    old_description=taste_rec.description)            

@app.route('/list_tastes', methods=['GET', 'POST'])
def list_tastes():
    tastes = taste_repo.get_all_tastes()
    return render_scm_template('list_tastes.html', tastes=tastes)

####################################################################################
# TOPIC
####################################################################################
@app.route('/add_topic', methods=['GET', 'POST'])
def add_topic():
    topic_recs = topic_repo.get_all_topics()
    topic_recs.insert(0, None)

    if request.method == 'POST':
        try:
            name = request.form['name'].strip()
            description = request.form['description'].strip()
            parent_id = int(request.form['parent_topic_id'])
            
            topic_repo.add_topic(name=name,
                                 description=description,
                                 parent_id=parent_id)
            db.session.commit()
            
            message = 'Successfully added topic %s' % name
            logger.info(message)
            
            return redirect_with_message(url_for('list_topics'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            
            message = 'Failed to add topic %s' % name
            logger.error(message)
            
            flash(message, 'danger')
            return render_scm_template('add_update_topic.html', 
                                        topic_rec=None,
                                        topic_recs=topic_recs)
    else:
        return render_scm_template('add_update_topic.html', 
                                   topic_rec=None,
                                   topic_recs=topic_recs)

@app.route('/update_topic/<int:topic_id>', methods=['GET', 'POST'])
def update_topic(topic_id):
    topic_recs = topic_repo.get_all_topics()
    topic_recs.insert(0, None)
    topic_rec = topic_repo.get_topic(topic_id)

    if request.method == 'GET':        
        return render_scm_template('add_update_topic.html', 
                                   topic_rec=topic_rec,
                                   topic_recs=topic_recs)
    elif request.method == 'POST':
        try:
            name = request.form['name'].strip()
            description = request.form['description'].strip()
            parent_id = int(request.form['parent_topic_id'])
            
            topic_repo.update_topic(topic_id,
                                    name,
                                    description,
                                    parent_id)
            db.session.commit()

            message = 'Successfully updated topic %s (%s)' % (name, topic_id)
            logger.info(message)

            return redirect_with_message(url_for('list_topics'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('add_update_topic.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    topic_rec=topic_rec,
                                                    topic_recs=topic_recs)            

@app.route('/list_topics', methods=['GET', 'POST'])
def list_topics():
    topic_dtos = topic_manager.get_topic_dtos()
    return render_scm_template('list_topics.html', topic_dtos=topic_dtos)

####################################################################################
# DECORATION FORMS
####################################################################################
@app.route('/add_decoration_form', methods=['GET', 'POST'])
def add_decoration_form():
    if request.method == 'POST':
        try:
            name = request.form['name'].strip()
            description = request.form['description'].strip()
            
            decoration_form_repo.add_decoration_form(name=name,
                                                     description=description)
            db.session.commit()

            message = 'Successfully added decoration form %s' % name
            logger.info(message)
            
            return redirect_with_message(url_for('list_decoration_forms'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            message = 'Failed to add decoration form %s' % name
            flash(message, 'danger')
            return render_scm_template('name_description.html',
                                        site_title='Add a decoration form')
    else:
        return render_scm_template('name_description.html',
                                    site_title='Add a decoration form')

@app.route('/update_decoration_form/<int:decoration_form_id>', methods=['GET', 'POST'])
def update_decoration_form(decoration_form_id):
    decoration_form_rec = decoration_form_repo.get_decoration_form(decoration_form_id)
    if request.method == 'GET':
        return render_scm_template('name_description.html',
                                    site_title='Update decoration form',
                                    old_name=decoration_form_rec.name,
                                    old_description=decoration_form_rec.description)
    elif request.method == 'POST':
        try:
            name = request.form['name'].strip()
            description = request.form['description'].strip()
            
            decoration_form_repo.update_decoration_form(decoration_form_id,
                                                        name,
                                                        description)
            db.session.commit()
            
            message = 'Successfully updated decoration form %s (%s)' % (name, decoration_form_id)
            logger.info(message)

            return redirect_with_message(url_for('list_decoration_forms'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('name_description.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    site_title='Update decoration form',
                                                    old_name=decoration_form_rec.name,
                                                    old_description=decoration_form_rec.description)

@app.route('/list_decoration_forms', methods=['GET', 'POST'])
def list_decoration_forms():
    decoration_form_recs = decoration_form_repo.get_all_decoration_forms()
    return render_scm_template('list_decoration_forms.html', decoration_form_recs=decoration_form_recs)

####################################################################################
# DECORATION TECHNIQUES
####################################################################################
@app.route('/add_decoration_technique', methods=['GET', 'POST'])
def add_decoration_technique():
    if request.method == 'POST':
        try:
            name = request.form['name'].strip()
            description = request.form['description'].strip()
            
            decoration_technique_repo.add_decoration_technique(name=name,
                                                               description=description)
            db.session.commit()

            message = 'Successfully added decoration technique %s' % name
            logger.info(message)

            return redirect_with_message(url_for('list_decoration_techniques'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            message = 'Failed to add decoration form %s' % name
            flash(message, 'danger')
            return render_scm_template('name_description.html',
                                        site_title='Add a new decoration technique')
    else:
        return render_scm_template('name_description.html',
                                    site_title='Add a new decoration technique')

@app.route('/update_decoration_technique/<int:decoration_technique_id>', methods=['GET', 'POST'])
def update_decoration_technique(decoration_technique_id):
    decoration_technique_rec = decoration_technique_repo.get_decoration_technique(decoration_technique_id)
    if request.method == 'GET':        
        return render_scm_template('name_description.html',
                                    site_title='Update decoration technique',
                                    old_name=decoration_technique_rec.name,
                                    old_description=decoration_technique_rec.description)
    elif request.method == 'POST':
        try:
            name = request.form['name'].strip()
            description = request.form['description'].strip()
            
            decoration_technique_repo.update_decoration_technique(decoration_technique_id,
                                                                  name,
                                                                  description)
            db.session.commit()

            message = 'Successfully updated decoration technique %s (%s)' % (name, decoration_technique_id)
            logger.info(message)

            return redirect_with_message(url_for('list_decoration_techniques'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('name_description.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    site_title='Update decoration technique',
                                                    old_name=decoration_technique_rec.name,
                                                    old_description=decoration_technique_rec.description)

@app.route('/list_decoration_techniques', methods=['GET', 'POST'])
def list_decoration_techniques():
    decoration_technique_recs = decoration_technique_repo.get_all_decoration_techniques()
    return render_scm_template('list_decoration_techniques.html', decoration_technique_recs=decoration_technique_recs)

####################################################################################
# MATERIALS
####################################################################################
@app.route('/add_material', methods=['GET', 'POST'])
def add_material():
    
    if request.method == 'POST':
        try:
            name = request.form['name'].strip()
            description = request.form['description'].strip()
            unit_amount = request.form['unit_amount']
            unit = request.form['unit']
            unit_price = request.form['unit_price'].strip()            
            is_organic = 'is_organic' in request.form
            
            material_manager.add_material(name=name,
                                          description=description,
                                          is_organic=is_organic,
                                          unit_amount=unit_amount,
                                          unit=unit,
                                          unit_price=unit_price)
            db.session.commit()

            message = 'Successfully added material (%s, %s/%s %s)' % \
                      (name,
                       unit_price,
                       unit_amount,
                       unit)
            logger.info(message)

            return redirect_with_message(url_for('list_materials'), message, 'info')
        except ScmException as ex:
            message = 'Failed to add material (%s, %s/%s %s)' % \
                      (name,
                       unit_price,
                       unit_amount,
                       unit)
            flash(message, 'danger')            
            return render_scm_template('add_material.html', unit_choices=scm_constants.UNIT_CHOICES)
    else:
        return render_scm_template('add_material.html', unit_choices=scm_constants.UNIT_CHOICES)

@app.route('/update_material/<int:material_id>', methods=['GET', 'POST'])
def update_material(material_id):
    material_rec = material_repo.get_material(material_id)
    material_version_rec = material_version_repo.get_latest_version_of_material(material_id)

    if request.method == 'GET':        
        return render_scm_template('update_material.html',
                                    material_rec=material_rec,
                                    material_version_rec=material_version_rec,
                                    unit_choices=scm_constants.UNIT_CHOICES)
    elif request.method == 'POST':
        try:
            name = request.form['name'].strip()
            description = request.form['description'].strip()            
            unit_price = Decimal(request.form['unit_price'])

            material_manager.update_material(material_id,
                                             name,
                                             description,
                                             unit_price)
            db.session.commit()
            message = 'Successfully updated material (%s, %s/ %s %s)' % \
                      (name,
                       unit_price,
                       material_rec.unit_amount,
                       material_rec.unit)
            logger.info(message)

            return redirect_with_message(url_for('list_materials'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('update_material.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    material_rec=material_rec,
                                                    material_version_rec=material_version_rec,
                                                    unit_choices=scm_constants.UNIT_CHOICES)

@app.route('/show_material_unit_price_history/<int:material_id>', methods=['GET', 'POST'])
def show_material_unit_price_history(material_id):
    material_rec = material_repo.get_material(material_id)
    material_versions = material_version_repo.get_material_history(material_id)
    return render_scm_template('material_history.html',
                               material_rec=material_rec,
                               material_versions=material_versions)
    
@app.route('/list_materials', methods=['GET', 'POST'])
def list_materials():
    material_dtos = material_manager.get_material_dtos()
    return render_scm_template('list_materials.html', material_dtos=material_dtos)

####################################################################################
# CUSTOMERS
####################################################################################
@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    customer_recs = customer_repo.get_all_customers()
    customer_recs.insert(0, None)

    if request.method == 'POST':
        try:
            name = request.form['name'].strip()
            birthday = request.form['birthday']
            address = request.form['address'].strip()
            phone = request.form['phone'].strip()
            email_address = request.form['email_address'].strip()
            facebook = request.form['facebook'].strip()
            recommended_by = int(request.form['recommended_by'])
            note = request.form['note'].strip()
            
            customer_repo.add_customer(name,
                                       birthday,
                                       address,
                                       phone,
                                       email_address,
                                       facebook,
                                       recommended_by,
                                       note)
            db.session.commit()
            
            message = 'Successfully added customer %s' % name
            logger.info(message)

            return redirect_with_message(url_for('list_customers'), message, 'info')
        except ScmException as ex:
            message = ex.message
            db.session.rollback()
            return render_scm_template_with_message('add_update_customer.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    customer_rec=None,
                                                    customer_recs=customer_recs)
    else:
        return render_scm_template('add_update_customer.html', 
                                   customer_rec=None,
                                   customer_recs=customer_recs)

@app.route('/update_customer/<int:customer_id>', methods=['GET', 'POST'])
def update_customer(customer_id):
    customer_recs = customer_repo.get_all_customers()
    customer_recs.insert(0, None)
    customer_rec = customer_repo.get_customer(customer_id)
    if request.method == 'GET':
        return render_scm_template('add_update_customer.html',
                                   customer_rec=customer_rec,
                                   customer_recs=customer_recs)
    elif request.method == 'POST':
        try:
            name = request.form['name'].strip()
            birthday = request.form['birthday']
            address = request.form['address'].strip()
            phone = request.form['phone'].strip()
            email_address = request.form['email_address'].strip()
            facebook = request.form['facebook'].strip()
            recommended_by = int(request.form['recommended_by'])
            note = request.form['note'].strip()

            customer_repo.update_customer(customer_id,
                                          name,
                                          birthday,
                                          address,
                                          phone,
                                          email_address,
                                          facebook,
                                          recommended_by,
                                          note)
            db.session.commit()

            message = 'Successfully updated customer %s' % name
            logger.info(message)

            return redirect_with_message(url_for('list_customers'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('add_update_customer.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    customer_rec=customer_rec,
                                                    customer_recs=customer_recs)            

@app.route('/show_customer_order_history/<int:customer_id>', methods=['GET', 'POST'])
def show_customer_order_history(customer_id):
    pass

@app.route('/list_customers', methods=['GET', 'POST'], defaults={'page':1})
@app.route('/list_customers/', methods=['GET', 'POST'], defaults={'page':1})
@app.route('/list_customers/<int:page>', methods=['GET', 'POST'])
@app.route('/list_customers/<int:page>/', methods=['GET', 'POST'])
def list_customers(page):
    per_page = int(config['PAGING']['customers_per_page'])
    search_text = request.args.get('search_text')
    
    customer_dtos = customer_manager.get_paginated_customer_dtos(page,
                                                                 per_page,
                                                                 search_text)
    
    return render_scm_template('list_customers.html', customer_dtos=customer_dtos)

@app.route('/customer_details/<int:customer_id>', methods=['GET', 'POST'])
def customer_details(customer_id):
    customer_dto = customer_manager.get_customer_details(customer_id)
    return render_scm_template('customer_details.html',
                               customer_dto=customer_dto)

####################################################################################
# SUB FORMULAS
####################################################################################

@app.route('/list_subformulas', methods=['GET', 'POST'])
@app.route('/list_subformulas/', methods=['GET', 'POST'])
def list_subformulas_default():
    first_taste_rec = taste_repo.get_first_taste()
    if first_taste_rec is not None:
        return redirect('/list_subformulas/' + str(first_taste_rec.id))
    return render_error('No taste found in the database. Please add a taste.')

@app.route('/list_subformulas/<int:taste_id>', methods=['GET', 'POST'], defaults={'page':1})
@app.route('/list_subformulas/<int:taste_id>/', methods=['GET', 'POST'], defaults={'page':1})
@app.route('/list_subformulas/<int:taste_id>/<int:page>', methods=['GET', 'POST'])
@app.route('/list_subformulas/<int:taste_id>/<int:page>/', methods=['GET', 'POST'])
def list_subformulas(taste_id, page):
    per_page = int(config['PAGING']['subformulas_per_page'])
    search_text = request.args.get('search_text')
    
    subformula_dtos, db_changed = subformula_manager.get_paginated_subformula_dtos(
        taste_id,
        page,
        per_page,
        search_text)

    if db_changed == True:
        db.session.commit()

    taste_rec = taste_repo.get_taste(taste_id)
    taste_recs = taste_repo.get_all_tastes()
                                                                  
    return render_scm_template('list_subformulas.html',
                                search_text=search_text,
                                taste_rec=taste_rec,
                                taste_recs=taste_recs,
                                subformula_dtos=subformula_dtos)

def __extract_subformula_props(props_dict):
    subformula_name = props_dict['subformula_name']
    taste_id = int(props_dict['taste_id'])
    subformula_type = int(props_dict['subformula_type'])
    description = props_dict['subformula_description']
    note = props_dict['subformula_note']
    material_ids = []
    amounts = []
        
    i = 0
    while True:
        material_choice_i = 'material_choices_' + str(i)
        material_amount_i = 'material_amount_' + str(i)
        
        if material_choice_i not in props_dict:
            break

        material_id = int(props_dict[material_choice_i])
        amount = Decimal(props_dict[material_amount_i])
            
        material_ids.append(material_id)
        amounts.append(amount)
        i += 1

    return subformula_name, \
        taste_id, \
        subformula_type, \
        description, \
        note, \
        material_ids, \
        amounts

@app.route('/add_subformula', methods=['GET', 'POST'])
def add_subformula():
    material_dtos = material_manager.get_material_dtos()
    taste_recs = taste_repo.get_all_tastes()

    if request.method == 'POST':
        try:
            subformula_name, \
            taste_id, \
            subformula_type, \
            description, \
            note, \
            material_ids, \
            amounts = __extract_subformula_props(request.form)

            new_subformula_id = subformula_manager.add_subformula(subformula_name,
                                        taste_id,
                                        subformula_type,
                                        description,
                                        note,
                                        material_ids,
                                        amounts)
            db.session.flush()
            subformula_manager.estimate_subformula_cost(new_subformula_id)            
            db.session.commit()

            message = 'Successfully added subformula %s' % subformula_name
            logger.info(message)

            return redirect_with_message(url_for('list_subformulas', taste_id=taste_id), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('add_subformula.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    taste_recs=taste_recs,
                                                    material_dtos=material_dtos,
                                                    subformula_type_names=scm_constants.FORMULA_TYPE_NAMES)
    else:
        return render_scm_template('add_subformula.html',
                                   taste_recs=taste_recs,
                                   material_dtos=material_dtos,
                                   subformula_type_names=scm_constants.FORMULA_TYPE_NAMES)

@app.route('/subformula_details/<int:subformula_id>', methods=['GET', 'POST'])
def subformula_details(subformula_id):
    subformula_rec, taste_rec, material_dtos = subformula_manager.get_subformula_details(subformula_id)

    return render_scm_template('subformula_details.html',
                               subformula_rec=subformula_rec,
                               taste_rec=taste_rec,
                               material_dtos=material_dtos)

@app.route('/update_subformula/<int:subformula_id>', methods=['GET', 'POST'])
def update_subformula(subformula_id):
    subformula_rec, material_subformulas, total_cost = subformula_manager.get_subformula_info(subformula_id)
    taste_recs = taste_repo.get_all_tastes()
    material_dtos = material_manager.get_material_dtos()

    if request.method == 'POST':
        try:
            subformula_name, \
            taste_id, \
            subformula_type, \
            description, \
            note, \
            material_ids, \
            amounts = __extract_subformula_props(request.form)

            subformula_manager.update_subformula(subformula_id,
                                           subformula_name,
                                           taste_id,
                                           subformula_type,
                                           description,
                                           note,
                                           material_ids,
                                           amounts)
            db.session.flush()
            subformula_manager.estimate_subformula_cost(subformula_id)
            db.session.commit()

            message = 'Successfully updated subformula %s' % subformula_id
            logger.info(message)

            return redirect_with_message(url_for('list_subformulas', taste_id=taste_id), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('update_subformula.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    subformula_rec=subformula_rec,
                                                    material_subformulas=material_subformulas,
                                                    taste_recs=taste_recs,
                                                    material_dtos=material_dtos,
                                                    subformula_type_names=scm_constants.FORMULA_TYPE_NAMES,
                                                    total_cost=total_cost)

    return render_scm_template('update_subformula.html',
                               subformula_rec=subformula_rec,
                               material_subformulas=material_subformulas,
                               taste_recs=taste_recs,
                               subformula_type_names=scm_constants.FORMULA_TYPE_NAMES,
                               material_dtos=material_dtos,
                               total_cost=total_cost)

@app.route('/subformula_cost_estimation_details/<int:subformula_id>', methods=['GET', 'POST'])
def subformula_cost_estimation_details(subformula_id):
    subformula_rec = subformula_repo.get_subformula(subformula_id)
    cost_estimation, material_cost_estimation_dtos = subformula_manager.get_cost_estimation(subformula_id)
    return render_scm_template('subformula_cost_estimation.html',
                               subformula_rec=subformula_rec,
                               cost_estimation=cost_estimation,
                               material_cost_estimation_dtos=material_cost_estimation_dtos)

####################################################################################
# FORMULAS
####################################################################################

@app.route('/formula_cost_estimation_details/<int:formula_id>')
def formula_cost_estimation_details(formula_id):
    formula_rec, \
    subformula_recs, \
    subformula_counts, \
    taste_names, \
    subformula_cost_estimations, \
    material_cost_estimation_dtos, \
    begin_material_cost_estimation_dtos, \
    end_material_cost_estimation_dtos = formula_director.get_formula_cost_estimation_details(formula_id)

    return render_scm_template('formula_cost_estimation.html',
                                formula_rec=formula_rec,
                                subformula_recs=subformula_recs,
                                subformula_counts=subformula_counts,
                                taste_names=taste_names,
                                subformula_cost_estimations=subformula_cost_estimations,
                                material_cost_estimation_dtos=material_cost_estimation_dtos,
                                begin_material_cost_estimation_dtos=begin_material_cost_estimation_dtos,
                                end_material_cost_estimation_dtos=end_material_cost_estimation_dtos)

@app.route('/formula_details/<int:formula_id>')
def formula_details(formula_id):
    formula_rec, \
    subformula_recs, \
    subformula_counts, \
    taste_names, \
    material_dtos, \
    begin_material_dtos, \
    end_material_dtos = formula_manager.get_formula_details(formula_id)

    return render_scm_template('formula_details.html',
                                formula_rec=formula_rec,
                                subformula_recs=subformula_recs,
                                subformula_counts=subformula_counts,
                                taste_names=taste_names,
                                material_dtos=material_dtos,
                                begin_material_dtos=begin_material_dtos,
                                end_material_dtos=end_material_dtos)

@app.route('/list_formulas', methods=['GET', 'POST'], defaults={'page':1})
@app.route('/list_formulas/', methods=['GET', 'POST'], defaults={'page':1})
@app.route('/list_formulas/<int:page>', methods=['GET', 'POST'])
@app.route('/list_formulas/<int:page>/', methods=['GET', 'POST'])
def list_formulas(page):
    per_page = int(config['PAGING']['formulas_per_page'])
    search_text = request.args.get('search_text')

    formula_dtos, db_changed = formula_director.get_paginated_formula_dtos(
        page,
        per_page,
        search_text)

    if db_changed == True:
        db.session.commit()
                                                                  
    return render_scm_template('list_formulas.html',
                                search_text=search_text,
                                formula_dtos=formula_dtos)

def __extract_formula_props(props_dict):
    formula_name = props_dict['formula_name']
    formula_description = props_dict['formula_description']
    formula_note = props_dict['formula_note']

    subformula_ids = []
    subformula_counts = []
        
    i = 0
    while True:
        subformula_choices_i = 'subformula_choices_' + str(i)
        subformula_count_i = 'subformula_count_' + str(i)
        if subformula_choices_i not in props_dict:
            break

        subformula_id = int(props_dict[subformula_choices_i])
        subformula_count = int(props_dict[subformula_count_i])
            
        subformula_ids.append(subformula_id)
        subformula_counts.append(subformula_count)
        i += 1

    return formula_name, \
        formula_description, \
        formula_note, \
        subformula_ids, \
        subformula_counts

@app.route('/add_formula', methods=['GET', 'POST'])
def add_formula():
    taste_recs = taste_repo.get_all_tastes()
    taste_subformula_dict, subformula_dict = subformula_manager.get_taste_subformula_dict()

    if request.method == 'GET':
        return render_scm_template('add_formula.html',
                                   taste_recs=taste_recs,
                                   taste_subformula_dict=taste_subformula_dict,
                                   subformula_dict=subformula_dict)
    elif request.method == 'POST':
        try:
            formula_name, \
            formula_description, \
            formula_note, \
            subformula_ids, \
            subformula_counts = __extract_formula_props(request.form)

            formula_director.add_formula(formula_name,
                                         formula_description,
                                         formula_note,
                                         subformula_ids,
                                         subformula_counts)
            
            db.session.commit()

            message = 'Successfully added formula %s' % formula_name
            logger.info(message)

            return redirect_with_message(url_for('list_formulas'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('add_formula.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    taste_recs=taste_recs,
                                                    taste_subformula_dict=taste_subformula_dict,
                                                    subformula_dict=subformula_dict)

@app.route('/update_formula/<int:formula_id>', methods=['GET', 'POST'])
def update_formula(formula_id):
    formula_rec = formula_repo.get_formula(formula_id)
    taste_recs = taste_repo.get_all_tastes()
    taste_subformula_dict, subformula_dict = subformula_manager.get_taste_subformula_dict()
    subformula_recs, subformula_counts = formula_manager.get_subformula_info_of_formula(formula_id)

    if request.method == 'GET':
        return render_scm_template('formula_update.html',
                                    formula_rec=formula_rec,
                                    taste_recs=taste_recs,
                                    taste_subformula_dict=taste_subformula_dict,
                                    subformula_dict=subformula_dict,
                                    subformula_recs=subformula_recs,
                                    subformula_counts=subformula_counts)
    elif request.method == 'POST':
        try:
            new_formula_name, \
            new_formula_description, \
            new_formula_note, \
            new_subformula_ids, \
            new_subformula_counts = __extract_formula_props(request.form)

            formula_director.update_formula(formula_id,
                                            new_formula_name,
                                            new_formula_description,
                                            new_formula_note,
                                            new_subformula_ids,
                                            new_subformula_counts)
            db.session.commit()
            message = 'Successfully updated formula %s' % formula_id
            logger.info(message)
            return redirect_with_message(url_for('list_formulas'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('formula_update.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    formula_rec=formula_rec,
                                                    taste_recs=taste_recs,
                                                    taste_subformula_dict=taste_subformula_dict,
                                                    subformula_dict=subformula_dict,
                                                    subformula_recs=subformula_recs,
                                                    subformula_counts=subformula_counts)

####################################################################################
# ORDER
####################################################################################

def __extract_order_props(props_dict):
    customer_id = int(props_dict['customer_id'])
    ordered_on = datetime.datetime.strptime(props_dict['ordered_on'], '%Y-%m-%d %H:%M')
    delivery_appointment = datetime.datetime.strptime(props_dict['delivery_appointment'], '%Y-%m-%d %H:%M')
    delivery_method_id = int(props_dict['delivery_method_id'])
    message = props_dict['message']

    product_names = []
    product_amounts = []
    formula_ids = []
    decoration_form_ids = []
    decoration_technique_ids = []
    with_boxes = []

    i = 0
    while True:
        product_name_id = 'product_name_' + str(i)
        product_amount_id = 'product_amount_' + str(i)
        formula_choices_id = 'formula_choices_' + str(i)
        decoration_form_choices_id = 'decoration_form_choices_' + str(i)
        decoration_technique_choices_id = 'decoration_technique_choices_' + str(i)
        with_box_id = 'with_box_' + str(i)
        
        if product_name_id in props_dict:
            product_names.append(props_dict[product_name_id])
            product_amounts.append(props_dict[product_amount_id])
            formula_ids.append(int(props_dict[formula_choices_id]))
            decoration_form_ids.append(int(props_dict[decoration_form_choices_id]))
            decoration_technique_ids.append(int(props_dict[decoration_technique_choices_id]))
            if with_box_id in props_dict:
                with_boxes.append(True)
            else:
                with_boxes.append(False)
            i += 1
        else:
            break

    return customer_id, \
           ordered_on, \
           delivery_appointment, \
           delivery_method_id, \
           message, \
           product_names, \
           product_amounts, \
           formula_ids, \
           decoration_form_ids, \
           decoration_technique_ids, \
           with_boxes

@app.route('/add_order', methods=['GET', 'POST'])
def add_order():
    customer_recs = customer_repo.get_all_customers()
    delivery_method_recs = delivery_method_repo.get_all_delivery_methods()    
    decoration_form_recs = decoration_form_repo.get_all_decoration_forms()
    decoration_technique_recs = decoration_technique_repo.get_all_decoration_techniques()    
    formula_recs = formula_repo.get_all_formulas()

    if request.method == 'POST':
        try:
            customer_id, \
            ordered_on, \
            delivery_appointment, \
            delivery_method_id, \
            message, \
            product_names, \
            product_amounts, \
            formula_ids, \
            decoration_form_ids, \
            decoration_technique_ids, \
            with_boxes = __extract_order_props(request.form)

            new_order_id = order_chairman.add_order(customer_id,
                                                    ordered_on,
                                                    delivery_appointment,
                                                    delivery_method_id,
                                                    message,
                                                    product_names,
                                                    product_amounts,
                                                    formula_ids,
                                                    decoration_form_ids,
                                                    decoration_technique_ids,
                                                    with_boxes)
            db.session.commit()

            message = 'Successfully added order %s' % str(new_order_id)
            logger.info(message)

            return redirect_with_message(url_for('list_orders'), message, 'info')
        except ScmException as ex:
            db.session.rollback()

    return render_scm_template('add_order.html', 
                                customer_recs=customer_recs,
                                delivery_method_recs=delivery_method_recs,
                                decoration_form_recs=decoration_form_recs,
                                decoration_technique_recs=decoration_technique_recs,
                                formula_recs=formula_recs)

def __lazy_get_order_dtos(page, per_page, search_text):
    paginated_order_dtos = order_manager.get_paginated_order_dtos(page,
                                                                  per_page,
                                                                  search_text)
    db_changed = False
    checked_formula_ids_set = set()
    formula_ids_set = set()
    order_dtos_need_cost_update = []
    for i in range(len(paginated_order_dtos.items)):
        if paginated_order_dtos.items[i].has_up_to_date_cost_estimation == False:
            new_order_cost = order_chairman.estimate_order_cost(paginated_order_dtos.items[i].order_id)
            paginated_order_dtos.items[i].total_cost = new_order_cost
            db_changed = True

    return paginated_order_dtos, db_changed

@app.route('/list_orders', methods=['GET', 'POST'], defaults={'page':1})
@app.route('/list_orders/', methods=['GET', 'POST'], defaults={'page':1})
@app.route('/list_orders<int:page>', methods=['GET', 'POST'])
@app.route('/list_orders/<int:page>', methods=['GET', 'POST'])
def list_orders(page):
    per_page = int(config['PAGING']['orders_per_page'])
    search_text = request.args.get('search_text')

    paginated_order_dtos, db_changed = __lazy_get_order_dtos(page, per_page, search_text)

    if db_changed == True:
        db.session.commit()

    return render_scm_template('list_orders.html', order_dtos=paginated_order_dtos)

def __lazy_get_product_dtos(order_id):
    db_changed = False
    product_dtos = product_manager.get_product_dtos(order_id)

    for product_dto in product_dtos:
        if product_dto.has_up_to_date_cost_estimation == False:
            new_product_cost_estimation = product_ceo.estimate_product_cost(product_dto.product_id)

            product_dto.product_cost_estimation = new_product_cost_estimation
            db_changed = True
    
    if db_changed == True:
        db.session.commit()

    return product_dtos

@app.route('/order_details/<int:order_id>', methods=['GET', 'POST'])
def order_details(order_id):    
    product_dtos = __lazy_get_product_dtos(order_id)
    order_dto = order_manager.get_order_dto(order_id)

    return render_scm_template('order_details.html',
                               order_dto=order_dto,
                               product_dtos=product_dtos)

def __extract_update_order_args(order_rec, args):
    customer_id_arg = args.get('customer_id_arg')
    if customer_id_arg is None:
        customer_id_arg = order_rec.customer_id
    else:
        customer_id_arg = int(customer_id_arg)

    ordered_on_arg = args.get('ordered_on_arg')
    if ordered_on_arg is None:
        ordered_on_arg = order_rec.ordered_on

    delivery_appointment_arg = args.get('delivery_appointment_arg')
    if delivery_appointment_arg is None:
        delivery_appointment_arg = order_rec.delivery_appointment

    delivery_method_id_arg = args.get('delivery_method_id_arg')
    if delivery_method_id_arg is None:
        delivery_method_id_arg = order_rec.delivery_method_id
    else:
        delivery_method_id_arg = int(delivery_method_id_arg)

    order_status_arg = args.get('order_status_arg')
    if order_status_arg is None:
        order_status_arg = order_rec.order_status
    else:
        order_status_arg = int(order_status_arg)

    delivered_on_arg = args.get('delivered_on_arg')
    if delivered_on_arg is None:
        delivered_on_arg = order_rec.delivered_on

    payment_status_arg = args.get('payment_status_arg')
    if payment_status_arg is None:
        payment_status_arg = order_rec.payment_status
    else:
        payment_status_arg = int(payment_status_arg)

    paid_on_arg = args.get('paid_on_arg')
    if paid_on_arg is None:
        paid_on_arg = order_rec.paid_on

    message_arg = args.get('message_arg')
    if message_arg is None:
        message_arg = order_rec.message

    price_to_customers = {}
    price_to_customers_arg = args.get('price_to_customers_arg')

    if price_to_customers_arg is not None:
        product_ids_prices = price_to_customers_arg.split('!!!!')

        for product_id_price in product_ids_prices:
            if product_id_price != '':
                pair = product_id_price.split('--')
                price_to_customers[int(pair[0])] = pair[1]

    new_product_name_arg = args.get('new_product_name_arg')
    if new_product_name_arg is None:
        new_product_name_arg = ''
    
    product_amount_arg = args.get('product_amount_arg')
    if product_amount_arg is None:
        product_amount_arg = 1
    else:
        product_amount_arg = int(product_amount_arg)

    chosen_formula_id_arg = args.get('chosen_formula_id_arg')
    if chosen_formula_id_arg is None or chosen_formula_id_arg == '':
        chosen_formula_id_arg = -1
    else:
        chosen_formula_id_arg = int(chosen_formula_id_arg)

    chosen_decoration_form_id_arg = args.get('chosen_decoration_form_id_arg')
    if chosen_decoration_form_id_arg is None or chosen_decoration_form_id_arg == '':
        chosen_decoration_form_id_arg = -1
    else:
        chosen_decoration_form_id_arg = int(chosen_decoration_form_id_arg)

    chosen_decoration_techinque_id_arg = args.get('chosen_decoration_techinque_id_arg')
    if chosen_decoration_techinque_id_arg is None or chosen_decoration_techinque_id_arg == '':
        chosen_decoration_techinque_id_arg = -1
    else:
        chosen_decoration_techinque_id_arg = int(chosen_decoration_techinque_id_arg)

    with_box_arg = args.get('with_box_arg')
    if with_box_arg is None or with_box_arg == '':
        with_box_arg = 'false'

    return customer_id_arg, \
        ordered_on_arg, \
        delivery_appointment_arg, \
        delivery_method_id_arg, \
        order_status_arg, \
        delivered_on_arg, \
        payment_status_arg, \
        paid_on_arg, \
        message_arg, \
        new_product_name_arg, \
        product_amount_arg, \
        chosen_formula_id_arg, \
        chosen_decoration_form_id_arg, \
        chosen_decoration_techinque_id_arg, \
        with_box_arg, \
        price_to_customers

def __extract_product_prices_to_customer(props):
    product_prices_to_customer = {}
    order_price_to_customer = 0

    for key, value in props.items():
        if key.startswith('price_to_customer_'):
            product_id_str = key[len('price_to_customer_'):]
            product_id = int(product_id_str)

            product_price = 0
            try:
                product_price = float(value)
            except ValueError:
                pass

            product_prices_to_customer[product_id] = product_price
            order_price_to_customer += product_price

    return order_price_to_customer, product_prices_to_customer

@app.route('/update_order/<int:order_id>', methods=['GET', 'POST'])
def update_order(order_id):
    order_rec = order_repo.get_order(order_id)

    customer_id_arg, \
        ordered_on_arg, \
        delivery_appointment_arg, \
        delivery_method_id_arg, \
        order_status_arg, \
        delivered_on_arg, \
        payment_status_arg, \
        paid_on_arg, \
        message_arg, \
        new_product_name_arg, \
        product_amount_arg, \
        chosen_formula_id_arg, \
        chosen_decoration_form_id_arg, \
        chosen_decoration_techinque_id_arg, \
        with_box_arg, \
        price_to_customers = __extract_update_order_args(order_rec, request.args)

    customer_recs = customer_repo.get_all_customers()    
    product_dtos = __lazy_get_product_dtos(order_id)

    if len(price_to_customers) == 0:
        for product_dto in product_dtos:
            price_to_customers[product_dto.product_id] = product_dto.price_to_customer

    delivery_method_recs = delivery_method_repo.get_all_delivery_methods()    
    decoration_form_recs = decoration_form_repo.get_all_decoration_forms()
    decoration_technique_recs = decoration_technique_repo.get_all_decoration_techniques()
    formula_recs = formula_repo.get_all_formulas()
    
    total_price_to_customer = 0
    for product_dto in product_dtos:
        if product_dto.product_id in price_to_customers:
            price_to_customer = price_to_customers[product_dto.product_id]            
            if price_to_customer is not None:
                if type(price_to_customer) == str:
                    try:
                        price_to_customer = float(price_to_customer)                    
                        total_price_to_customer += price_to_customer
                    except ValueError:
                        pass
                else:
                    total_price_to_customer += price_to_customer

    if request.method == 'GET':        
        return render_scm_template('update_order.html',
                                    order_id=order_id,
                                    customer_id=customer_id_arg,
                                    ordered_on=ordered_on_arg,
                                    delivery_appointment=delivery_appointment_arg,
                                    delivery_method_id=delivery_method_id_arg,
                                    order_status=order_status_arg,
                                    delivered_on=delivered_on_arg,
                                    payment_status=payment_status_arg,
                                    paid_on=paid_on_arg,
                                    new_product_name=new_product_name_arg,
                                    product_amount=product_amount_arg,
                                    chosen_formula_id=chosen_formula_id_arg,
                                    chosen_decoration_form_id=chosen_decoration_form_id_arg,
                                    chosen_decoration_technique_id=chosen_decoration_techinque_id_arg,
                                    with_box=with_box_arg,
                                    order_cost_estimation=order_rec.total_cost,
                                    customer_recs=customer_recs,
                                    delivery_method_recs=delivery_method_recs,
                                    product_dtos=product_dtos,
                                    order_status_names=scm_constants.ORDER_STATUS_NAMES,
                                    payment_status_names=scm_constants.PAYMENT_STATUS_NAMES,
                                    decoration_form_recs=decoration_form_recs,
                                    decoration_technique_recs=decoration_technique_recs,
                                    formula_recs=formula_recs,
                                    total_price_to_customer=total_price_to_customer,
                                    price_to_customers=price_to_customers)
    elif request.method == 'POST':        
        try:
            customer_id = int(request.form['customer_id'])
            ordered_on = request.form['ordered_on']
            delivery_appointment = request.form['delivery_appointment']
            delivery_method_id = int(request.form['delivery_method_id'])
            
            order_status = int(request.form['order_status'])
            delivered_on = None
            if order_status == int(OrderStatus.DELIVERED):
                delivered_on = request.form['delivered_on']

            paid_on = None
            payment_status = request.form['payment_status']
            if payment_status != int(PaymentStatus.NOT_PAID):
                paid_on = request.form['paid_on']

            message = request.form['message']

            order_price_to_customer, product_prices_to_customer = __extract_product_prices_to_customer(request.form)
            product_manager.update_prices_to_customer(product_prices_to_customer)

            order_manager.update_order(order_id,
                                       customer_id,
                                       delivery_appointment,
                                       delivery_method_id,
                                       ordered_on,
                                       order_status,
                                       delivered_on,
                                       payment_status,
                                       paid_on,
                                       message,
                                       order_price_to_customer)
            db.session.commit()
            
            message = 'Successfully updated order %s' % order_id
            logger.info(message)
            
            return redirect_with_message(url_for('list_orders'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('update_order.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    order_id=order_id,
                                                    customer_id=customer_id_arg,
                                                    ordered_on=ordered_on_arg,
                                                    delivery_appointment=delivery_appointment_arg,
                                                    delivery_method_id=delivery_method_id_arg,
                                                    order_status=order_status_arg,
                                                    delivered_on=delivered_on_arg,
                                                    payment_status=payment_status_arg,
                                                    paid_on=paid_on_arg,
                                                    new_product_name=new_product_name_arg,
                                                    product_amount=product_amount_arg,
                                                    chosen_taste_id=chosen_taste_id_arg,
                                                    chosen_formula_id=chosen_formula_id_arg,
                                                    chosen_decoration_form_id=chosen_decoration_form_id_arg,
                                                    chosen_decoration_technique_id=chosen_decoration_techinque_id_arg,
                                                    with_box=with_box_arg,
                                                    order_cost_estimation=order_rec.total_cost,
                                                    customer_recs=customer_recs,
                                                    delivery_method_recs=delivery_method_recs,
                                                    product_dtos=product_dtos,
                                                    order_status_names=scm_constants.ORDER_STATUS_NAMES,
                                                    payment_status_names=scm_constants.PAYMENT_STATUS_NAMES,
                                                    decoration_form_recs=decoration_form_recs,
                                                    decoration_technique_recs=decoration_technique_recs,
                                                    formula_recs=formula_recs,
                                                    total_price_to_customer=total_price_to_customer,
                                                    price_to_customers=price_to_customers)

@app.route('/add_new_product_to_order/<int:order_id>', methods=['GET', 'POST'])
def add_new_product_to_order(order_id):
    new_product_name = request.args.get('new_product_name_arg')
    product_amount = int(request.args.get('product_amount_arg'))    
    formula_id = int(request.args.get('formula_id_arg'))
    decoration_form_id = int(request.args.get('decoration_form_id_arg'))
    decoration_technique_id = int(request.args.get('decoration_technique_id_arg'))
    
    with_box_arg = request.args.get('with_box_arg')
    with_box = with_box_arg.upper() == 'TRUE'

    try:
        product_ceo.add_product(new_product_name,
                                product_amount,
                                order_id,
                                formula_id,
                                decoration_form_id,
                                decoration_technique_id,
                                with_box)
        db.session.commit()
    except ScmException as ex:
        db.session.rollback()
        message = 'Failed to add a new product "%s" to order %s' % (product_name, order_id)
        return redirect_with_message(url_for('update_order', 
                                             order_id=order_id,
                                             customer_id_arg=[request.args.get('customer_id_arg')],
                                             ordered_on_arg=[request.args.get('ordered_on_arg')],
                                             delivery_appointment_arg=[request.args.get('delivery_appointment_arg')],
                                             delivery_method_id_arg=[request.args.get('delivery_method_id_arg')],
                                             order_status_arg=[request.args.get('order_status_arg')],
                                             delivered_on_arg=[request.args.get('delivered_on_arg')],
                                             payment_status_arg=[request.args.get('payment_status_arg')],
                                             paid_on_arg=[request.args.get('paid_on_arg')],
                                             message_arg=[request.args.get('message_arg')],
                                             price_to_customers_arg=[request.args.get('price_to_customers_arg')],
                                             new_product_name_arg=[request.args.get('new_product_name_arg')],
                                             product_amount_arg=[request.args.get('product_amount_arg')],                                             
                                             chosen_formula_id_arg=[request.args.get('formula_id_arg')],
                                             chosen_decoration_form_id_arg=[request.args.get('decoration_form_id_arg')],
                                             chosen_decoration_technique_id_arg=[request.args.get('decoration_technique_id_arg')],
                                             with_box_arg=[request.args.get('with_box_arg')]
                                             ),
                                             message,
                                             'danger')
    
    message = 'Successfully add a new product %s to order %s' % (new_product_name, order_id)
    logger.info(message)

    return redirect_with_message(url_for('update_order', 
                                 order_id=order_id, 
                                 customer_id_arg=[request.args.get('customer_id_arg')],
                                 ordered_on_arg=[request.args.get('ordered_on_arg')],
                                 delivery_appointment_arg=[request.args.get('delivery_appointment_arg')],
                                 delivery_method_id_arg=[request.args.get('delivery_method_id_arg')],
                                 order_status_arg=[request.args.get('order_status_arg')],
                                 delivered_on_arg=[request.args.get('delivered_on_arg')],
                                 payment_status_arg=[request.args.get('payment_status_arg')],
                                 paid_on_arg=[request.args.get('paid_on_arg')],
                                 message_arg=[request.args.get('message_arg')],
                                 price_to_customers_arg=[request.args.get('price_to_customers_arg')],
                                 new_product_name_arg=[''],
                                 product_amount_arg=['1'],                                 
                                 chosen_formula_id_arg=['-1'],
                                 chosen_decoration_form_id_arg=['-1'],
                                 chosen_decoration_technique_id_arg=['-1'],
                                 with_box_arg=['false']
                                 ), 
                                 message, 
                                 'info')

####################################################################################
# PRODUCT
####################################################################################

@app.route('/product_details/<int:product_id>', methods=['GET', 'POST'])
def product_details(product_id):
    product_dto = product_manager.get_product_dto(product_id)
    product_image_path_recs = product_image_path_repo.get_product_image_paths(product_id)

    return render_scm_template('product_details.html',
                                product_dto=product_dto,
                                product_image_path_recs=product_image_path_recs)

def __extract_update_product_args(product_rec, args):
    current_product_name = args.get('product_name_arg')
    if current_product_name is None:
        current_product_name = product_rec.name

    product_amount = args.get('product_amount_arg')
    if product_amount is not None:
        product_amount = int(product_amount)
    else:
        product_amount = product_rec.amount        
        
    selected_decoration_form_id = args.get('decoration_form_id_arg')
    if selected_decoration_form_id is not None:
        selected_decoration_form_id = int(selected_decoration_form_id)
    else:
        selected_decoration_form_id = product_rec.decoration_form_id

    selected_decoration_technique_id = args.get('decoration_technique_id_arg')
    if selected_decoration_technique_id is not None:
        selected_decoration_technique_id = int(selected_decoration_technique_id)
    else:
        selected_decoration_technique_id = product_rec.decoration_technique_id

    selected_formula_id = args.get('formula_id_arg')
    if selected_formula_id is not None:
        selected_formula_id = int(selected_formula_id)
    else:
        selected_formula_id = product_rec.formula_id

    selected_box_status = args.get('box_status_arg')
    if selected_box_status is not None:
        selected_box_status = int(selected_box_status)
    else:
        selected_box_status = product_rec.box_status
    chosen_box_returned_on = args.get('box_returned_on_arg')

    selected_sample_images_group_id = request.args.get('sample_images_group_id_arg')
    if selected_sample_images_group_id is not None:
        selected_sample_images_group_id = int(selected_sample_images_group_id)
    else:
        selected_sample_images_group_id = product_rec.sample_images_group_id
        
    return current_product_name, \
            product_amount, \
            selected_decoration_form_id, \
            selected_decoration_technique_id, \
            selected_formula_id, \
            selected_box_status, \
            chosen_box_returned_on, \
            selected_sample_images_group_id

@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    product_rec = product_repo.get_product(product_id)    
    product_image_path_recs = product_image_path_repo.get_product_image_paths(product_id)    
    decoration_form_recs = decoration_form_repo.get_all_decoration_forms()
    decoration_technique_recs = decoration_technique_repo.get_all_decoration_techniques()    
    sample_images_group_recs = sample_images_group_repo.get_all_sample_images_groups()
    
    latest_3_sample_image_paths = []
    if product_rec.sample_images_group_id is not None:
        latest_3_sample_image_paths = sample_image_path_repo.get_latest_3_sample_image_paths(product_rec.sample_images_group_id)

    subformula_recs = subformula_repo.get_all_subformulas()

    if request.method == 'GET':
        current_product_name, \
            product_amount, \
            selected_decoration_form_id, \
            selected_decoration_technique_id, \
            selected_formula_id, \
            selected_box_status, \
            chosen_box_returned_on, \
            selected_sample_images_group_id = __extract_update_product_args(product_rec, request.args)

        formula_recs = formula_repo.get_all_formulas()
        existing_product_image_paths_arg = request.args.get('existing_product_image_paths_arg')
        product_image_path_recs = __infer_product_image_path_recs(product_id, existing_product_image_paths_arg)

        sample_images_group_id_arg = request.args.get('sample_images_group_id_arg')
        if sample_images_group_id_arg is not None:
            selected_sample_images_group_id = int(sample_images_group_id_arg)
            latest_3_sample_image_paths = sample_image_path_repo.get_latest_3_sample_image_paths(selected_sample_images_group_id)
    elif request.method == 'POST':
        try:
            remaining_product_image_path_ids = __extract_remaining_image_path_ids(request.form, 'existing_product_image_')
            current_product_name = request.form['product_name']
            product_amount = int(request.form['product_amount'])
            selected_decoration_form_id = int(request.form['decoration_form_id'])
            selected_decoration_technique_id = int(request.form['decoration_technique_id'])            
            selected_box_status = int(request.form['box_status'])
            chosen_box_returned_on = request.form['box_returned_on']
            
            selected_formula_id = int(request.form['formula_id'])
            if selected_formula_id == -1:
                selected_formula_id = None

            selected_sample_images_group_id = int(request.form['sample_images_group_id'])
            if selected_sample_images_group_id == -1:
                selected_sample_images_group_id = None
                latest_3_sample_image_paths = []

            uploaded_files = request.files.getlist('file[]')

            product_ceo.update_product(product_id,
                                       current_product_name,
                                       selected_decoration_form_id,
                                       selected_decoration_technique_id,
                                       selected_formula_id,
                                       selected_box_status,
                                       chosen_box_returned_on,
                                       selected_sample_images_group_id,
                                       product_image_path_recs,
                                       remaining_product_image_path_ids,
                                       uploaded_files)
            db.session.commit()

            formula_recs = formula_repo.get_all_formulas()
            product_image_path_recs = product_image_path_repo.get_product_image_paths(product_id)
            
            message = 'Successfully updated product %s (%s)' % (current_product_name, product_id)
            logger.info(message)
            
            flash(message, 'info')
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('update_sample_images_group.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    decoration_form_recs=decoration_form_recs,
                                                    decoration_technique_recs=decoration_technique_recs,
                                                    product_rec=product_rec,
                                                    product_image_path_recs=product_image_path_recs,
                                                    formula_recs=formula_recs,
                                                    box_status_names=scm_constants.BOX_STATUS_NAMES,
                                                    sample_images_group_recs=sample_images_group_recs,
                                                    latest_3_sample_image_paths=latest_3_sample_image_paths,
                                                    current_product_name=current_product_name,
                                                    selected_formula_id=selected_formula_id,
                                                    selected_decoration_form_id=selected_decoration_form_id,
                                                    selected_decoration_technique_id=selected_decoration_technique_id,                                                    
                                                    selected_box_status=selected_box_status,
                                                    chosen_box_returned_on=chosen_box_returned_on,
                                                    selected_sample_images_group_id=selected_sample_images_group_id)
    
    return render_scm_template('update_product.html',
                               decoration_form_recs=decoration_form_recs,
                               decoration_technique_recs=decoration_technique_recs,
                               product_rec=product_rec,
                               product_image_path_recs=product_image_path_recs,
                               formula_recs=formula_recs,
                               box_status_names=scm_constants.BOX_STATUS_NAMES,
                               sample_images_group_recs=sample_images_group_recs,
                               latest_3_sample_image_paths=latest_3_sample_image_paths,
                               current_product_name=current_product_name,
                               selected_decoration_form_id=selected_decoration_form_id,
                               selected_decoration_technique_id=selected_decoration_technique_id,
                               selected_formula_id=selected_formula_id,
                               selected_box_status=selected_box_status,
                               chosen_box_returned_on=chosen_box_returned_on,
                               selected_sample_images_group_id=selected_sample_images_group_id)

@app.route('/delete_product/<int:product_id>', methods=['GET', 'POST'])
def delete_product(product_id):
    product_rec = product_repo.get_product(product_id)
    order_id = product_rec.order_id
    product_name = product_rec.name

    try:
        product_manager.delete_product(product_id)
        db.session.commit()
    except ScmException as ex:
        db.session.rollback()
        message = 'Failed to delete product "%s" (%s)' % (product_name, product_id)
        return redirect_with_message(url_for('update_order', 
                                             order_id=order_id,
                                             customer_id_arg=[request.args.get('customer_id_arg')],
                                             ordered_on_arg=[request.args.get('ordered_on_arg')],
                                             delivery_appointment_arg=[request.args.get('delivery_appointment_arg')],
                                             delivery_method_id_arg=[request.args.get('delivery_method_id_arg')],
                                             order_status_arg=[request.args.get('order_status_arg')],
                                             delivered_on_arg=[request.args.get('delivered_on_arg')],
                                             payment_status_arg=[request.args.get('payment_status_arg')],
                                             paid_on_arg=[request.args.get('paid_on_arg')],
                                             message_arg=[request.args.get('message_arg')],
                                             price_to_customers_arg=[request.args.get('price_to_customers_arg')],
                                             new_product_name_arg=[request.args.get('new_product_name_arg')],
                                             product_amount_arg=[request.args.get('product_amount_arg')],
                                             chosen_subformula_id_arg=[request.args.get('subformula_id_arg')],
                                             chosen_decoration_form_id_arg=[request.args.get('decoration_form_id_arg')],
                                             chosen_decoration_technique_id_arg=[request.args.get('decoration_technique_id_arg')],
                                             with_box_arg=[request.args.get('with_box_arg')]
                                             ),
                                             message,
                                             'danger')
    
    message = 'Successfully deleted product "%s" (%s)' % (product_name, product_id)
    logger.info(message)

    return redirect_with_message(url_for('update_order', 
                                 order_id=order_id,
                                 customer_id_arg=[request.args.get('customer_id_arg')],
                                 ordered_on_arg=[request.args.get('ordered_on_arg')],
                                 delivery_appointment_arg=[request.args.get('delivery_appointment_arg')],
                                 delivery_method_id_arg=[request.args.get('delivery_method_id_arg')],
                                 order_status_arg=[request.args.get('order_status_arg')],
                                 delivered_on_arg=[request.args.get('delivered_on_arg')],
                                 payment_status_arg=[request.args.get('payment_status_arg')],
                                 paid_on_arg=[request.args.get('paid_on_arg')],
                                 message_arg=[request.args.get('message_arg')],
                                 price_to_customers_arg=[request.args.get('price_to_customers_arg')],
                                 new_product_name_arg=[request.args.get('new_product_name_arg')],
                                 product_amount_arg=[request.args.get('product_amount_arg')],
                                 chosen_subformula_id_arg=[request.args.get('subformula_id_arg')],
                                 chosen_decoration_form_id_arg=[request.args.get('decoration_form_id_arg')],
                                 chosen_decoration_technique_id_arg=[request.args.get('decoration_technique_id_arg')],
                                 with_box_arg=[request.args.get('with_box_arg')]
                                 ),
                                 message,
                                 'info')

def __infer_product_image_path_recs(product_id,
                                    existing_product_image_paths_arg):
    all_product_image_path_recs = product_image_path_repo.get_product_image_paths(product_id)

    if existing_product_image_paths_arg is None:
        return all_product_image_path_recs

    existing_product_image_paths = existing_product_image_paths_arg.split("!!!")
    all_product_image_path_recs = product_image_path_repo.get_product_image_paths(product_id)
    product_image_path_recs = []
    for product_image_path_rec in all_product_image_path_recs:
        for existing_product_image_path in existing_product_image_paths:
            if existing_product_image_path == product_image_path_rec.file_path:
                product_image_path_recs.append(product_image_path_rec)

    return product_image_path_recs

####################################################################################
# DELIVERY METHOD
####################################################################################
@app.route('/add_delivery_method', methods=['GET', 'POST'])
def add_delivery_method():    
    if request.method == 'POST':
        try:
            name = request.form['name'].strip()
            description = request.form['description'].strip()
            delivery_method_repo.add_delivery_method(name=name, description=description)
            db.session.commit()

            message = 'Successfully added delivery method %s' % name
            logger.info(message)

            return redirect_with_message(url_for('list_delivery_methods'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            message = 'Failed to add delivery method %s' % name
            flash(message, 'danger')
            return render_scm_template('name_description.html',
                                       site_title='Add a new delivery method')
    else:
        return render_scm_template('name_description.html',
                                    site_title='Add a new delivery method')

@app.route('/update_delivery_method/<int:delivery_method_id>', methods=['GET', 'POST'])
def update_delivery_method(delivery_method_id):
    delivery_method_rec = delivery_method_repo.get_delivery_method(delivery_method_id)
    if request.method == 'GET':
        return render_scm_template('name_description.html',
                                    site_title='Add a new delivery method',
                                    old_name=delivery_method_rec.name,
                                    old_description=delivery_method_rec.description)
    elif request.method == 'POST':
        try:
            name = request.form['name'].strip()
            description = request.form['description'].strip()
            delivery_method_repo.update_delivery_method(delivery_method_id,
                                                        name,
                                                        description)
            db.session.commit()
            
            message = 'Successfully updated delivery method %s (%s)' % (name, delivery_method_id)
            logger.info(message)

            return redirect_with_message(url_for('list_delivery_methods'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('name_description.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    site_title='Add a new delivery method',
                                                    old_name=delivery_method_rec.name,
                                                    old_description=delivery_method_rec.description)

@app.route('/list_delivery_methods', methods=['GET', 'POST'])
def list_delivery_methods():
    delivery_methods = delivery_method_repo.get_all_delivery_methods()
    return render_scm_template('list_delivery_methods.html', delivery_methods=delivery_methods)

@app.route('/list_sample_images', methods=['GET', 'POST'])
def list_sample_images_default():
    topic_recs = topic_repo.get_all_topics()

    if len(topic_recs) == 0:
        return render_error('No topic exists in the database. Please add a topic!')

    return redirect('list_sample_images/' + str(topic_recs[0].id))

####################################################################################
# SAMPLE IMAGES
####################################################################################

@app.route('/list_sample_images/<int:topic_id>', methods=['GET', 'POST'])
def list_sample_images(topic_id):
    topic_recs = topic_repo.get_all_topics()
    sample_images_group_recs = sample_images_group_repo.get_sample_images_groups_by_topic(topic_id)
    latest_groups_3_image_paths = sample_images_group_manager.get_latest_groups_3_image_paths(sample_images_group_recs)

    return render_scm_template('list_sample_images.html',
                               topic_recs=topic_recs,
                               sample_images_group_recs=sample_images_group_recs,
                               latest_groups_3_image_paths=latest_groups_3_image_paths,
                               selected_topic_id=topic_id)

@app.route('/add_sample_images_group/<int:topic_id>', methods=['GET', 'POST'])
def add_sample_images_group(topic_id):
    topic_rec = topic_repo.get_topic(topic_id)

    if request.method == 'POST':
        try:
            sample_images_group_name = request.form['sample_images_group_name']
            uploaded_files = request.files.getlist('file[]')
            sample_images_group_manager.add_sample_images_group(topic_id,
                                                                sample_images_group_name,
                                                                uploaded_files)
            db.session.commit()
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('add_sample_images_group.html',
                                                    ex.message,
                                                    'danger',
                                                    ex)
        message = 'Successfully added a new sample images group for topic %s' % topic_rec.name
        logger.info(message)

        return redirect_with_message(url_for('list_sample_images', topic_id=topic_id), message, 'info')
    return render_scm_template('add_sample_images_group.html',
                               topic_rec=topic_rec)

@app.route('/update_sample_images_group/<int:sample_images_group_id>', methods=['GET', 'POST'])
def update_sample_images_group(sample_images_group_id):
    sample_image_path_recs = sample_image_path_repo.get_sample_image_paths(sample_images_group_id)
    sample_images_group_rec = sample_images_group_repo.get_sample_images_group(sample_images_group_id)
    topic_recs = topic_repo.get_all_topics()
    
    if request.method == 'POST':
        try:
            remaining_sample_image_path_ids = __extract_remaining_image_path_ids(request.form, 'existing_image_')
            sample_images_group_name = request.form['sample_images_group_name']
            topic_id = int(request.form['topic_id'])
            uploaded_files = request.files.getlist('file[]')

            sample_images_group_manager.update_sample_images_group(sample_images_group_id,
                                                                   topic_id,
                                                                   sample_images_group_name,
                                                                   sample_image_path_recs,
                                                                   remaining_sample_image_path_ids,
                                                                   uploaded_files)
            db.session.commit()
            sample_image_path_recs = sample_image_path_repo.get_sample_image_paths(sample_images_group_id)
            
            message = 'Successfully updated sample images'
            logger.info(message)

            flash(message, 'info')
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('update_sample_images_group.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    topic_recs=topics_recs,
                                                    sample_images_group_rec=sample_images_group_rec,
                                                    sample_image_path_recs=sample_image_path_recs)
    
    return render_scm_template('update_sample_images_group.html',
                               topic_recs=topic_recs,
                               sample_images_group_rec=sample_images_group_rec,
                               sample_image_path_recs=sample_image_path_recs)

def __extract_remaining_image_path_ids(props_dict, existing_image_prefix):
    i = 0
    remaining_image_path_ids = []

    while True:
        existing_image_i = existing_image_prefix + str(i)
        if existing_image_i not in props_dict:
            break

        remaining_image_path_ids.append(int(props_dict[existing_image_i]))
        i += 1

    return remaining_image_path_ids

@app.route('/delete_sample_images_group/<int:sample_images_group_id>', methods=['GET', 'POST'])
def delete_sample_images_group(sample_images_group_id):
    sample_images_group_rec = sample_images_group_repo.get_sample_images_group(sample_images_group_id)
    topic_id = sample_images_group_rec.topic_id
    sample_images_group_name = sample_images_group_rec.name

    try:
        sample_images_group_manager.delete_sample_images_group(sample_images_group_id)
        db.session.commit()
    except ScmException as ex:
        db.session.rollback()
        message = 'Failed to delete sample_images_group "%s" (%s)' % (sample_images_group_name, sample_images_group_id)
        return redirect_with_message(url_for('list_sample_images', topic_id=topic_id),
                                    message,
                                    'danger')
    
    message = 'Successfully deleted sample_images_group "%s" (%s)' % (sample_images_group_name, sample_images_group_id)
    logger.info(message)

    return redirect_with_message(url_for('list_sample_images', topic_id=topic_id),
                                message,
                                'info')

@app.route('/sample_images_group_details/<int:sample_images_group_id>', methods=['GET', 'POST'])
def sample_images_group_details(sample_images_group_id):
    sample_images_group_rec = sample_images_group_repo.get_sample_images_group(sample_images_group_id)
    sample_image_path_recs = sample_image_path_repo.get_sample_image_paths(sample_images_group_id)

    return render_scm_template('sample_images_group_details.html',
                                sample_images_group_rec=sample_images_group_rec,
                                sample_image_path_recs=sample_image_path_recs)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0');
