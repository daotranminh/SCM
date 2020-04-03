import logging

from init import config
from dto.order_dto import OrderDto
from dto.paginated_scm import PaginatedScm
from utilities import scm_constants

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class OrderManager:
    def __init__(self, 
                order_repo,
                product_repo):
        self.order_repo = order_repo
        self.product_repo = product_repo

    def add_order(self,
                  customer_id,
                  ordered_on,
                  delivery_appointment,
                  delivery_method_id,
                  message,
                  product_names,
                  taste_ids,
                  decoration_form_ids,
                  decoration_technique_ids,
                  with_boxes):
        new_order_id = self.order_repo.add_order(customer_id,
                                                delivery_method_id,
                                                ordered_on,
                                                delivery_appointment,
                                                message)
        for i in range(len(product_names)):
            self.product_repo.add_product(product_names[i],
                                          new_order_id,
                                          taste_ids[i],
                                          decoration_form_ids[i],
                                          decoration_technique_ids[i],
                                          with_boxes[i])
        
        return new_order_id

    def get_order_dto(self, order_id):
        order_rec, \
        customer_name, \
        delivery_method_name = self.order_repo.get_order_dto(order_id)
        
        order_dto = OrderDto(order_id,
                             order_rec.customer_id,
                             customer_name,
                             order_rec.ordered_on,
                             order_rec.delivery_appointment,
                             delivery_method_name,
                             order_rec.message,
                             scm_constants.ORDER_STATUS_NAMES[order_rec.order_status],
                             order_rec.delivered_on,
                             order_rec.payment_status,
                             order_rec.paid_on)

        return order_dto

    def get_paginated_order_dtos(self,
                                 page,
                                 per_page,
                                 search_text):
        paginated_order_dtos = self.order_repo.get_paginated_order_dtos(page, per_page, search_text)
        order_dtos = []
        for order_rec, customer_name, delivery_method_name, order_status_name in paginated_order_dtos.items:
            order_dto = OrderDto(order_rec.id,
                                 order_rec.customer_id,
                                 customer_name,
                                 order_rec.ordered_on,
                                 order_rec.delivery_appointment,
                                 delivery_method_name,
                                 order_rec.message,
                                 scm_constants.ORDER_STATUS_NAMES[order_rec.order_status],
                                 order_rec.delivered_on,
                                 order_rec.payment_status,
                                 order_rec.paid_on)
            order_dtos.append(order_dto)

        paginated_order_dtos1 = PaginatedScm(order_dtos,
                                            paginated_order_dtos.has_prev,
                                            paginated_order_dtos.has_next,
                                            paginated_order_dtos.prev_num,
                                            paginated_order_dtos.next_num,
                                            paginated_order_dtos.page,
                                            paginated_order_dtos.pages)
        return paginated_order_dtos1
