import logging

from flask_sqlalchemy import sqlalchemy

from init import Order, Customer, Taste, Decoration, DeliveryMethod, config
from utilities.scm_enums import ErrorCodes, DeliveryStatus, PaymentStatus, BoxStatus
from utilities.scm_exceptions import ScmException

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class OrderRepository:
    def __init__(self, db):
        self.db = db

    def get_all_orders(self):
        return Order.query.all()

    def get_paginated_orders(self,
                                page,
                                per_page,
                                search_text):
        sub_query_customer = self.db.session.query(Customer.id, Customer.name).subquery()

        order_recs = self.db.session. \
                     query(Order, sub_query_customer.c.name). \
                     join(sub_query_customer, Order.customer_id == sub_query_customer.c.id)

        paginated_order_recs = order_recs.paginate(page, per_page, error_out=False)

        print(paginated_order_recs.items)
        return paginated_order_recs
    
    def get_order(self, order_id):
        return Order.query.filter(Order.id == order_id).first()

    def add_order(self,
                  customer_id,
                  taste_id,
                  decoration_id,
                  delivery_method_id,
                  ordered_on,
                  delivery_appointment,
                  message,
                  with_box):
        try:
            box_status = int(BoxStatus.BOX_NOT_NEEDED)
            if with_box:
                box_status = int(BoxStatus.BOX_WITH_CAKE_IN_PRODUCTION)
                
            order_rec = Order(customer_id=customer_id,
                              taste_id=taste_id,
                              decoration_id=decoration_id,
                              delivery_method_id=delivery_method_id,
                              ordered_on=ordered_on,
                              delivery_appointment=delivery_appointment,
                              message=message,
                              box_status=box_status)
            self.db.session.add(order_rec)
            self.db.session.flush()
            return order_rec.id
        except sqlalchemy.exc.SQLAlchemyError as e:
            message = 'Error: failed to add order. Details: %s' % (str(e))
            logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_ORDER_FAILED, message)

    def update_order(self,
                     order_id,
                     customer_id,
                     taste_id,
                     decoration_id,
                     delivery_method_id,
                     ordered_on,
                     delivery_appointment,
                     message):
        order_rec = self.get_order(order_id)
        order_rec.customer_id = customer_id
        order_rec.taste_id = taste_id
        order_rec.decoration_id = decoration_id
        order_rec.delivery_method_id = delivery_method_id
        order_rec.ordered_on = ordered_on
        order_rec.delivery_appointment = delivery_appointment
        order_rec.message = message
