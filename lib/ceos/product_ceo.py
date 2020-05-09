import logging

from flask import url_for
from init import config
from dto.product_dto import ProductDto
from utilities.scm_logger import ScmLogger

class ProductCEO:
    logger = ScmLogger(__name__)

    def __init__(self,
                 product_repo,
                 formula_repo,
                 product_cost_estimation_repo,
                 product_image_path_repo,
                 formula_director):
        self.product_repo = product_repo
        self.formula_repo = formula_repo
        self.product_cost_estimation_repo = product_cost_estimation_repo
        self.product_image_path_repo = product_image_path_repo
        self.formula_director = formula_director

    def update_product(self,
                       product_id,
                       product_name,
                       decoration_form_id,
                       decoration_technique_id,
                       formula_id,
                       box_status,
                       box_returned_on,
                       sample_images_group_id,
                       product_image_path_recs,
                       remaining_product_image_path_ids,
                       uploaded_files):        
        product_rec = self.product_repo.get_product(product_id)
        if product_rec.formula_id != formula_id:
            formula_rec = self.formula_repo.get_formula(formula_id)
            if formula_rec.has_up_to_date_cost_estimation == True:
                self.product_repo.update_cost_product_rec(product_rec, formula_rec.total_cost)
            else:
                product_total_cost = self.formula_director.estimate_formula_cost(formula_id)
                self.product_repo.update_cost_product_rec(product_rec, product_total_cost)

                self.product_cost_estimation_repo.delete_cost_estimation_of_product(product_id)
                cost_estimation_infos = self.cost_estimation_repo.get_cost_estimations_of_formula(formula_id)
    
                for cost_estimation_rec, count in cost_estimation_infos:
                    self.product_cost_estimation_repo.add_product_cost_estimation(product_id, cost_estimation_rec.id)
        
            message = 'Formula of product %s changed to %s. New total cost = %s' % (product_id, formula_id, product_total_cost)
            ProductCEO.logger.info(message)

            self.update_order_cost(product_rec.order_id)

        self.product_repo.update_product(product_name,
                                         decoration_form_id,
                                         decoration_technique_id,
                                         formula_id,
                                         box_status,
                                         box_returned_on,
                                         sample_images_group_id)
        
        self.product_image_path_repo.update_product_image_paths(product_id,
                                                                product_image_path_recs,
                                                                remaining_product_image_path_ids,
                                                                uploaded_files)

    def update_order_cost(self, order_id):
        sibling_products = self.product_repo.get_products_of_order(order_id)

        order_cost = 0
        for sibling_product in sibling_products:
            if sibling_product.total_cost is not None:
                order_cost += sibling_product.total_cost * sibling_product.amount

        self.order_repo.update_cost(order_id, order_cost)
        message = 'Cost of order %s updated to %s' % (order_id, order_cost)
        ProductCEO.logger.info(message)