import logging

from init import config

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class CustomerManager:
    def __init__(self, customer_repo):
        self.customer_repo = customer_repo

    def get_customer_choices(self):
        customer_recs = self.customer_repo.get_all_customers()

        customer_choices = [(-1, '')]
        for customer_rec in customer_recs:
            customer_choices.append((customer_rec.id, customer_rec.name))

        return customer_choices
        
