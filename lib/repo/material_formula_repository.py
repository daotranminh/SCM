import logging

from flask_sqlalchemy import sqlalchemy
from init import MaterialFormula, config

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class MaterialFormulaRepository:
    def __init__(self, db):
        self.db = db

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
