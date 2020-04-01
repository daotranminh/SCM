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
                 order_status,
                 delivered_on,
                 payment_status,
                 paid_on):
        self.order_id = order_id
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.ordered_on = ordered_on
        self.delivery_appointment = delivery_appointment
        self.delivery_method_name = delivery_method_name
        self.message = message
        self.order_status = order_status
        self.delivered_on = delivered_on
        self.payment_status = payment_status
        self.paid_on = paid_on
