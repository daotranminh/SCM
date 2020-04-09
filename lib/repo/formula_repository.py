import logging

from flask_sqlalchemy import sqlalchemy

from init import Formula, Taste, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class FormulaRepository:
    def __init__(self, db):
        self.db = db

    def get_formula(self, formula_id):
        return Formula.query.filter(Formula.id == formula_id).first()

    def get_formula_dto(self, formula_id):
        return self.db.session.query(Formula, Taste). \
            filter(Formula.id == formula_id). \
            filter(Formula.taste_id == Taste.id). \
            first()
        
    def get_all_formulas(self):
        return Formula.query.all()

    def get_formulas_of_taste(self, taste_id):
        return Formula.query.filter(Formula.taste_id == taste_id).all()

    def get_paginated_formulas(self,
                               page,
                               per_page,
                               search_text):
        formula_recs = Formula.query
        if search_text is not None and search_text != '':
            search_pattern = '%' + search_text + '%'
            formula_recs = formula_recs.filter((Formula.name.ilike(search_pattern)) |
                                                (Formula.description.ilike(search_pattern)))
        return formula_recs.paginate(page, per_page, error_out=False)

    def add_formula(self,
                  name,
                  taste_id,
                  description,
                  note):
        try:
            formula_rec = Formula(taste_id=taste_id,
                                  name=name,
                                  description=description,
                                  note=note)
            self.db.session.add(formula_rec)
            self.db.session.flush()
            return formula_rec.id
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add formula record. Details: %s' % (str(ex))
            logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_FORMULA_FAILED, message)

    def set_flag_has_up_to_date_cost_estimation(self, formula_id, flag):
        formula_rec = self.get_formula(formula_id)
        formula_rec.has_up_to_date_cost_estimation = flag