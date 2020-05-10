import logging

from flask_sqlalchemy import sqlalchemy

from init import FixedSubFormula, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class FixedSubFormulaRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_fixed_subformulas_of_fixed_formula(self, fixed_formula_id):
        return FixedSubFormula.query. \
            filter(FixedSubFormula.fixed_formula_id == fixed_formula_id). \
            all()

    def add_fixed_subformula(self,
                             fixed_formula_id,
                             original_subformula_id,
                             taste_id,
                             taste_name,
                             subformula_type,
                             name,
                             description,
                             note,
                             total_cost,
                             count):
        try:
            fixed_subformula_rec = FixedSubFormula(fixed_formula_id=fixed_formula_id,
                                                   original_subformula_id=original_subformula_id,
                                                   taste_id=taste_id,
                                                   taste_name=taste_id,
                                                   subformula_type=subformula_type,
                                                   name=name,
                                                   description=description,
                                                   note=note,
                                                   total_cost=total_cost,
                                                   count=count)
            self.db.session.add(fixed_subformula_rec)
            self.db.session.flush()
            return fixed_subformula_rec.id
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add fixed_subformula_rec. Details: %s' % (str(ex))
            FixedSubFormulaRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_SUBFORMULA_FAILED, message)