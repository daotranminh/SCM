import logging
import os
import datetime
from decimal import Decimal

from flask import Flask, Response, render_template, request, flash, redirect, make_response, session, url_for
from werkzeug.utils import secure_filename

from init import app, db, config
from lib.forms.customer_forms import AddCustomerForm
from lib.forms.customer_forms import UpdateCustomerForm
from lib.forms.decoration_form_forms import AddDecorationFormForm
from lib.forms.decoration_form_forms import UpdateDecorationFormForm
from lib.forms.decoration_technique_forms import AddDecorationTechniqueForm
from lib.forms.decoration_technique_forms import UpdateDecorationTechniqueForm
from lib.forms.delivery_method_forms import AddDeliveryMethodForm
from lib.forms.delivery_method_forms import UpdateDeliveryMethodForm
from lib.forms.material_forms import AddMaterialForm
from lib.forms.material_forms import UpdateMaterialForm
from lib.forms.taste_forms import AddTasteForm
from lib.forms.taste_forms import UpdateTasteForm
from lib.forms.topic_forms import AddTopicForm
from lib.forms.topic_forms import UpdateTopicForm
from lib.forms.order_forms import AddOrderForm
from lib.forms.order_forms import UpdateOrderForm

from lib.repo.delivery_method_repository import DeliveryMethodRepository
from lib.repo.decoration_form_repository import DecorationFormRepository
from lib.repo.decoration_technique_repository import DecorationTechniqueRepository
from lib.repo.material_repository import MaterialRepository
from lib.repo.material_version_repository import MaterialVersionRepository
from lib.repo.material_formula_repository import MaterialFormulaRepository
from lib.repo.material_version_cost_estimation_repository import MaterialVersionCostEstimationRepository
from lib.repo.cost_estimation_repository import CostEstimationRepository
from lib.repo.customer_repository import CustomerRepository
from lib.repo.taste_repository import TasteRepository
from lib.repo.topic_repository import TopicRepository
from lib.repo.formula_repository import FormulaRepository
from lib.repo.order_repository import OrderRepository
from lib.repo.product_repository import ProductRepository
from lib.repo.product_image_path_repository import ProductImagePathRepository
from lib.repo.sample_image_path_repository import SampleImagePathRepository
from lib.repo.sample_images_group_repository import SampleImagesGroupRepository

from lib.managers.material_manager import MaterialManager
from lib.managers.customer_manager import CustomerManager
from lib.managers.taste_manager import TasteManager
from lib.managers.topic_manager import TopicManager
from lib.managers.formula_manager import FormulaManager
from lib.managers.delivery_method_manager import DeliveryMethodManager
from lib.managers.order_manager import OrderManager
from lib.managers.product_manager import ProductManager
from lib.managers.sample_images_group_manager import SampleImagesGroupManager
from lib.managers.decoration_form_manager import DecorationFormManager
from lib.managers.decoration_technique_manager import DecorationTechniqueManager

from utilities import scm_constants
from utilities.scm_enums import OrderStatus, PaymentStatus
from utilities.scm_exceptions import ScmException

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

delivery_method_repo = DeliveryMethodRepository(db)
decoration_form_repo = DecorationFormRepository(db)
decoration_technique_repo = DecorationTechniqueRepository(db)
material_repo = MaterialRepository(db)
material_formula_repo = MaterialFormulaRepository(db)
material_version_repo = MaterialVersionRepository(db)
material_version_cost_estimation_repo = MaterialVersionCostEstimationRepository(db)
cost_estimation_repo = CostEstimationRepository(db)
customer_repo = CustomerRepository(db)
taste_repo = TasteRepository(db)
topic_repo = TopicRepository(db)
formula_repo = FormulaRepository(db)
order_repo = OrderRepository(db)
sample_image_path_repo = SampleImagePathRepository(db)
sample_images_group_repo = SampleImagesGroupRepository(db)
product_repo = ProductRepository(db)
product_image_path_repo = ProductImagePathRepository(db)

