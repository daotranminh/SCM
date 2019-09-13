import logging

from init import config
from dto.customer_dto import CustomerDto

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

    def get_customer_dtos(self):
        customer_recs = self.customer_repo.get_all_customers()
        customers_dict = {}

        for customer_rec in customer_recs:
            customers_dict[customer_rec.id] = customer_rec

        customer_dtos = []
        for customer_rec in customer_recs:
            recommendator = ''
            if customer_rec.recommended_by != -1:
                recommendator = customers_dict[customer_rec.recommended_by].name
            customer_dto = CustomerDto(customer_rec.id,
                                       customer_rec.name,
                                       customer_rec.birthday,
                                       customer_rec.address,
                                       customer_rec.phone,
                                       customer_rec.email_address,
                                       customer_rec.facebook,
                                       customer_rec.recommended_by,
                                       recommendator,
                                       customer_rec.registered_on)
            customer_dtos.append(customer_dto)
        return customer_dtos
