import logging

from flask_sqlalchemy import sqlalchemy
from init import MaterialVersion, MaterialFormula, config

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
        sub_query_material_version = self.db.session. \
                                     query(MaterialVersion.material_id, MaterialVersion.unit_price). \
                                     filter(MaterialVersion.is_current == True). \
                                     subquery()
        material_formulas = self.db.session. \
                            query(MaterialFormula, sub_query_material_version.c.unit_price). \
                            filter(MaterialFormula.formula_id == formula_id). \
                            join(sub_query_material_version, sub_query_material_version.c.material_id == MaterialFormula.material_id). \
                            all()

        print(material_formulas)
        
        return material_formulas
        
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
