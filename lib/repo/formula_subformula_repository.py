import logging

from flask_sqlalchemy import sqlalchemy
from init import FormulaSubFormula, config
from utilities.scm_logger import ScmLogger

class FormulaSubFormulaRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_count(self, formula_id, subformula_id):
        return self.db.session.query(FormulaSubFormula.count). \
            filter(FormulaSubFormula.formula_id == formula_id, FormulaSubFormula.subformula_id == subformula_id). \
            first()

    def get_formula_subformulas_of_formula(self, formula_id):
        return FormulaSubFormula.query. \
            filter(FormulaSubFormula.formula_id == formula_id). \
            all()

    def get_formulas_of_subformula(self, subformula_id):
        return FormulaSubFormula.query. \
            filter(FormulaSubFormula.subformula_id == subformula_id). \
            all()

    def delete_formula_subformula(self, formula_subformula_id):
        FormulaSubFormula.query. \
            filter(FormulaSubFormula.id == formula_subformula_id). \
            delete()
        self.db.session.flush()

    def delete_subformulas_of_formula(self, formula_id):
        FormulaSubFormula.query. \
            filter(FormulaSubFormula.formula_id == formula_id). \
            delete()
        self.db.session.flush()

    def add_formula_subformula(self,
                               formula_id,
                               subformula_id,
                               subformula_count):
        try:
            formula_subformula_rec = FormulaSubFormula(formula_id=formula_id,
                                                       subformula_id=subformula_id,
                                                       count=subformula_count)
            self.db.session.add(formula_subformula_rec)
            self.db.session.flush()
        
        except sqlalchemy.exc.SQLAlchemyError as e:
            message = 'Error: failed to add formula_subformula record. Details: %s' % (str(e))
            FormulaSubFormulaRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_FORMULA_SUBFORMULA_FAILED, message)
