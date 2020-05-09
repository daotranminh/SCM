import logging

from init import config
from dto.paginated_scm import PaginatedScm
from utilities.scm_logger import ScmLogger

class OrderChairman:
    logger = ScmLogger(__name__)

    def __init__(self,
                 order_repo,
                 product_repo,
                 product_ceo):
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.product_ceo = product_ceo

    def add_order(self,
                  customer_id,
                  ordered_on,
                  delivery_appointment,
                  delivery_method_id,
                  message,
                  product_names,
                  product_amounts,
                  formula_ids,
                  decoration_form_ids,
                  decoration_technique_ids,
                  with_boxes):
        new_order_id = self.order_repo.add_order(customer_id,
                                                delivery_method_id,
                                                ordered_on,
                                                delivery_appointment,
                                                message)

        order_cost = 0                                                
        for i in range(len(product_names)):
            new_product_id = self.product_ceo.add_product(product_names[i],
                                                          product_amounts[i],
                                                          new_order_id,
                                                          formula_ids[i],
                                                          decoration_form_ids[i],
                                                          decoration_technique_ids[i],
                                                          with_boxes[i])
            product_rec = self.product_repo.get_product(new_product_id)
            order_cost += product_rec.total_cost
        
        self.order_repo.update_cost(new_order_id, order_cost)
        
        return new_order_id

    def estimate_order_cost(self, order_id):
        order_rec = self.order_repo.get_order(order_id)        
        if order_rec.has_up_to_date_cost_estimation == True:
            return order_rec.total_cost

        product_recs = self.product_repo.get_products_of_order(order_id)
        new_order_cost = 0
        for product_rec in product_recs:
            product_cost = self.product_ceo.estimate_product_cost(product_rec.id)
            new_order_cost += product_cost * product_rec.amount

        self.order_repo.update_cost(order_rec.id, new_order_cost)

        return new_order_cost
