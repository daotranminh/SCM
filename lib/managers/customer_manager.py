import logging

from init import config
from dto.customer_dto import CustomerDto
from dto.paginated_scm import PaginatedScm
from utilities.scm_logger import ScmLogger

class CustomerManager:
    logger = ScmLogger(__name__)

    def __init__(self, customer_repo):
        self.customer_repo = customer_repo

    def get_customer_details(self,
                             customer_id):
        customer_rec = self.customer_repo.get_customer(customer_id)
        recommendator = None
        if customer_rec.recommended_by != -1:
            recommendator_rec = self.customer_repo.get_customer(customer_rec.recommended_by)
            recommnedator = recommendator_rec.name
        
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
        return customer_dto
        
    def get_customer_choices1(self):
        customer_choices = self.get_customer_choices()
        customer_choices.insert(0, (-1, ''))
        return customer_choices

    def get_customer_choices(self):
        customer_recs = self.customer_repo.get_all_customers()

        customer_choices = []
        for customer_rec in customer_recs:
            customer_choices.append((customer_rec.id, customer_rec.name))

        return customer_choices

    def get_paginated_customer_dtos(self,
                                    page,
                                    per_page,
                                    search_text):
        customer_recs = self.customer_repo.get_all_customers()
        customers_dict = {}

        for customer_rec in customer_recs:
            customers_dict[customer_rec.id] = customer_rec

        paginated_customer_recs = self.customer_repo.get_paginated_customers(page,
                                                                             per_page,
                                                                             search_text)

        return self.__convert_to_paginated_customer_dtos(customers_dict,
                                                         paginated_customer_recs)

    def __convert_to_customer_dtos(self,
                                   customers_dict,
                                   customer_recs):
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
    
    def __convert_to_paginated_customer_dtos(self,
                                             customers_dict,
                                             paginated_customer_recs):
        customer_dtos = self.__convert_to_customer_dtos(customers_dict,
                                                        paginated_customer_recs.items)
        paginated_customer_dtos = PaginatedScm(customer_dtos,
                                               paginated_customer_recs.has_prev,
                                               paginated_customer_recs.has_next,
                                               paginated_customer_recs.prev_num,
                                               paginated_customer_recs.next_num,
                                               paginated_customer_recs.page,
                                               paginated_customer_recs.pages)
        return paginated_customer_dtos
    
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
