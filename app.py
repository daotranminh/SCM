import logging
from flask import Flask, Response, render_template, request, flash, redirect, make_response, session, url_for

from init import app, db, config
from lib.forms.customer_forms import AddCustomerForm
from lib.forms.customer_forms import UpdateCustomerForm
from lib.forms.decoration_form_forms import AddDecorationFormForm
from lib.forms.decoration_form_forms import UpdateDecorationFormForm
from lib.forms.material_forms import AddMaterialForm
from lib.forms.material_forms import UpdateMaterialForm
from lib.forms.taste_forms import AddTasteForm
from lib.forms.taste_forms import UpdateTasteForm
from lib.forms.topic_forms import AddTopicForm
from lib.forms.topic_forms import UpdateTopicForm

from lib.repo.decoration_form_repository import DecorationFormRepository
from lib.repo.material_repository import MaterialRepository
from lib.repo.material_version_repository import MaterialVersionRepository
from lib.repo.material_formula_repository import MaterialFormulaRepository
from lib.repo.customer_repository import CustomerRepository
from lib.repo.taste_repository import TasteRepository
from lib.repo.topic_repository import TopicRepository
from lib.repo.formula_repository import FormulaRepository

from lib.managers.material_manager import MaterialManager
from lib.managers.customer_manager import CustomerManager
from lib.managers.topic_manager import TopicManager
from lib.managers.formula_manager import FormulaManager

from utilities import scm_constants
from utilities.scm_exceptions import ScmException

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

decoration_form_repo = DecorationFormRepository(db)
material_repo = MaterialRepository(db)
material_formula_repo = MaterialFormulaRepository(db)
material_version_repo = MaterialVersionRepository(db)
customer_repo = CustomerRepository(db)
taste_repo = TasteRepository(db)
topic_repo = TopicRepository(db)
formula_repo = FormulaRepository(db)

material_manager = MaterialManager(material_repo,
                                   material_version_repo)
customer_manager = CustomerManager(customer_repo)
topic_manager = TopicManager(topic_repo)
formula_manager = FormulaManager(formula_repo,
                                 material_formula_repo,
                                 taste_repo)

