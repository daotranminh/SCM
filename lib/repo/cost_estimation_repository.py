import logging

from flask_sqlalchemy import sqlalchemy

from init import CostEstimation, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class CostEstimationRepository:
    def __init__(self, db):
        self.db = db

    def get_cost_estimation(self, cost_esitimation_id):
        return CostEstimation.query. \
            filter(CostEstimation.id == cost_esitimation_id). \
            first()

    def add_cost_estimation(self, formula_id,):
        try:
            cost_estimation_rec = CostEstimation(formula_id=formula_id)
            self.db.session.add(cost_estimation_rec)
            self.db.flush()
            return cost_estimation_rec.id
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add cost_estimation_rec. Details: %s' % (str(ex))
            logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_COST_ESTIMATION_FAILED, message)

    def update_total_cost(self, 
                          cost_estimation_id, 
                          total_cost):
        cost_estimation_rec = self.get_cost_estimation(cost_esitimation_id)
        cost_estimation_rec.total_cost = total_cost