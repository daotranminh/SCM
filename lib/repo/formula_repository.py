import logging

from flask_sqlalchemy import sqlalchemy

from init import Formula, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class FormulaRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_formula(self, formula_id):
        return Formula.query.filter(Formula.id == formula_id).first()

    def delete_formula(self, formula_id):
        Formula.query.filter(Formula.id == formula_id).delete()

    def get_all_formulas(self):
        return Formula.query.all()

    def get_paginated_formulas(self,
                               page,
                               per_page,
                               search_text):
        formula_query = Formula.query

        if search_text is not None and search_text != '':
            search_pattern = '%' + search_text + '%'
            formula_query = formula_query.filter((Formula.name.ilike(search_pattern)) |
                                                 (Formula.description.ilike(search_pattern)))
        return formula_query.paginate(page, per_page, error_out=False)

    def add_formula(self,
                    name,
                    description,
                    note):
        try:
            formula_rec = Formula(name=name,
                                  description=description,
                                  note=note)
            self.db.session.add(formula_rec)
            self.db.session.flush()
            return formula_rec.id
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add formula record. Details: %s' % (str(ex))
            FormulaRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_FORMULA_FAILED, message)

    def set_flag_has_up_to_date_cost_estimation(self, formula_id, flag):
        formula_rec = self.get_formula(formula_id)
        formula_rec.has_up_to_date_cost_estimation = flag

    def update_cost_estimation(self, formula_id, total_cost):
        formula_rec = self.get_formula(formula_id)
        formula_rec.total_cost = total_cost
        formula_rec.has_up_to_date_cost_estimation = true