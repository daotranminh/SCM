import logging

from flask_sqlalchemy import sqlalchemy

from init import FixedPlate, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class FixedPlateRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_fixed_plate(self, fixed_plate_id):
        return FixedPlate.query.filter(FixedPlate.id == fixed_plate_id).first()

    def get_fixed_plate_of_product(self, product_id):
        return FixedPlate.query.filter(FixedPlate.product_id == product_id).first()

    def add_fixed_plate(self,
                        product_id,
                        original_plate_id,
                        name,
                        description,
                        unit_count,
                        unit_price):
        try:
            fixed_plate_rec = FixedPlate(product_id=product_id,
                                         original_plate_id=original_plate_id,
                                         name=name,
                                         description=description,
                                         unit_count=unit_count,
                                         unit_price=unit_price)
            self.db.session.add(fixed_plate_rec)
            self.db.session.flush()
            return fixed_plate_rec.id
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add fixed_plate_rec. Details: %s' % (str(ex))
            FixedPlateRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_FIXED_PLATE_FAILED, message)