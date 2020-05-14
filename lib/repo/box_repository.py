import logging

from flask_sqlalchemy import sqlalchemy

from init import Box, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class BoxRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_box(self, box_id):
        return Box.query.filter(Box.id == box_id).first()

    def get_all_boxes(self):
        return Box.query. \
            order_by(Box.name). \
            all()

    def add_box(self,
                name,
                description,
                unit_count,
                unit_price):
        try:
            box_rec = Box(name=name,
                         description=description,
                         unit_count=unit_count,
                         unit_price=unit_price)
            self.db.session.add(box_rec)
            self.db.session.flush()
            return box_rec.id
        
        except sqlalchemy.exc.SQLAlchemyError as e:
            message = 'Error: failed to add box. Details: %s' % (str(e))
            PlateRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_BOX_FAILED, message)

    def update_box(self,
                   box_id,
                   name,
                   description,
                   unit_count,
                   unit_price):
        box_rec = self.get_box(box_id)
        self.update_box_rec(box_rec, name, description, unit_count, unit_price)

    def update_box_rec(self,
                       box_rec,
                       name,
                       description,
                       unit_count,
                       unit_price):
        box_rec.name = name
        box_rec.description = description
        box_rec.unit_count = unit_count
        box_rec.unit_price = unit_price
        self.db.session.flush()