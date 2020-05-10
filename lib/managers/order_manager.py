import logging

from init import config
from dto.order_dto import OrderDto
from dto.paginated_scm import PaginatedScm
from utilities import scm_constants
from utilities.scm_exceptions import ScmException
from utilities.scm_enums import ErrorCodes, OrderStatus
from utilities.scm_logger import ScmLogger

class OrderManager:
    logger = ScmLogger(__name__)

    def __init__(self, 
                order_repo,
                product_repo):
        self.order_repo = order_repo
        self.product_repo = product_repo

    def get_order_dto(self, order_id):
        order_rec, \
        customer_name, \
        delivery_method_name = self.order_repo.get_order_dto(order_id)
        
        order_status_name = self.__get_order_status_name(order_rec.order_status)
        payment_status_name = self.__get_payment_status_name(order_rec.payment_status)

        order_dto = OrderDto(order_id,
                             order_rec.customer_id,
                             customer_name,
                             order_rec.ordered_on,
                             order_rec.delivery_appointment,
                             delivery_method_name,
                             order_rec.message,
                             order_status_name,
                             order_rec.delivered_on,
                             payment_status_name,
                             order_rec.paid_on,
                             order_rec.total_cost,
                             order_rec.has_up_to_date_cost_estimation,
                             order_rec.price_to_customer)

        return order_dto

    def get_paginated_order_dtos(self,
                                 page,
                                 per_page,
                                 search_text):
        paginated_order_dtos = self.order_repo.get_paginated_order_dtos(page, per_page, search_text)
        order_dtos = []
        for order_rec, customer_name, delivery_method_name in paginated_order_dtos.items:
            order_status_name = self.__get_order_status_name(order_rec.order_status)
            payment_status_name = self.__get_payment_status_name(order_rec.payment_status)

            order_dto = OrderDto(order_rec.id,
                                 order_rec.customer_id,
                                 customer_name,
                                 order_rec.ordered_on,
                                 order_rec.delivery_appointment,
                                 delivery_method_name,
                                 order_rec.message,
                                 order_status_name,
                                 order_rec.delivered_on,
                                 payment_status_name,
                                 order_rec.paid_on,
                                 order_rec.total_cost,
                                 order_rec.has_up_to_date_cost_estimation,
                                 order_rec.price_to_customer)
            order_dtos.append(order_dto)

        paginated_order_dtos1 = PaginatedScm(order_dtos,
                                            paginated_order_dtos.has_prev,
                                            paginated_order_dtos.has_next,
                                            paginated_order_dtos.prev_num,
                                            paginated_order_dtos.next_num,
                                            paginated_order_dtos.page,
                                            paginated_order_dtos.pages)
        return paginated_order_dtos1

    def __get_order_status_name(self, order_status):
        for order_status_name in scm_constants.ORDER_STATUS_NAMES:
            if order_status_name[0] == order_status:
                return order_status_name[1]

        message = 'Order status key %s does not exist' % (str(order_status))
        OrderManager.logger.error(message)
        raise ScmException(ErrorCodes.ERROR_ORDER_STATUS_KEY_NOT_EXIST, message)

    def __get_payment_status_name(self, payment_status):
        for payment_status_name in scm_constants.PAYMENT_STATUS_NAMES:
            if payment_status_name[0] == payment_status:
                return payment_status_name[1]

        message = 'Payment status key %s does not exist' % (str(payment_status))
        OrderManager.logger.error(message)
        raise ScmException(ErrorCodes.ERROR_PAYMENT_STATUS_KEY_NOT_EXIST, message)