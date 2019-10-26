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
                 ordered_on,
                 delivered_on,
                 message,
                 order_status):
        self.order_id = order_id
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.ordered_on = ordered_on
        self.delivered_on = delivered_on
        self.message = message
        self.order_status = order_status
        
