import logging

from flask_sqlalchemy import sqlalchemy

from init import FixedBox, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class FixedBoxRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_fixed_box(self, fixed_box_id):
        return FixedBox.query.filter(FixedBox.id == fixed_box_id).first()

    def get_fixed_box_of_product(self, product_id):
        return FixedBox.query.filter(FixedBox.product_id == product_id).first()

    def add_fixed_box(self,
                      product_id,            
                      original_box_id,
                      name,
                      description,
                      unit_count,
                      unit_price):
        try:
            fixed_box_rec = FixedBox(product_id=product_id,
                                     original_box_id=original_box_id,
                                     name=name,
                                     description=description,
                                     unit_count=unit_count,
                                     unit_price=unit_price)
            self.db.session.add(fixed_box_rec)
            self.db.session.flush()
            return fixed_box_rec.id
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add fixed_box_rec. Details: %s' % (str(ex))
            FixedBoxRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_FIXED_BOX_FAILED, message)