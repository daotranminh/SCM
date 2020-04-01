import logging

from flask_sqlalchemy import sqlalchemy

from init import Order, Customer, DeliveryMethod, OrderStatus, config
from utilities.scm_enums import ErrorCodes, DeliveryStatus, PaymentStatus
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

    def get_paginated_order_dtos(self,
                                page,
                                per_page,
                                search_text):

        customer_query = self.db.session.query(Customer.id, Customer.name).subquery()
        delivery_method_query = self.db.session.query(DeliveryMethod.id, DeliveryMethod.name).subquery()
        order_status_query = self.db.session.query(OrderStatus.id, OrderStatus.name).subquery()

        order_dto_query = self.db.session.query(Order, \
                                                customer_query.c.name, \
                                                delivery_method_query.c.name, \
                                                order_status_query.c.name). \
            join(customer_query, Order.customer_id == customer_query.c.id). \
            join(delivery_method_query, Order.delivery_method_id == delivery_method_query.c.id). \
            join(order_status_query, Order.order_status_id == order_status_query.c.id)

        paginated_order_dtos = order_dto_query.paginate(page, per_page, error_out=False)

        return paginated_order_dtos
    
    def get_order(self, order_id):
        return Order.query.filter(Order.id == order_id).first()

    def get_order_dto(self, order_id):
        customer_query = self.db.session.query(Customer.id, Customer.name).subquery()
        delivery_method_query = self.db.session.query(DeliveryMethod.id, DeliveryMethod.name).subquery()
        order_status_query = self.db.session.query(OrderStatus.id, OrderStatus.name).subquery()

        order_dto_query = self.db.session.query(Order, \
                                                customer_query.c.name, \
                                                delivery_method_query.c.name, \
                                                order_status_query.c.name). \
            filter(Order.id == order_id). \
            join(customer_query, Order.customer_id == customer_query.c.id). \
            join(delivery_method_query, Order.delivery_method_id == delivery_method_query.c.id). \
            join(order_status_query, Order.order_status_id == order_status_query.c.id)
        
        return order_dto_query.first()

    def add_order(self,
                  customer_id,
                  delivery_method_id,
                  ordered_on,
                  delivery_appointment,
                  message):
        try:            
            order_rec = Order(customer_id=customer_id,
                              delivery_method_id=delivery_method_id,
                              ordered_on=ordered_on,
                              delivery_appointment=delivery_appointment,
                              message=message)
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
                     decoration_id,
                     delivery_method_id,
                     ordered_on,
                     delivery_appointment,
                     message):
        order_rec = self.get_order(order_id)
        order_rec.customer_id = customer_id
        order_rec.decoration_id = decoration_id
        order_rec.delivery_method_id = delivery_method_id
        order_rec.ordered_on = ordered_on
        order_rec.delivery_appointment = delivery_appointment
        order_rec.message = message
