from flask import Flask, Response, render_template, request, flash, redirect, make_response, session, url_for

from init import app, db
from lib.forms.customer_forms import AddCustomerForm
from lib.forms.material_forms import AddMaterialForm
from lib.forms.material_forms import UpdateMaterialForm

from lib.repo.material_repository import MaterialRepository
from lib.repo.material_version_repository import MaterialVersionRepository
from lib.repo.customer_repository import CustomerRepository

from lib.managers.material_manager import MaterialManager

from utilities import scm_constants
from utilities.scm_exceptions import ScmException

material_repo = MaterialRepository(db)
material_version_repo = MaterialVersionRepository(db)
customer_repo = CustomerRepository(db)

material_manager = MaterialManager(material_repo,
                                   material_version_repo)

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

    return render_template(site_html,
                           **kwargs,
                           menu_configuration=session[scm_constants.MENU_CONFIGURATION])

def redirect_with_message(url, message, message_type):
    flash(message, message_type)
    return redirect(url)

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
            flash(message, 'info')
            return redirect(url_for('list_materials'))
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
        return render_scm_template('material.html', form=form)
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
            flash(message, 'info')
            return redirect(url_for('list_materials'))
        except ScmException as ex:
            db.session.rollback()
            return render_scm_template_with_message('material.html',
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
    form = AddCustomerForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data.strip()
        address = form.address.data.strip()
        phone = form.phone.data.strip()
        email_address = form.email_address.data.strip()
        facebook = form.facebook.data.strip()

        customer_repo.add_customer(name,
                                   address,
                                   phone,
                                   email_address,
                                   facebook)
        db.session.commit()
    return render_scm_template('add_customer.html', form=form)

@app.route('/list_customers', methods=['GET', 'POST'])
def list_customers():
    customers = customer_repo.get_all_customers()
    return render_scm_template('list_customers.html', customers=customers)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0');
