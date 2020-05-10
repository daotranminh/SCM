import logging

from flask_sqlalchemy import sqlalchemy

from init import FixedFormula, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class FixedFormulaRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_fixed_formulas_of_product(self, product_id):
        return FixedFormula.query. \
            filter(FixedFormula.product_id == product_id). \
            all()

    def add_fixed_formula(self,
                          product_id,
                          original_formula_id,
                          name,
                          description,
                          note,
                          total_cost):
        try:
            fixed_formula_rec = FixedFormula(product_id=product_id,
                                             original_formula_id=original_formula_id,
                                             name=name,
                                             description=description,
                                             note=note,
                                             total_cost=total_cost)
            self.db.session.add(fixed_formula_rec)
            self.db.session.flush()
            return fixed_formula_rec.id
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add fixed_subformula_rec. Details: %s' % (str(ex))
            CostEstimationRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_FORMULA_FAILED, message)