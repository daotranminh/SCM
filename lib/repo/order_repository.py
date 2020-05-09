import logging

from flask_sqlalchemy import sqlalchemy

from init import Order, Customer, DeliveryMethod, config
from utilities.scm_enums import ErrorCodes, PaymentStatus
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class OrderRepository:
    logger = ScmLogger(__name__)

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

        order_dto_query = self.db.session.query(Order, \
                                                customer_query.c.name, \
                                                delivery_method_query.c.name). \
            join(customer_query, Order.customer_id == customer_query.c.id). \
            join(delivery_method_query, Order.delivery_method_id == delivery_method_query.c.id)

        paginated_order_dtos = order_dto_query.paginate(page, per_page, error_out=False)

        return paginated_order_dtos
    
    def get_order(self, order_id):
        return Order.query.filter(Order.id == order_id).first()

    def get_order_dto(self, order_id):
        customer_query = self.db.session.query(Customer.id, Customer.name).subquery()
        delivery_method_query = self.db.session.query(DeliveryMethod.id, DeliveryMethod.name).subquery()

        order_dto_query = self.db.session.query(Order, \
                                                customer_query.c.name, \
                                                delivery_method_query.c.name). \
            filter(Order.id == order_id). \
            join(customer_query, Order.customer_id == customer_query.c.id). \
            join(delivery_method_query, Order.delivery_method_id == delivery_method_query.c.id)
        
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
                              message=message,
                              order_status=0)
            self.db.session.add(order_rec)
            self.db.session.flush()
            return order_rec.id
        except sqlalchemy.exc.SQLAlchemyError as e:
            message = 'Error: failed to add order. Details: %s' % (str(e))
            OrderRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_ORDER_FAILED, message)

    def update_order(self,
                     order_id,
                     customer_id,
                     delivery_appointment,
                     delivery_method_id,
                     ordered_on,
                     order_status,
                     delivered_on,
                     payment_status,
                     paid_on,
                     message,
                     price_to_customer):
        order_rec = self.get_order(order_id)
        order_rec.customer_id = customer_id
        order_rec.delivery_appointment = delivery_appointment
        order_rec.delivery_method_id = delivery_method_id
        order_rec.ordered_on = ordered_on
        order_rec.order_status = order_status
        order_rec.delivered_on = delivered_on
        order_rec.payment_status = payment_status
        order_rec.paid_on = paid_on  
        order_rec.message = message
        order_rec.price_to_customer = price_to_customer

        if payment_status == int(PaymentStatus.FULLY_PAID):
            order_rec.is_fixed = True

        self.db.session.flush()