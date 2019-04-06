from flask import Flask, Response, render_template, request, flash, redirect, make_response

from init import app, db
from lib.forms.material_forms import AddMaterialForm
from lib.repo.material_repository import MaterialRepository

material_repo = MaterialRepository(db)

@app.route('/add-material', methods=['GET', 'POST'])
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

    return render_template('add_material.html', form=form)

@app.route('/list-material', methods=['GET', 'POST'])
def list_material():
    materials = material_repo.get_all_materials()
    return render_template('list_materials.html', materials=materials)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0');
