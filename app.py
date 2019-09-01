from flask import Flask, Response, render_template, request, flash, redirect, make_response, session

from init import app, db
from lib.forms.material_forms import AddMaterialForm
from lib.forms.customer_forms import AddCustomerForm

from lib.repo.material_repository import MaterialRepository
from lib.repo.customer_repository import CustomerRepository

from utilities import scm_constants

material_repo = MaterialRepository(db)
customer_repo = CustomerRepository(db)

####################################################################################
# MENU
####################################################################################
@app.before_request
def menu_setup():
    customer_funcs = [
        ['add_customer', 'Add customer'],
        ['list_customers', 'List customers']
    ]
    
    statistics_funcs = [
        ['statistics_order', 'Order'],
        ['statistics_income', 'Income']
    ]

    menu_configuration = {
        'Statistics': statistics_funcs,
        'Customer': customer_funcs        
    }

    session[scm_constants.MENU_CONFIGURATION] = menu_configuration

####################################################################################
# HELPERS
####################################################################################
def render_scm_template(site_html, **kwargs):
    return render_template(site_html,
                           **kwargs,
                           menu_configuration=session[scm_constants.MENU_CONFIGURATION])
    
####################################################################################
# MATERIALS
####################################################################################
@app.route('/add_material', methods=['GET', 'POST'])
def add_material():
    form = AddMaterialForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data.strip()
        unit = form.unit.data
        unit_price = form.unit_price.data.strip()
        #is_organic = form.is_organic
        
        material_repo.add_material(name=name,
                                   is_organic=False,
                                   unit=unit,
                                   unit_price=unit_price)
        db.session.commit()

    return render_scm_template('add_material.html', form=form)

@app.route('/list_materials', methods=['GET', 'POST'])
def list_materials():
    materials = material_repo.get_all_materials()
    return render_scm_template('list_materials.html', materials=materials)

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
