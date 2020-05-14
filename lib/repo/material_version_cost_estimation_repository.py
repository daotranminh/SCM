import logging

from flask_sqlalchemy import sqlalchemy

from init import MaterialVersionCostEstimation, Material, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class MaterialVersionCostEstimationRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_material_version_cost_estimation_of_cost_estimation(self, cost_estimation_id):
        material_query = self.db.session. \
                             query(Material.id, Material.name). \
                             subquery()
        material_version_cost_estimations = self.db.session. \
                                            query(MaterialVersionCostEstimation, material_query.c.name). \
                                            filter(MaterialVersionCostEstimation.cost_estimation_id == cost_estimation_id). \
                                            join(material_query, material_query.c.id == MaterialVersionCostEstimation.material_id). \
                                            order_by(material_query.c.name). \
                                            all()

        return material_version_cost_estimations

    def add_material_version_cost_estimation(self,
                                             material_id,
                                             material_version_id,
                                             cost_estimation_id,
                                             unit_amount,
                                             unit,
                                             unit_price,
                                             amount,
                                             cost):
        try:
            material_version_cost_estimation_rec = MaterialVersionCostEstimation(
                material_id=material_id,
                material_version_id=material_version_id,
                cost_estimation_id=cost_estimation_id,
                unit_amount=unit_amount,
                unit=unit,
                unit_price=unit_price,
                amount=amount,
                cost=cost)
            self.db.session.add(material_version_cost_estimation_rec)
            self.db.session.flush()
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add material_version_cost_estimation_rec. Details: %s' % (str(ex))
            MaterialVersionCostEstimationRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_MATERIAL_VERSION_COST_ESTIMATION_FAILED, message)