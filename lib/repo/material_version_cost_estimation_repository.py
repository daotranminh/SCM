import logging

from flask_sqlalchemy import sqlalchemy

from init import MaterialVersionCostEstimation, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class MaterialVersionCostEstimationRepository:
    def __init__(self, db):
        self.db = db

    def get_material_version_cost_estimation_of_cost_estimation(self, cost_esitimation_id):
        return MaterialVersionCostEstimation.query. \
            filter(MaterialVersionCostEstimation.cost_esitimation_id == cost_esitimation_id). \
            all()

    def add_material_version_cost_estimation(self,
                                             material_verion_id,
                                             cost_estimation_id,
                                             unit_amount,
                                             unit,
                                             unit_price,
                                             amount,
                                             cost):
        try:
            material_version_cost_estimation_rec = MaterialVersionCostEstimation(
                material_verion_id=material_verion_id,
                cost_estimation_id=cost_estimation_id,
                unit_amount=unit_amount,
                unit=unit,
                unit_price=unit_price,
                amount=amount,
                cost=cost)
            self.db.session.add(material_version_cost_estimation_rec)        
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add material_version_cost_estimation_rec. Details: %s' % (str(ex))
            logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_MATERIAL_VERSION_COST_ESTIMATION_FAILED, message)