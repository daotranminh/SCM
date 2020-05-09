import logging
import datetime

from flask_sqlalchemy import sqlalchemy

from init import ProductCostEstimation, config
from utilities.scm_enums import ErrorCodes, BoxStatus
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class ProductCostEstimationRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def add_product_cost_estimation(self,
                                    product_id,
                                    cost_estimation_id):
        try:
            product_cost_estimation_rec = ProductCostEstimation(product_id=product_id,
                                                                cost_estimation_id=cost_estimation_id)

            self.db.session.add(product_cost_estimation_rec)
            self.db.session.flush()
            return product_cost_estimation_rec.id
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add product_cost_estimation record. Details: %s' % (str(ex))
            ProductCostEstimationRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_PRODUCT_COST_ESTIMATION_FAILED, message)

    def delete_cost_estimation_of_product(self, product_id):
        ProductCostEstimation.query.filter(ProductCostEstimation.product_id == product_id).delete()
        self.db.session.flush()