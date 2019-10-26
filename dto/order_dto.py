import logging

from init import config

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class OrderDto:
    def __init__(self,
                 order_id,
                 customer_id,
                 customer_name,
                 taste_id,
                 taste,
                 decoration_id,
                 decoration,
                 delivery_method_id,
                 delivery_method,
                 ordered_on,
                 delivered_on,
                 message,
                 order_status):
        self.order_id = order_id
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.taste_id = taste_id
        self.taste = taste
        self.decoration_id = decoration_id
        self.decoration = decoration
        self.delivery_method_id = delivery_method_id
        self.delivery_method = delivery_method
        self.ordered_on = ordered_on
        self.delivered_on = delivered_on
        self.message = message
        self.order_status = order_status
        
