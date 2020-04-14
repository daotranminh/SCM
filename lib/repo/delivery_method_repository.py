import logging

from flask_sqlalchemy import sqlalchemy

from init import DeliveryMethod, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class DeliveryMethodRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_all_delivery_methods(self):
        return DeliveryMethod.query.all()

    def get_delivery_method(self, id):
        return DeliveryMethod.query.filter(DeliveryMethod.id == id).first()

    def add_delivery_method(self,
                            name,
                            description):
        try:
            delivery_method_rec = DeliveryMethod(name=name, description=description)
            self.db.session.add(delivery_method_rec)
            self.db.session.flush()
            return delivery_method_rec.id
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add delivery method. Details: %s' % (str(ex))
            DeliveryMethodRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_DELIVERY_METHOD_FAILED, message)

    def update_delivery_method(self,
                               delivery_method_id,
                               name,
                               description):
        delivery_method_rec = self.get_delivery_method(delivery_method_id)
        delivery_method_rec.name = name
        delivery_method_rec.description = description
