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
                 delivery_appointment,
                 delivery_method_name,
                 message,
                 order_status_name,
                 delivered_on,
                 payment_status_name,
                 paid_on,
                 total_cost,
                 price_to_customer):
        self.order_id = order_id
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.ordered_on = ordered_on
        self.delivery_appointment = delivery_appointment
        self.delivery_method_name = delivery_method_name
        self.message = message
        self.order_status_name = order_status_name
        self.delivered_on = delivered_on
        self.payment_status_name = payment_status_name
        self.paid_on = paid_on
        self.total_cost = total_cost
        self.price_to_customer = price_to_customer
