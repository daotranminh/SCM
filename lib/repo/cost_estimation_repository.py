import logging

from flask_sqlalchemy import sqlalchemy

from init import CostEstimation, FormulaSubFormula, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class CostEstimationRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_cost_estimation(self, cost_esitimation_id):
        return CostEstimation.query. \
            filter(CostEstimation.id == cost_esitimation_id). \
            first()

    def get_cost_estimations_of_formula(self, formula_id):
        formula_subformula_query = self.db.session.query(FormulaSubFormula.subformula_id, FormulaSubFormula.count). \
            filter(FormulaSubFormula.formula_id == formula_id). \
            subquery()

        return self.db.session.query(CostEstimation, formula_subformula_query.c.count). \
            filter(CostEstimation.is_current == True). \
            join(formula_subformula_query, CostEstimation.subformula_id == formula_subformula_query.c.subformula_id). \
            all()

    def get_current_cost_estimation_of_subformula(self, subformula_id):
        return CostEstimation.query. \
            filter(CostEstimation.subformula_id == subformula_id, CostEstimation.is_current == True). \
            first()

    def add_cost_estimation(self, subformula_id):
        try:
            cost_estimation_rec = CostEstimation(subformula_id=subformula_id)
            self.db.session.add(cost_estimation_rec)
            self.db.session.flush()
            return cost_estimation_rec.id
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add cost_estimation_rec. Details: %s' % (str(ex))
            CostEstimationRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_COST_ESTIMATION_FAILED, message)

    def update_total_cost(self, 
                          cost_estimation_id, 
                          total_cost):
        cost_estimation_rec = self.get_cost_estimation(cost_estimation_id)
        cost_estimation_rec.total_cost = total_cost
        self.db.session.flush()

        message = 'Set total_cost of cost_estimation_rec %s to %s' % (cost_estimation_id, total_cost)
        CostEstimationRepository.logger.info(message)