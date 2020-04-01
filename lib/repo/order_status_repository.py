import logging

from flask_sqlalchemy import sqlalchemy

from init import OrderStatus, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class OrderStatusRepository:
    def __init__(self, db):
        self.db = db

    def get_all_order_status(self):
        return OrderStatus.query.all()

    def get_order_status(self, id):
        return OrderStatus.query.filter(OrderStatus.id == id).first()

    def add_order_status(self,
                         name,
                         description):
        try:
            order_status_rec = OrderStatus(name=name, description=description)
            self.db.session.add(order_status_rec)
            self.db.session.flush()
            return order_status_rec.id
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add order_status. Details: %s' % (str(ex))
            logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_ORDER_STATUS_FAILED, message)

    def update_order_status(self,
                            order_status_id,
                            name,
                            description):
        order_status_rec = self.get_order_status(order_status_id)
        order_status_rec.name = name
        order_status_rec.description = description