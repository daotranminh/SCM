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
                 cost_estimation_repo,
                 order_repo,
                 plate_repo,
                 box_repo,
                 formula_director):
        self.product_repo = product_repo
        self.formula_repo = formula_repo
        self.product_cost_estimation_repo = product_cost_estimation_repo
        self.product_image_path_repo = product_image_path_repo
        self.cost_estimation_repo = cost_estimation_repo
        self.order_repo = order_repo
        self.plate_repo = plate_repo
        self.box_repo = box_repo
        self.formula_director = formula_director

    def add_product(self,
                    name,
                    amount,
                    order_id,
                    formula_id,
                    formula_amount,
                    decoration_form_id,
                    decoration_technique_id,
                    plate_id,
                    plate_count,
                    box_id,
                    box_count,
                    box_to_be_returned):
        new_product_id = self.product_repo.add_product(name,
                                                      amount,
                                                      order_id,
                                                      formula_id,
                                                      formula_amount,
                                                      decoration_form_id,
                                                      decoration_technique_id,
                                                      plate_id,
                                                      plate_count,
                                                      box_id,
                                                      box_count,
                                                      box_to_be_returned)
        
        product_rec = self.product_repo.get_product(new_product_id)

        cost_estimation_infos = self.cost_estimation_repo.get_cost_estimations_of_formula(formula_id)

        total_product_cost = 0
        for cost_estimation_rec, count in cost_estimation_infos:
            self.product_cost_estimation_repo.add_product_cost_estimation(new_product_id, cost_estimation_rec.id)
            total_product_cost += (cost_estimation_rec.total_cost * count)

        total_product_cost *= formula_amount

        if plate_id != -1:
            plate_rec = self.plate_repo.get_plate(plate_id)
            total_product_cost += plate_count * plate_rec.unit_price / plate_rec.unit_count

        if box_id != -1:
            box_rec = self.box_repo.get_box(box_id)
            total_product_cost += box_count * box_rec.unit_price / box_rec.unit_count
            
        self.product_repo.update_cost_product_rec(product_rec, total_product_cost)
        self.order_repo.set_flag_has_up_to_date_cost_estimation(order_id, False)

        return new_product_id

    def update_product(self,
                       product_id,
                       product_name,
                       product_amount,
                       decoration_form_id,
                       decoration_technique_id,
                       plate_id,
                       box_id,
                       formula_id,
                       box_status,
                       box_returned_on,
                       sample_images_group_id,
                       product_image_path_recs,
                       remaining_product_image_path_ids,
                       uploaded_files):        
        product_rec = self.product_repo.get_product(product_id)

        if product_rec.formula_id != formula_id or \
            product_rec.plate_id != plate_id or \
            product_rec.box_id != box_id:
        
            formula_cost = 0
            if product_rec.formula_id != formula_id:
                formula_rec = self.formula_repo.get_formula(formula_id)
                if formula_rec.has_up_to_date_cost_estimation == True:
                    formula_cost = formula_rec.total_cost
                else:
                    formula_cost = self.formula_director.estimate_formula_cost(formula_id)

                    self.product_cost_estimation_repo.delete_cost_estimation_of_product(product_id)

                    cost_estimation_infos = self.cost_estimation_repo.get_cost_estimations_of_formula(formula_id)
                    for cost_estimation_rec, count in cost_estimation_infos:
                        self.product_cost_estimation_repo.add_product_cost_estimation(product_id, cost_estimation_rec.id)

                    message = 'Formula of product %s changed to %s. New formula cost = %s' % (product_id, formula_id, formula_cost)
                    ProductCEO.logger.info(message)
            else:
                formula_rec = self.formula_repo.get_formula(formula_id)
                if formula_rec.has_up_to_date_cost_estimation == True:
                    formula_cost = formula_rec.total_cost
                else:
                    formula_cost = self.formula_director.estimate_formula_cost(formula_id)

            plate_rec = None
            if product_rec.plate_id != plate_id:
                plate_rec = self.plate_repo.get_plate(plate_id)
                message = 'Plate of product %s changed to %s. New plate cost = %s' % (product_id, plate_id, plate_rec.unit_price / plate_rec.unit_count)
                ProductCEO.logger.info(message)
            else:
                plate_rec = self.plate_repo.get_plate(product_rec.plate_id)
            plate_cost = plate_rec.unit_price / plate_rec.unit_count

            box_rec = None
            if product_rec.box_id != box_id:
                box_rec = self.box_repo.get_box(box_id)
                message = 'Box of product %s changed to %s. New box cost = %s' % (product_id, box_id, box_rec.unit_price / box_rec.unit_count)
                ProductCEO.logger.info(message)
            else:
                box_rec = self.box_repo.get_box(product_rec.box_id)
            box_cost = box_rec.unit_price / box_rec.unit_count

            self.product_repo.update_cost_product_rec(product_rec, formula_cost + plate_cost + box_cost)
        
            message = 'New cost of product %s is %s' % (product_id, formula_cost + plate_cost + box_cost)
            ProductCEO.logger.info(message)

            self.order_repo.set_flag_has_up_to_date_cost_estimation(product_rec.order_id, False)

        if product_rec.amount != product_amount:
            message = 'Amount of product %s changed to %s' % (product_id, product_amount)
            ProductCEO.logger.info(message)
            self.order_repo.set_flag_has_up_to_date_cost_estimation(product_rec.order_id, False)

        self.product_repo.update_product_rec(product_rec,
                                             product_name,
                                             product_amount,
                                             decoration_form_id,
                                             decoration_technique_id,
                                             plate_id,
                                             box_id,
                                             formula_id,
                                             box_status,
                                             box_returned_on,
                                             sample_images_group_id)
        
        self.product_image_path_repo.update_product_image_paths(product_id,
                                                                product_image_path_recs,
                                                                remaining_product_image_path_ids,
                                                                uploaded_files)

    def estimate_product_cost(self, product_id):
        product_rec = self.product_repo.get_product(product_id)
        if product_rec.has_up_to_date_cost_estimation or product_rec.is_fixed:
            return product_rec.total_cost
        
        new_formula_cost = self.formula_director.estimate_formula_cost(product_rec.formula_id)
        message = 'Estimate cost of formula %s. Got %s' % (product_rec.formula_id, new_formula_cost)
        ProductCEO.logger.info(message)

        plate_rec = self.plate_repo.get_plate(product_rec.plate_id)
        box_rec = self.box_repo.get_box(product_rec.box_id)

        new_product_cost = new_formula_cost * product_rec.formula_amount + \
            (plate_rec.unit_price / plate_rec.unit_count) * product_rec.plate_count + \
            (box_rec.unit_price / box_rec.unit_count) * product_rec.box_count

        message = 'New cost of product %s is %s' % (product_id, new_product_cost)
        ProductCEO.logger.info(message)        

        self.product_repo.update_cost_product_rec(product_rec, new_product_cost)
        self.order_repo.set_flag_has_up_to_date_cost_estimation(product_rec.order_id, False)

        return new_product_cost