taste_manager = TasteManager(taste_repo)
delivery_method_manager = DeliveryMethodManager(delivery_method_repo)
material_manager = MaterialManager(material_repo,
                                   material_version_repo,
                                   material_formula_repo)
customer_manager = CustomerManager(customer_repo)
topic_manager = TopicManager(topic_repo)
formula_manager = FormulaManager(formula_repo,
                                 material_formula_repo,
                                 taste_repo,
                                 material_version_cost_estimation_repo,
                                 cost_estimation_repo,
                                 product_repo,
                                 order_repo)
order_manager = OrderManager(order_repo,
                            product_repo)
sample_images_group_manager = SampleImagesGroupManager(sample_images_group_repo,
                                                       sample_image_path_repo)
decoration_form_manager = DecorationFormManager(decoration_form_repo)
decoration_technique_manager = DecorationTechniqueManager(decoration_technique_repo)
product_manager = ProductManager(product_repo, 
                                 product_image_path_repo,
                                 sample_image_path_repo)

####################################################################################
# MENU
####################################################################################
@app.before_request
def menu_setup():
    production_funcs = [
        ['list_materials', 'List of materials'],
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
        logger.error(exception)
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
            return redirect_with_message(url_for('list_tastes'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            message = 'Failed to add taste %s' % name
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
    topic_choices = topic_manager.get_topic_choices()
    form = AddTopicForm(request.form, topic_choices)
    if request.method == 'POST' and form.validate():
        try:
            name = form.name.data.strip()
            description = form.description.data.strip()
            parent_id = form.parent_topic.data
            
            topic_repo.add_topic(name=name,
                                 description=description,
                                 parent_id=parent_id)
            db.session.commit()
            message = 'Successfully added topic %s' % name
            return redirect_with_message(url_for('list_topics'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            message = 'Failed to add topic %s' % name
            flash(message, 'danger')
            return render_scm_template('add_topic.html', form=form)
    else:
        return render_scm_template('add_topic.html', form=form)

@app.route('/update_topic/<int:topic_id>', methods=['GET', 'POST'])
def update_topic(topic_id):
    topic_choices = topic_manager.get_topic_choices()
    if request.method == 'GET':
        topic_rec = topic_repo.get_topic(topic_id)
        form = UpdateTopicForm(request.form, topic_rec, topic_choices)
        return render_scm_template('update_topic.html', form=form)
    elif request.method == 'POST':
        try:
            form = UpdateTopicForm(request.form, None, topic_choices)
            name = form.name.data.strip()
            description = form.description.data.strip()
            parent_id = form.parent_topic.data            
            
            topic_repo.update_topic(topic_id,
                                    name,
                                    description,
                                    parent_id)
            db.session.commit()
            message = 'Successfully updated topic %s (%s)' % (name, topic_id)
            return redirect_with_message(url_for('list_topics'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('update_topic.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    form=form)            

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
            print(request.form)
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
    customer_choices = customer_manager.get_customer_choices1()
    form = AddCustomerForm(request.form, customer_choices)

    if request.method == 'POST' and form.validate():
        try:
            name = form.name.data.strip()
            birthday = form.birthday.data
            address = form.address.data.strip()
            phone = form.phone.data.strip()
            email_address = form.email_address.data.strip()
            facebook = form.facebook.data.strip()
            recommended_by = form.recommended_by.data
            note = form.note.data
            
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
            return redirect_with_message(url_for('list_customers'), message, 'info')
        except ScmException as ex:
            message = ex.message
            db.session.rollback()
            return render_scm_template_with_message('add_customer.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    form=form)
    else:
        return render_scm_template('add_customer.html', form=form)

@app.route('/update_customer/<int:customer_id>', methods=['GET', 'POST'])
def update_customer(customer_id):
    customer_choices = customer_manager.get_customer_choices1()
    if request.method == 'GET':
        customer_rec = customer_repo.get_customer(customer_id)
        form = UpdateCustomerForm(request.form, customer_choices, customer_rec)
    
        return render_scm_template('update_customer.html', form=form)
    elif request.method == 'POST':
        try:
            form = UpdateCustomerForm(request.form, customer_choices, None)
            name = form.name.data
            birthday = form.birthday.data
            address = form.address.data
            phone = form.phone.data
            email_address = form.email_address.data
            facebook = form.facebook.data
            recommended_by = form.recommended_by.data
            note = form.note.data

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
            return redirect_with_message(url_for('list_customers'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('material.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    form=form)            

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
# FORMULAS
####################################################################################

@app.route('/list_formulas', methods=['GET', 'POST'], defaults={'page':1})
@app.route('/list_formulas/', methods=['GET', 'POST'], defaults={'page':1})
@app.route('/list_formulas/<int:page>', methods=['GET', 'POST'])
@app.route('/list_formulas/<int:page>/', methods=['GET', 'POST'])
def list_formulas(page):
    per_page = int(config['PAGING']['formulas_per_page'])
    search_text = request.args.get('search_text')
    
    formula_dtos = formula_manager.get_paginated_formula_dtos(page,
                                                              per_page,
                                                              search_text)
    return render_scm_template('list_formulas.html',
                        formula_dtos=formula_dtos)

def __extract_formula_props(props_dict):
    formula_name = props_dict['formula_name']
    taste_id = int(props_dict['taste_id'])
    description = props_dict['formula_description']
    note = props_dict['formula_note']
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

    return formula_name, taste_id, description, note, material_ids, amounts

@app.route('/add_formula', methods=['GET', 'POST'])
def add_formula():
    material_dtos = material_manager.get_material_dtos()
    taste_recs = taste_repo.get_all_tastes()

    if request.method == 'POST':
        message = ''

        try:
            formula_name, taste_id, description, note, material_ids, amounts = __extract_formula_props(request.form)

            new_formula_id = formula_manager.add_formula(formula_name,
                                        taste_id,
                                        description,
                                        note,
                                        material_ids,
                                        amounts)
            db.session.flush()

            formula_manager.estimate_formula_cost(new_formula_id)
            
            db.session.commit()
            message = 'Successfully added formula %s' % formula_name
            return redirect_with_message(url_for('list_formulas'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('add_formula.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    tast_recs=taste_recs,
                                                    material_dtos=material_dtos)

        
    else:
        return render_scm_template('add_formula.html',
                                   taste_recs=taste_recs,
                                   material_dtos=material_dtos)

@app.route('/formula_details/<int:formula_id>', methods=['GET', 'POST'])
def formula_details(formula_id):
    formula_rec, taste_rec, material_dtos = formula_manager.get_formula_details(formula_id)

    return render_scm_template('formula_details.html',
                               formula_rec=formula_rec,
                               taste_rec=taste_rec,
                               material_dtos=material_dtos)

@app.route('/update_formula/<int:formula_id>', methods=['GET', 'POST'])
def update_formula(formula_id):
    formula_rec, material_formulas, total_cost = formula_manager.get_formula_info(formula_id)
    taste_recs = taste_repo.get_all_tastes()
    material_dtos = material_manager.get_material_dtos()

    if request.method == 'POST':
        try:
            formula_name, taste_id, description, note, material_ids, amounts = __extract_formula_props(request.form)

            formula_manager.update_formula(formula_id,
                                           formula_name,
                                           taste_id,
                                           description,
                                           note,
                                           material_ids,
                                           amounts)
            db.session.flush()
            
            formula_manager.estimate_formula_cost(formula_id)

            db.session.commit()
            message = 'Successfully updated formula %s' % formula_id
            return redirect_with_message(url_for('list_formulas'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('update_formula.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    formula_rec=formula_rec,
                                                    material_formulas=material_formulas,
                                                    taste_recs=taste_recs,
                                                    material_dtos=material_dtos,
                                                    total_cost=total_cost)

    return render_scm_template('update_formula.html',
                               formula_rec=formula_rec,
                               material_formulas=material_formulas,
                               taste_recs=taste_recs,
                               material_dtos=material_dtos,
                               total_cost=total_cost)

@app.route('/estimate_formula_cost/<int:formula_id>', methods=['GET', 'POST'])
def estimate_formula_cost(formula_id):
    try:
        formula_rec = formula_repo.get_formula(formula_id)
        if formula_rec.has_up_to_date_cost_estimation == False:
            formula_manager.estimate_formula_cost(formula_id)        
        db.session.commit()
    except ScmException as ex:
            db.session.rollback()
            message = 'Failed to estimate cost of formula %s (%s). Details: %s' % (formula_rec.name, formula_rec.id, str(ex))
            return render_error(message)

    cost_estimation, material_cost_estimation_dtos = formula_manager.get_cost_estimation(formula_id)
    return render_scm_template('cost_estimation.html',
                               formula_rec=formula_rec,
                               cost_estimation=cost_estimation,
                               material_cost_estimation_dtos=material_cost_estimation_dtos)

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
    taste_ids = []
    decoration_form_ids = []
    decoration_technique_ids = []
    with_boxes = []

    i = 0
    while True:
        product_name_id = 'product_name_' + str(i)
        taste_choices_id = 'taste_choices_' + str(i)
        decoration_form_choices_id = 'decoration_form_choices_' + str(i)
        decoration_technique_choices_id = 'decoration_technique_choices_' + str(i)
        with_box_id = 'with_box_' + str(i)
        
        if product_name_id in props_dict:
            product_names.append(props_dict[product_name_id])
            taste_ids.append(int(props_dict[taste_choices_id]))
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
           taste_ids, \
           decoration_form_ids, \
           decoration_technique_ids, \
           with_boxes

@app.route('/add_order', methods=['GET', 'POST'])
def add_order():
    customer_choices = customer_manager.get_customer_choices()
    delivery_method_choices = delivery_method_manager.get_delivery_method_choices()
    taste_choices = taste_manager.get_taste_choices()
    decoration_form_choices = decoration_form_manager.get_decoration_form_choices()
    decoration_technique_choices = decoration_technique_manager.get_decoration_technique_choices()

    if request.method == 'POST':
        try:
            customer_id, \
            ordered_on, \
            delivery_appointment, \
            delivery_method_id, \
            message, \
            product_names, \
            taste_ids, \
            decoration_form_ids, \
            decoration_technique_ids, \
            with_boxes = __extract_order_props(request.form)

            new_order_id = order_manager.add_order(customer_id,
                                                   ordered_on,
                                                   delivery_appointment,
                                                   delivery_method_id,
                                                   message,
                                                   product_names,
                                                   taste_ids,
                                                   decoration_form_ids,
                                                   decoration_technique_ids,
                                                   with_boxes)
            db.session.commit()
            message = 'Successfully added order %s' % str(new_order_id)
            return redirect_with_message(url_for('list_orders'), message, 'info')
        except ScmException as ex:
            db.session.rollback()

    return render_scm_template('add_order.html', 
                                customer_choices=customer_choices,
                                delivery_method_choices=delivery_method_choices,
                                taste_choices=taste_choices,
                                decoration_form_choices=decoration_form_choices,
                                decoration_technique_choices=decoration_technique_choices)    

@app.route('/list_orders', methods=['GET', 'POST'], defaults={'page':1})
@app.route('/list_orders/', methods=['GET', 'POST'], defaults={'page':1})
@app.route('/list_orders<int:page>', methods=['GET', 'POST'])
@app.route('/list_orders/<int:page>', methods=['GET', 'POST'])
def list_orders(page):
    per_page = int(config['PAGING']['orders_per_page'])
    search_text = request.args.get('search_text')

    paginated_order_dtos = order_manager.get_paginated_order_dtos(page,
                                                                  per_page,
                                                                  search_text)

    return render_scm_template('list_orders.html', order_dtos=paginated_order_dtos)

@app.route('/order_details/<int:order_id>', methods=['GET', 'POST'])
def order_details(order_id):
    order_dto = order_manager.get_order_dto(order_id)
    product_dtos = product_manager.get_product_dtos(order_id)

    return render_scm_template('order_details.html',
                               order_dto=order_dto,
                               product_dtos=product_dtos)

@app.route('/update_order/<int:order_id>', methods=['GET', 'POST'])
def update_order(order_id):
    customer_choices = customer_manager.get_customer_choices()
    delivery_method_choices = delivery_method_manager.get_delivery_method_choices()
    product_dtos = product_manager.get_product_dtos(order_id)
    
    if request.method == 'GET':
        order_rec = order_repo.get_order(order_id)
        return render_scm_template('update_order.html',
                                    order_rec=order_rec,
                                    customer_choices=customer_choices,
                                    delivery_method_choices=delivery_method_choices,
                                    product_dtos=product_dtos,
                                    order_status_names=scm_constants.ORDER_STATUS_NAMES,
                                    payment_status_names=scm_constants.PAYMENT_STATUS_NAMES)
    elif request.method == 'POST':        
        try:
            customer_id = request.form['customer_id']
            ordered_on = request.form['ordered_on']
            delivery_appointment = request.form['delivery_appointment']
            delivery_method_id = request.form['delivery_method_id']
            
            order_status = request.form['order_status']
            delivered_on = None
            if order_status == OrderStatus.DELIVERED:
                delivered_on = request.form['delivered_on']

            paid_on = None
            payment_status = request.form['payment_status']
            if payment_status != PaymentStatus.NOT_PAID:
                paid_on = request.form['paid_on']

            message = request.form['message']

            order_repo.update_order(order_id,
                                    customer_id,
                                    delivery_appointment,
                                    delivery_method_id,
                                    ordered_on,
                                    order_status,
                                    delivered_on,
                                    payment_status,
                                    paid_on,
                                    message)
            db.session.commit()
            message = 'Successfully updated order %s' % order_id
            return redirect_with_message(url_for('list_orders'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('update_order.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    order_rec=order_rec,
                                                    customer_choices=customer_choices,
                                                    delivery_method_choices=delivery_method_choices,
                                                    product_dtos=product_dtos,
                                                    order_status_names=scm_constants.ORDER_STATUS_NAMES,
                                                    payment_status_names=scm_constants.PAYMENT_STATUS_NAMES)

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

@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    product_rec = product_repo.get_product(product_id)    
    product_image_path_recs = product_image_path_repo.get_product_image_paths(product_id)
    taste_recs = taste_repo.get_all_tastes()
    decoration_form_recs = decoration_form_repo.get_all_decoration_forms()
    decoration_technique_recs = decoration_technique_repo.get_all_decoration_techniques()    
    sample_images_group_recs = sample_images_group_repo.get_all_sample_images_groups()
    
    selected_taste_id = product_rec.taste_id
    current_product_name = product_rec.name
    selected_decoration_form_id = product_rec.decoration_form_id
    selected_decoration_technique_id = product_rec.decoration_technique_id
    selected_formula_id = product_rec.formula_id
    selected_box_status = product_rec.box_status
    chosen_box_returned_on = product_rec.box_returned_on
    selected_sample_images_group_id = product_rec.sample_images_group_id

    latest_3_sample_image_paths = []
    if product_rec.sample_images_group_id is not None:
        latest_3_sample_image_paths = sample_image_path_repo.get_latest_3_sample_image_paths(product_rec.sample_images_group_id)

    formula_recs = formula_repo.get_formulas_of_taste(selected_taste_id)

    if request.method == 'GET':
        current_product_name = request.args.get('product_name_arg')
        if current_product_name is None:
            current_product_name = product_rec.name
        
        taste_id_arg = request.args.get('taste_id_arg')
        if taste_id_arg is not None: 
            selected_taste_id = int(taste_id_arg)
            formula_recs = formula_repo.get_formulas_of_taste(selected_taste_id)

        decoration_form_id_arg = request.args.get('decoration_form_id_arg')
        if decoration_form_id_arg is not None:
            selected_decoration_form_id = int(decoration_form_id_arg)

        decoration_technique_id_arg = request.args.get('decoration_technique_id_arg')
        if decoration_technique_id_arg is not None:
            selected_decoration_technique_id = int(decoration_technique_id_arg)

        formula_id_arg = request.args.get('formula_id_arg')
        if formula_id_arg is not None:
            selected_formula_id = int(formula_id_arg)

        box_status_arg = request.args.get('box_status_arg')
        if box_status_arg is not None:
            selected_box_status = int(box_status_arg)
            chosen_box_returned_on = request.args.get('box_returned_on_arg')

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
            selected_taste_id = int(request.form['taste_id'])
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

            product_manager.update_product(product_id,
                                           current_product_name,
                                           selected_taste_id,
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
            product_image_path_recs = product_image_path_repo.get_product_image_paths(product_id)
            message = 'Successfully updated product %s (%s)' % (current_product_name, product_id)
            flash(message, 'info')
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('update_sample_images_group.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    taste_recs=taste_recs,
                                                    decoration_form_recs=decoration_form_recs,
                                                    decoration_technique_recs=decoration_technique_recs,
                                                    product_rec=product_rec,
                                                    product_image_path_recs=product_image_path_recs,
                                                    formula_recs=formula_recs,
                                                    box_status_names=scm_constants.BOX_STATUS_NAMES,
                                                    sample_images_group_recs=sample_images_group_recs,
                                                    latest_3_sample_image_paths=latest_3_sample_image_paths,
                                                    current_product_name=current_product_name,
                                                    selected_taste_id=selected_taste_id,
                                                    selected_decoration_form_id=selected_decoration_form_id,
                                                    selected_decoration_technique_id=selected_decoration_technique_id,
                                                    selected_formula_id=selected_formula_id,
                                                    selected_box_status=selected_box_status,
                                                    chosen_box_returned_on=chosen_box_returned_on,
                                                    selected_sample_images_group_id=selected_sample_images_group_id)
    
    return render_scm_template('update_product.html',
                               taste_recs=taste_recs,
                               decoration_form_recs=decoration_form_recs,
                               decoration_technique_recs=decoration_technique_recs,
                               product_rec=product_rec,
                               product_image_path_recs=product_image_path_recs,
                               formula_recs=formula_recs,
                               box_status_names=scm_constants.BOX_STATUS_NAMES,
                               sample_images_group_recs=sample_images_group_recs,
                               latest_3_sample_image_paths=latest_3_sample_image_paths,
                               current_product_name=current_product_name,
                               selected_taste_id=selected_taste_id,
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
        return redirect_with_message(url_for('order_details', order_id=order_id),
                                     message,
                                     'danger')
    
    message = 'Successfully deleted product "%s" (%s)' % (product_name, product_id)
    return redirect_with_message(url_for('order_details', order_id=order_id),
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

@app.route('/estimate_product_cost/<int:product_id>', methods=['GET', 'POST'])
def estimate_product_cost(product_id):
    try:
        product_rec = product_repo.get_product(product_id)
        if product_rec.is_fixed == False:
            cost_estimation = cost_estimation_repo.get_current_cost_estimation_of_formula(product_rec.formula_id)
            if cost_estimation is not None:
                product_rec.cost_estimation_id = cost_estimation.id
                db.session.commit()
    except ScmException as ex:
        message = 'Error estimating cost of product %s. Details: %s' % (product_id, str(s))
        return render_error(message)
    
    return redirect(url_for('order_details', order_id=product_rec.order_id))

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
        message = 'Successfully added a new sample images group.'
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
