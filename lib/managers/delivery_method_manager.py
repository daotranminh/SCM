import logging

from init import config

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class DeliveryMethodManager:
    def __init__(self, delivery_method_repo):
        self.delivery_method_repo = delivery_method_repo

    def get_delivery_method_choices(self):
        delivery_method_recs = self.delivery_method_repo.get_all_delivery_methods()

        delivery_method_choices = []
        for delivery_method_rec in delivery_method_recs:
            delivery_method_choices.append((delivery_method_rec.id, delivery_method_rec.name))

        return delivery_method_choices
