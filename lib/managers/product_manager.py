import logging

from flask import url_for
from init import config
from dto.product_dto import ProductDto

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class ProductManager:
    def __init__(self,
                 product_repo,
                 product_image_path_repo,
                 sample_image_path_repo):
        self.product_repo = product_repo
        self.product_image_path_repo = product_image_path_repo
        self.sample_image_path_repo = sample_image_path_repo

    def get_latest_groups_3_image_paths(self,
                                        product_recs):
        latest_groups_3_image_paths = []
        for product_rec in product_recs:
            most_3_latest_product_image_paths = self.product_image_path_repo.get_latest_3_product_image_paths(product_rec.id)
            latest_groups_3_image_paths += most_3_latest_product_image_paths

        return latest_groups_3_image_paths
        
    def add_product(self,
                    name,
                    order_id,
                    taste_id,
                    decoration_form_id,
                    decoration_technique_id,
                    uploaded_files):
        new_product_id = self.product_repo.add_product(name,
                                                      order_id,
                                                      taste_id,
                                                      decoration_form_id,
                                                      decoration_technique_id)
        self.product_image_path_repo.add_product_image_paths(new_product_id,
                                                            uploaded_files)
        
    def delete_product(self,
                       product_id):
        self.product_image_path_repo.delete_product_image_paths(product_id)
        self.product_repo.delete_product(product_id)

    def get_product_dto(self, product_id):
        product_rec, \
        taste_id, \
        taste_name, \
        decoration_form_id, \
        decoration_form_name, \
        decoration_technique_id, \
        decoration_technique_name, \
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
                                 taste_id,
                                 taste_name,
                                 decoration_form_id,
                                 decoration_form_name,
                                 decoration_technique_id,
                                 decoration_technique_name,
                                 formula_id,
                                 formula_name,
                                 sample_images_group_id,
                                 sample_images_group_name, 
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
