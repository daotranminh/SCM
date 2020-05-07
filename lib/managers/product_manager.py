import logging

from flask import url_for
from init import config
from dto.product_dto import ProductDto
from utilities.scm_logger import ScmLogger

class ProductManager:
    logger = ScmLogger(__name__)

    def __init__(self,
                 product_repo,
                 product_image_path_repo,
                 sample_image_path_repo,
                 cost_estimation_repo,
                 order_repo,
                 product_cost_estimation_repo):
        self.product_repo = product_repo
        self.product_image_path_repo = product_image_path_repo
        self.sample_image_path_repo = sample_image_path_repo
        self.cost_estimation_repo = cost_estimation_repo
        self.order_repo = order_repo
        self.product_cost_estimation_repo = product_cost_estimation_repo

    def get_latest_groups_3_image_paths(self,
                                        product_recs):
        latest_groups_3_image_paths = []
        for product_rec in product_recs:
            most_3_latest_product_image_paths = self.product_image_path_repo.get_latest_3_product_image_paths(product_rec.id)
            latest_groups_3_image_paths += most_3_latest_product_image_paths

        return latest_groups_3_image_paths
        
    def add_product(self,
                    name,
                    amount,
                    order_id,
                    formula_id,
                    decoration_form_id,
                    decoration_technique_id,
                    with_box):
        new_product_id = self.product_repo.add_product(name,
                                                      amount,
                                                      order_id,
                                                      formula_id,
                                                      decoration_form_id,
                                                      decoration_technique_id,
                                                      with_box)
        
        product_rec = self.product_repo.get_product(new_product_id)

        cost_estimation_infos = self.cost_estimation_repo.get_cost_estimations_of_formula(formula_id)

        total_product_cost = 0
        for cost_estimation_rec, count in cost_estimation_infos:
            self.product_cost_estimation_repo.add_product_cost_estimation(new_product_id, cost_estimation_rec.id)
            total_product_cost += (cost_estimation_rec.total_cost * count)
            
        product_rec.total_cost = total_product_cost
        product_rec.has_up_to_date_cost_estimation = True

        self.update_order_cost(order_id)

        return new_product_id

    def delete_product(self,
                       product_id):
        product_rec = self.product_repo.get_product(product_id)
        
        order_rec = self.order_repo.get_order(product_rec.order_id)
        
        order_cost = 0
        sibling_products = self.product_repo.get_products_of_order(product_rec.order_id)
        for sibling_product in sibling_products:
            if sibling_product.id != product_id and sibling_product.total_cost is not None:
                order_cost += sibling_product.total_cost * sibling_product.amount
        order_rec.total_cost = order_cost

        self.product_image_path_repo.delete_product_image_paths(product_id)
        self.product_repo.delete_product(product_id)

    def get_product_dto(self, product_id):
        product_rec, \
        decoration_form_id, \
        decoration_form_name, \
        decoration_technique_id, \
        decoration_technique_name, \
        formula_id, \
        formula_name, \
        formula_has_up_to_date_cost_estimation, \
        sample_images_group_id, \
        sample_images_group_name = self.product_repo.get_product_dto(product_id)

        sample_images_group_id = product_rec.sample_images_group_id
        latest_3_sample_image_paths = ['', '', '']
        if sample_images_group_id is not None:
            latest_3_sample_image_paths = self.sample_image_path_repo.get_latest_3_sample_image_paths(sample_images_group_id)

        latest_3_product_image_paths = self.product_image_path_repo.get_latest_3_product_image_paths(product_id)

        product_dto = ProductDto(product_id,
                                 product_rec.name,
                                 product_rec.amount,
                                 decoration_form_id,
                                 decoration_form_name,
                                 decoration_technique_id,
                                 decoration_technique_name,
                                 formula_id,
                                 formula_name,
                                 formula_has_up_to_date_cost_estimation,
                                 product_rec.price_to_customer,
                                 sample_images_group_id,
                                 sample_images_group_name, 
                                 product_rec.total_cost,
                                 latest_3_sample_image_paths,
                                 latest_3_product_image_paths)
        return product_dto

    def get_product_dtos(self, order_id):
        product_recs = self.product_repo.get_products_of_order(order_id)

        product_dtos = []
        for product_rec in product_recs:
            product_dto = self.get_product_dto(product_rec.id)
            product_dtos.append(product_dto)

        return product_dtos

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
            self.product_cost_estimation_repo.delete_cost_estimation_of_product(product_id)

            cost_estimation_infos = self.cost_estimation_repo.get_cost_estimations_of_formula(formula_id)

            total_product_cost = 0
            for cost_estimation_rec, count in cost_estimation_infos:
                self.product_cost_estimation_repo.add_product_cost_estimation(product_id, cost_estimation_rec.id)
                total_product_cost += (cost_estimation_rec.total_cost * count)
            
            product_rec.total_cost = total_product_cost
            product_rec.has_up_to_date_cost_estimation = True

            message = 'Formula of product %s changed to %s. New total cost = %s' % (product_id, formula_id, total_product_cost)
            ProductManager.logger.info(message)

            self.update_order_cost(product_rec.order_id)

        product_rec.name = product_name
        product_rec.decoration_form_id = decoration_form_id
        product_rec.decoration_technique_id = decoration_technique_id
        product_rec.formula_id = formula_id
        product_rec.box_status = box_status
        product_rec.box_returned_on = box_returned_on
        product_rec.sample_images_group_id = sample_images_group_id
        
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

        order_rec = self.order_repo.get_order(order_id)
        order_rec.total_cost = order_cost
        message = 'Cost of order %s updated to %s' % (order_rec.id, order_cost)
        ProductManager.logger.info(message)

    def update_prices_to_customer(self, product_prices_to_customer):
        for key, value in product_prices_to_customer.items():
            product_rec = self.product_repo.get_product(key)
            product_rec.price_to_customer = value