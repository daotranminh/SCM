import logging

from flask_sqlalchemy import sqlalchemy
from sqlalchemy import desc

from init import Order, Customer, DeliveryMethod, config
from utilities.scm_enums import ErrorCodes, PaymentStatus
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class OrderRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_all_orders(self):
        return Order.query. \
            order_by(desc(Order.id)). \
            all()

    def get_paginated_order_dtos(self,
                                page,
                                per_page,
                                search_text,
                                sorting_criteria):

        customer_query = self.db.session.query(Customer.id, Customer.name).subquery()
        delivery_method_query = self.db.session.query(DeliveryMethod.id, DeliveryMethod.name).subquery()

        order_dto_query = self.db.session.query(Order, \
                                                customer_query.c.name, \
                                                delivery_method_query.c.name). \
            join(customer_query, Order.customer_id == customer_query.c.id). \
            join(delivery_method_query, Order.delivery_method_id == delivery_method_query.c.id)

        if search_text is not None and search_text != '':
            search_pattern = '%' + search_text + '%'
            order_dto_query = order_dto_query.filter(customer_query.c.name.ilike(search_pattern))

        if sorting_criteria == 'customer_name_asc':
            order_dto_query = order_dto_query.order_by(customer_query.c.name)
        elif sorting_criteria == 'customer_name_desc':
            order_dto_query = order_dto_query.order_by(desc(customer_query.c.name))
        elif sorting_criteria == 'delivery_appointment_asc':
            order_dto_query = order_dto_query.order_by(Order.delivery_appointment)
        elif sorting_criteria == 'delivery_appointment_desc':
            order_dto_query = order_dto_query.order_by(desc(Order.delivery_appointment))
        elif sorting_criteria == 'cost_estimation_asc':
            order_dto_query = order_dto_query.order_by(Order.total_cost)
        elif sorting_criteria == 'cost_estimation_desc':
            order_dto_query = order_dto_query.order_by(desc(Order.total_cost))
        elif sorting_criteria == 'price_to_customer_asc':
            order_dto_query = order_dto_query.order_by(Order.price_to_customer)
        elif sorting_criteria == 'price_to_customer_desc':
            order_dto_query = order_dto_query.order_by(desc(Order.price_to_customer))
        else:
            order_dto_query = order_dto_query.order_by(desc(Order.delivery_appointment))

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
                     price_to_customer,
                     paid_by_customer):
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
        order_rec.paid_by_customer = paid_by_customer

        if payment_status == int(PaymentStatus.FULLY_PAID):
            order_rec.is_fixed = True

        self.db.session.flush()

    def update_cost(self, order_id, new_total_cost):
        order_rec = self.get_order(order_id)
        self.update_cost_order_rec(order_rec, new_total_cost)

    def update_cost_order_rec(self, order_rec, new_total_cost):
        order_rec.total_cost = new_total_cost
        order_rec.has_up_to_date_cost_estimation = True
        self.db.session.flush()

        message = 'Update cost of order %s to %s' % (order_rec.id, new_total_cost)
        OrderRepository.logger.info(message)

    def set_flag_has_up_to_date_cost_estimation(self, order_id, flag):
        order_rec = self.get_order(order_id)
        self.set_flag_has_up_to_date_cost_estimation_order_rec(order_rec, flag)

    def set_flag_has_up_to_date_cost_estimation_order_rec(self, order_rec, flag):
        order_rec.has_up_to_date_cost_estimation = flag
        self.db.session.flush()

        message = 'Set flag of order %s to %s' % (order_rec.id, flag)
        OrderRepository.logger.info(message)