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
        return DeliveryMethod.query. \
            order_by(DeliveryMethod.name). \
            all()

    def get_paginated_delivery_methods(self,
                                       page,
                                       per_page,
                                       search_text):
        delivery_method_recs = DeliveryMethod.query
        if search_text is not None and search_text != '':
            search_pattern = '%' + search_text + '%'
            delivery_method_recs = delivery_method_recs.filter(DeliveryMethod.name.ilike(search_pattern))

        delivery_method_recs = delivery_method_recs.order_by(DeliveryMethod.name)
        return delivery_method_recs.paginate(page, per_page, error_out=False)

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
        self.db.session.flush()
