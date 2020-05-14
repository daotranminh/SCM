import logging

from flask_sqlalchemy import sqlalchemy

from init import Plate, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class PlateRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_plate(self, plate_id):
        return Plate.query.filter(Plate.id == plate_id).first()

    def get_all_plates(self):
        return Plate.query. \
            order_by(Plate.name). \
            all()

    def add_plate(self,
                  name,
                  description,
                  unit_count,
                  unit_price):
        try:
            plate_rec = Plate(name=name,
                              description=description,
                              unit_count=unit_count,
                              unit_price=unit_price)
            self.db.session.add(plate_rec)
            self.db.session.flush()
            return plate_rec.id
        
        except sqlalchemy.exc.SQLAlchemyError as e:
            message = 'Error: failed to add plate. Details: %s' % (str(e))
            PlateRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_PLATE_FAILED, message)

    def update_plate(self,
                     plate_id,
                     name,
                     description,
                     unit_count,
                     unit_price):
        plate_rec = self.get_plate(plate_id)
        self.update_plate_rec(plate_rec, name, description, unit_count, unit_price)

    def update_plate_rec(self,
                         plate_rec,
                         name,
                         description,
                         unit_count,
                         unit_price):
        plate_rec.name = name
        plate_rec.description = description
        plate_rec.unit_count = unit_count
        plate_rec.unit_price = unit_price
        self.db.session.flush()