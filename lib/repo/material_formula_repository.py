import logging

from flask_sqlalchemy import sqlalchemy
from init import Material, MaterialVersion, MaterialFormula, Formula, config
from utilities.scm_logger import ScmLogger

class MaterialFormulaRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_formulas_having_material(self, material_id):
        material_formula_query = self.db.session.query(MaterialFormula.formula_id). \
            filter(MaterialFormula.material_id == material_id). \
            subquery()

        formula_recs = self.db.session. \
            query(Formula). \
            join(material_formula_query, Formula.id == material_formula_query.c.formula_id). \
            all()
        
        return formula_recs

    def get_materials_of_formula(self, formula_id):
        return MaterialFormula.query. \
            filter(MaterialFormula.formula_id == formula_id). \
            all()

    def get_materials_of_formula_w_uprice(self, formula_id):
        sub_query_material = self.db.session. \
                             query(Material.id, Material.unit_amount, Material.unit). \
                             subquery()

        sub_query_material_version = self.db.session. \
                                     query(MaterialVersion.id, MaterialVersion.material_id, MaterialVersion.unit_price). \
                                     filter(MaterialVersion.is_current == True). \
                                     subquery()

        material_formulas_w_uprice = self.db.session. \
                                     query(MaterialFormula, \
                                        sub_query_material.c.unit_amount, \
                                        sub_query_material.c.unit, \
                                        sub_query_material_version.c.id, \
                                        sub_query_material_version.c.unit_price). \
                                     filter(MaterialFormula.formula_id == formula_id). \
                                     join(sub_query_material_version, sub_query_material_version.c.material_id == MaterialFormula.material_id). \
                                     join(sub_query_material, sub_query_material.c.id == MaterialFormula.material_id). \
                                     all()
        return material_formulas_w_uprice

    def get_material_dtos_of_formula(self, formula_id):
        sub_query_material = self.db.session. \
                             query(Material). \
                             order_by(Material.name). \
                             subquery()

        material_formula_dtos = self.db.session. \
                                    query(MaterialFormula, \
                                          sub_query_material.c.name, \
                                          sub_query_material.c.description, \
                                          sub_query_material.c.is_organic, \
                                          sub_query_material.c.unit). \
                                    filter(MaterialFormula.formula_id == formula_id). \
                                    join(sub_query_material, sub_query_material.c.id == MaterialFormula.material_id). \
                                    all()
        return material_formula_dtos
    
    def delete_materials_of_formula(self, formula_id):
        materials_of_formula = MaterialFormula.query. \
                               filter(MaterialFormula.formula_id == formula_id). \
                               delete()

    def add_material_formula(self,
                             formula_id,
                             material_id,
                             amount):
        try:
            material_formula_rec = MaterialFormula(formula_id=formula_id,
                                                   material_id=material_id,
                                                   amount=amount)
            self.db.session.add(material_formula_rec)
        
        except sqlalchemy.exc.SQLAlchemyError as e:
            message = 'Error: failed to add material_formula record. Details: %s' % (str(e))
            MaterialFormulaRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_MATERIAL_FORMULA_FAILED, message)
