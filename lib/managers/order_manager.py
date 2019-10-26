import logging

from init import config
from dto.order_dto import OrderDto
from dto.paginated_scm import PaginatedScm

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class OrderManager:
    def __init__(self, order_repo):
        self.order_repo = order_repo

    def get_paginated_order_dtos(self,
                                 page,
                                 per_page,
                                 search_text):
        paginated_order_recs = self.order_repo.get_paginated_orders(page, per_page, search_text)
        order_dtos = []
        for order_rec, customer_name, taste, decoration, delivery_method in paginated_order_recs.items:
            order_dto = OrderDto(order_rec.id,
                                 order_rec.customer_id,
                                 customer_name,
                                 order_rec.taste_id,
                                 taste,
                                 order_rec.decoration_id,
                                 decoration,
                                 order_rec.delivery_method_id,
                                 delivery_method,
                                 order_rec.ordered_on,
                                 order_rec.delivered_on,
                                 order_rec.message,
                                 order_rec.order_status)
            order_dtos.append(order_dto)

        paginated_order_dtos = PaginatedScm(order_dtos,
                                            paginated_order_recs.has_prev,
                                            paginated_order_recs.has_next,
                                            paginated_order_recs.prev_num,
                                            paginated_order_recs.next_num,
                                            paginated_order_recs.page,
                                            paginated_order_recs.pages)
        return paginated_order_dtos