####################################################################################
# MENU
####################################################################################
@app.before_request
def menu_setup():
    production_funcs = [
        ['list_materials', 'List of materials'],
        ['list_formulas', 'List of formulas'],
        ['list_decorations', 'List of decorations'],
        ['list_tastes', 'List of tastes']
    ]

    business_funcs = [
        ['list_customers', 'List of customers'],
        ['list_orders', 'List of orders'],        
    ]

    exhibition_funcs = [
        ['list_topics', 'List of topics'],        
        ['list_cakes', 'List of cakes']      
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

####################################################################################
# TASTE
####################################################################################
@app.route('/add_taste', methods=['GET', 'POST'])
def add_taste():
    form = AddTasteForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            name = form.name.data.strip()
            description = form.description.data.strip()
            taste_repo.add_taste(name=name, description=description)
            db.session.commit()
            message = 'Successfully added taste %s' % name
            return redirect_with_message(url_for('list_tastes'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            message = 'Failed to add taste %s' % name
            flash(message, 'danger')
            return render_scm_template('add_taste.html', form=form)
    else:
        return render_scm_template('add_taste.html', form=form)

@app.route('/update_taste/<int:taste_id>', methods=['GET', 'POST'])
def update_taste(taste_id):
    if request.method == 'GET':
        taste_rec = taste_repo.get_taste(taste_id)
        form = UpdateTasteForm(request.form, taste_rec)
        return render_scm_template('update_taste.html', form=form)
    elif request.method == 'POST':
        try:
            form = UpdateTasteForm(request.form, None)
            name = form.name.data.strip()
            description = form.description.strip()
            taste_repo.update_taste(taste_id,
                                    name,
                                    description)
            db.session.commit()
            message = 'Successfully updated taste %s (%s)' % (name, taste_id)
            return redirect_with_message(url_for('list_tastes'), message, 'info')
        except SmcException as ex:
            db.session.rollback()
            return render_scm_template_with_message('update_taste.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    form=form)            

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
    form = AddDecorationFormForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            name = form.name.data.strip()
            description = form.description.data.strip()
            
            decoration_form_repo.add_decoration_form(name=name,
                                                     description=description)
            db.session.commit()
            message = 'Successfully added decoration form %s' % name
            return redirect_with_message(url_for('list_decoration_forms'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            message = 'Failed to add decoration form %s' % name
            flash(message, 'danger')
            return render_scm_template('add_decoration_form.html', form=form)
    else:
        return render_scm_template('add_decoration_form.html', form=form)

@app.route('/update_decoration_form/<int:decoration_form_id>', methods=['GET', 'POST'])
def update_decoration_form(decoration_form_id):
    if request.method == 'GET':
        decoration_form_rec = decoration_form_repo.get_decoration_form(decoration_form_id)
        form = UpdateDecorationFormForm(request.form, decoration_form_rec)
        return render_scm_template('update_decoration_form.html', form=form)
    elif request.method == 'POST':
        try:
            form = UpdateDecorationFormForm(request.form, None)
            name = form.name.data.strip()
            description = form.description.data.strip()
            
            decoration_form_repo.update_decoration_form(decoration_form_id,
                                                        name,
                                                        description)
            db.session.commit()
            message = 'Successfully updated decoration form %s (%s)' % (name, decoration_form_id)
            return redirect_with_message(url_for('list_decoration_forms'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('update_decoration_form.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    form=form)

@app.route('/list_decoration_forms', methods=['GET', 'POST'])
def list_decoration_forms():
    decoration_form_recs = decoration_form_repo.get_all_decoration_forms()
    return render_scm_template('list_decoration_forms.html', decoration_form_recs=decoration_form_recs)

####################################################################################
# MATERIALS
####################################################################################
@app.route('/add_material', methods=['GET', 'POST'])
def add_material():
    form = AddMaterialForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            name = form.name.data.strip()
            description = form.description.data.strip()
            unit = form.unit.data
            unit_price = form.unit_price.data.strip()
            is_organic = False
            if form.is_organic.data == [0]:
                is_organic = True

            material_manager.add_material(name=name,
                                          description=description,
                                          is_organic=is_organic,
                                          unit=unit,
                                          unit_price=unit_price)
            db.session.commit()

            message = 'Successfully added material (%s, %s/%s)' % \
                      (name,
                       unit_price,
                       unit)
            return redirect_with_message(url_for('list_materials'), message, 'info')
        except ScmException as ex:
            message = 'Failed to add material (%s, %s/%s)' % \
                      (name,
                       unit_price,
                       unit)
            flash(message, 'danger')            
            return render_scm_template('add_material.html', form=form)
    else:
        return render_scm_template('add_material.html', form=form)

@app.route('/update_material/<int:material_id>', methods=['GET', 'POST'])
def update_material(material_id):
    if request.method == 'GET':
        material_rec = material_repo.get_material(material_id)
        material_version_rec = material_version_repo.get_latest_version_of_material(material_id)
        form = UpdateMaterialForm(request.form,
                                  material_rec,
                                  material_version_rec)
        return render_scm_template('update_material.html', form=form)
    elif request.method == 'POST':
        try:
            form = UpdateMaterialForm(request.form, None, None)
            name = form.name.data.strip()
            description = form.name.data.strip()
            unit = form.unit.data
            unit_price = form.unit_price.data
            is_organic = False
            if form.is_organic.data == [0]:
                is_organic = True

            material_manager.update_material(material_id,
                                             name,
                                             description,
                                             unit,
                                             unit_price,
                                             is_organic)
            db.session.commit()
            message = 'Successfully updated material (%s, %s/%s)' % \
                      (name,
                       unit_price,
                       unit)
            return redirect_with_message(url_for('list_materials'), message, 'info')
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('update_material.html',
                                                    ex.message,
                                                    'danger',
                                                    ex,
                                                    form=form)

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
    customer_choices = customer_manager.get_customer_choices()
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
    customer_choices = customer_manager.get_customer_choices()
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
        amount = float(props_dict[material_amount_i])
            
        material_ids.append(material_id)
        amounts.append(amount)
        i += 1

    return formula_name, taste_id, description, note, material_ids, amounts

@app.route('/add_formula', methods=['GET', 'POST'])
def add_formula():
    material_dtos = material_manager.get_material_dtos()
    taste_recs = taste_repo.get_all_tastes()

    if request.method == 'POST':
        try:
            formula_name, taste_id, description, note, material_ids, amounts = __extract_formula_props(request.form)

            formula_manager.add_formula(formula_name,
                                        taste_id,
                                        description,
                                        note,
                                        material_ids,
                                        amounts)

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
    formula_rec, taste_rec, material_dtos, total_cost = formula_manager.get_formula_details(formula_id)

    return render_scm_template('formula_details.html',
                               formula_rec=formula_rec,
                               taste_rec=taste_rec,
                               material_dtos=material_dtos,
                               total_cost=total_cost)

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

@app.route('/add_decoration', methods=['GET', 'POST'])
def add_decoration():
    topic_recs = topic_repo.get_all_topics()

    if request.method == 'POST':
        print(request.form)
        uploaded_files = request.files.getlist('file[]')
        print(uploaded_files)
        
        return render_scm_template('add_decoration.html',
                                   topic_recs=topic_recs,
                                   decoration_forms=scm_constants.DECORATION_FORMS,
                                   decoration_techniques=scm_constants.DECORATION_TECHNIQUES)

    return render_scm_template('add_decoration.html',
                               topic_recs=topic_recs,
                               decoration_forms=scm_constants.DECORATION_FORMS,
                               decoration_techniques=scm_constants.DECORATION_TECHNIQUES)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0');
