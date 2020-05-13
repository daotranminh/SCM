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
                 product_cost_estimation_repo,
                 formula_repo,
                 subformula_repo,
                 material_version_cost_estimation_repo,
                 material_repo,
                 fixed_formula_repo,
                 fixed_subformula_repo,
                 fixed_material_subformula_repo):
        self.product_repo = product_repo
        self.product_image_path_repo = product_image_path_repo
        self.sample_image_path_repo = sample_image_path_repo
        self.cost_estimation_repo = cost_estimation_repo
        self.order_repo = order_repo
        self.product_cost_estimation_repo = product_cost_estimation_repo
        self.formula_repo = formula_repo
        self.subformula_repo = subformula_repo
        self.material_version_cost_estimation_repo = material_version_cost_estimation_repo
        self.material_repo = material_repo
        self.fixed_formula_repo = fixed_formula_repo
        self.fixed_subformula_repo = fixed_subformula_repo
        self.fixed_material_subformula_repo = fixed_material_subformula_repo

    def get_latest_groups_3_image_paths(self,
                                        product_recs):
        latest_groups_3_image_paths = []
        for product_rec in product_recs:
            most_3_latest_product_image_paths = self.product_image_path_repo.get_latest_3_product_image_paths(product_rec.id)
            latest_groups_3_image_paths += most_3_latest_product_image_paths

        return latest_groups_3_image_paths

    def get_product_dto(self, product_id):
        product_rec, \
        decoration_form_id, \
        decoration_form_name, \
        decoration_technique_id, \
        decoration_technique_name, \
        plate_id, \
        plate_name, \
        box_id, \
        box_name, \
        formula_id, \
        formula_name, \
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
                                 plate_id,
                                 plate_name,
                                 box_id,
                                 box_name,
                                 formula_id,
                                 formula_name,                                 
                                 product_rec.price_to_customer,
                                 sample_images_group_id,
                                 sample_images_group_name, 
                                 product_rec.total_cost,
                                 product_rec.has_up_to_date_cost_estimation,
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

    def get_product_cost_estimation_details(self, product_id):
        fixed_formula_rec = self.fixed_formula_repo.get_fixed_formula_of_product(product_id)
        fixed_subformula_recs = self.fixed_subformula_repo.get_fixed_subformulas_of_fixed_formula(fixed_formula_rec.id)

        fixed_material_subformula_recs = []
        begin_fixed_material_subformula_recs = []
        end_fixed_material_subformula_recs = []

        for fixed_subformula_rec in fixed_subformula_recs:
            fixed_material_subformula_recs1 = self.fixed_material_subformula_repo.get_fixed_materials_of_fixed_subformula(fixed_subformula_rec.id)
            begin_fixed_material_subformula_recs.append(len(fixed_material_subformula_recs))
            fixed_material_subformula_recs += fixed_material_subformula_recs1
            end_fixed_material_subformula_recs.append(len(fixed_material_subformula_recs))

        return fixed_formula_rec, \
            fixed_subformula_recs, \
            fixed_material_subformula_recs, \
            begin_fixed_material_subformula_recs, \
            end_fixed_material_subformula_recs
        
    def delete_product(self, product_id):
        product_rec = self.product_repo.get_product(product_id)        
        order_rec = self.order_repo.get_order(product_rec.order_id)
        
        order_cost = 0
        sibling_products = self.product_repo.get_products_of_order(product_rec.order_id)
        for sibling_product in sibling_products:
            if sibling_product.id != product_id and sibling_product.total_cost is not None:
                order_cost += sibling_product.total_cost * sibling_product.amount

        self.order_repo.update_cost_order_rec(order_rec, order_cost)
        self.product_image_path_repo.delete_product_image_paths(product_id)
        self.product_cost_estimation_repo.delete_cost_estimation_of_product(product_id)
        self.product_repo.delete_product(product_id)

    def update_prices_to_customer(self, product_prices_to_customer):
        for key, value in product_prices_to_customer.items():
            product_rec = self.product_repo.get_product(key)
            self.product_repo.update_price_to_customer_product_rec(product_rec, value)

    def set_product_rec_fixed(self, product_rec):        
        self.product_repo.set_product_rec_fixed_flag(product_rec)
        message = 'Set product %s to fixed' % (product_rec.id)
        ProductManager.logger.info(message)

        formula_rec = self.formula_repo.get_formula(product_rec.formula_id)
        new_fixed_formula_id = self.fixed_formula_repo.add_fixed_formula(product_id=product_rec.id,
                                                                         original_formula_id=formula_rec.id,
                                                                         name=formula_rec.name,
                                                                         description=formula_rec.description,
                                                                         note=formula_rec.note,
                                                                         total_cost=formula_rec.total_cost)

        message = 'Add fixed_formula %s from formula %s' % (new_fixed_formula_id, formula_rec.id)
        ProductManager.logger.info(message)

        subformula_dtos = self.formula_repo.get_subformula_dtos_of_formula(formula_rec.id)
        for subformula_rec, taste_name, count in subformula_dtos:
            new_fixed_subformula_id = self.fixed_subformula_repo.add_fixed_subformula(fixed_formula_id=new_fixed_formula_id,
                                                                                      original_subformula_id=subformula_rec.id,
                                                                                      taste_id=subformula_rec.taste_id,
                                                                                      taste_name=taste_name,
                                                                                      subformula_type=subformula_rec.subformula_type,
                                                                                      name=subformula_rec.name,
                                                                                      description=subformula_rec.description,
                                                                                      note=subformula_rec.note,
                                                                                      total_cost=subformula_rec.total_cost,
                                                                                      count=count)
            message = 'Add fixed_subformula %s from subformula %s' % (new_fixed_subformula_id, subformula_rec.id)
            ProductManager.logger.info(message)

            current_cost_estimation_rec = \
                self.cost_estimation_repo.get_current_cost_estimation_of_subformula(subformula_rec.id)
            
            material_version_cost_estimation_recs = \
                self.material_version_cost_estimation_repo.get_material_version_cost_estimation_of_cost_estimation(current_cost_estimation_rec.id)

            for material_version_cost_estimation_rec, material_name in material_version_cost_estimation_recs:
                material_rec = self.material_repo.get_material(material_version_cost_estimation_rec.material_id)
                new_fixed_material_subformula_id = \
                    self.fixed_material_subformula_repo.add_fixed_material_subformula(fixed_subformula_id=new_fixed_subformula_id,
                                                                                      material_id=material_rec.id,
                                                                                      material_version_id=material_version_cost_estimation_rec.material_version_id,
                                                                                      name=material_name,
                                                                                      description=material_rec.description,
                                                                                      is_organic=material_rec.is_organic,
                                                                                      unit_amount=material_version_cost_estimation_rec.unit_amount,
                                                                                      unit=material_version_cost_estimation_rec.unit,
                                                                                      unit_price=material_version_cost_estimation_rec.unit_price,
                                                                                      amount=material_version_cost_estimation_rec.amount,
                                                                                      cost=material_version_cost_estimation_rec.cost)
                message = 'Add fixed_material_subformula %s from material %s (%s) and material_version %s' % (new_fixed_material_subformula_id,
                                                                                                              material_name,
                                                                                                              material_version_cost_estimation_rec.material_id,
                                                                                                              material_version_cost_estimation_rec.material_version_id)
                ProductManager.logger.info(message)