import logging

from init import config
from dto.paginated_scm import PaginatedScm
from utilities.scm_logger import ScmLogger
from utilities.scm_enums import ErrorCodes, OrderStatus

class OrderChairman:
    logger = ScmLogger(__name__)

    def __init__(self,
                 order_repo,                 
                 product_repo,
                 product_manager,
                 product_ceo):
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.product_manager = product_manager
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
                  formula_amounts,
                  decoration_form_ids,
                  decoration_technique_ids,
                  plate_ids,
                  box_ids,
                  boxes_to_be_returned):
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
                                                          formula_amounts[i],
                                                          decoration_form_ids[i],
                                                          decoration_technique_ids[i],
                                                          plate_ids[i],
                                                          box_ids[i],
                                                          boxes_to_be_returned[i])
            product_rec = self.product_repo.get_product(new_product_id)
            order_cost += product_rec.total_cost * product_rec.amount
        
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

    def update_order(self,
                     order_id,
                     customer_id,
                     delivery_appointment,
                     delivery_method_id,
                     ordered_on,
                     order_status,
                     delivered_on,
                     payment_status,
                     paid_on,
                     message,
                     price_to_customer,
                     paid_by_customer):
        self.order_repo.update_order(order_id,
                                     customer_id,
                                     delivery_appointment,
                                     delivery_method_id,
                                     ordered_on,
                                     order_status,
                                     delivered_on,
                                     payment_status,
                                     paid_on,
                                     message,
                                     price_to_customer,
                                     paid_by_customer)
        if order_status == int(OrderStatus.DELIVERED):
            product_recs = self.product_repo.get_products_of_order(order_id)
            for product_rec in product_recs:
                self.product_manager.set_product_rec_fixed(product_rec)
