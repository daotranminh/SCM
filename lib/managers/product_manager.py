import logging

from flask import url_for

from init import config

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class ProductManager:
    def __init__(self,
                 product_repo,
                 product_image_path_repo):
        self.product_repo = product_repo
        self.product_image_path_repo = product_image_path_repo

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