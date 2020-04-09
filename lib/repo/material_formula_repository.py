import logging

from flask_sqlalchemy import sqlalchemy
from init import Material, MaterialVersion, MaterialFormula, config

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class MaterialFormulaRepository:
    def __init__(self, db):
        self.db = db

    def get_materials_of_formula(self, formula_id):
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
            logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_MATERIAL_FORMULA_FAILED, message)
