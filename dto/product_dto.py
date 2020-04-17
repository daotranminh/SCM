import logging

from init import config

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class ProductDto:
    def __init__(self,
                 product_id,
                 product_name,
                 product_amount,
                 taste_id,
                 taste_name,
                 decoration_form_id,
                 decoration_form_name,
                 decoration_technique_id,
                 decoration_technique_name,
                 formula_id,
                 formula_name,
                 formula_has_up_to_date_cost_estimation,
                 price_to_customer,
                 sample_images_group_id,
                 sample_images_group_name,
                 product_cost_estimation,
                 latest_3_sample_image_paths,
                 latest_3_product_image_paths):
        self.product_id = product_id
        self.product_name = product_name
        self.product_amount = product_amount
        self.taste_id = taste_id
        self.taste_name = taste_name
        self.decoration_form_id = decoration_form_id
        self.decoration_form_name = decoration_form_name
        self.decoration_technique_id = decoration_technique_id
        self.decoration_technique_name = decoration_technique_name
        self.formula_id = formula_id
        self.formula_name = formula_name
        self.formula_has_up_to_date_cost_estimation = formula_has_up_to_date_cost_estimation
        self.price_to_customer = price_to_customer
        self.sample_images_group_id = sample_images_group_id
        self.sample_images_group_name = sample_images_group_name
        self.product_cost_estimation = product_cost_estimation
        self.sample_image_0 = latest_3_sample_image_paths[0]
        self.sample_image_1 = latest_3_sample_image_paths[1]
        self.sample_image_2 = latest_3_sample_image_paths[2]
        self.product_image_0 = latest_3_product_image_paths[0]
        self.product_image_1 = latest_3_product_image_paths[1]
        self.product_image_2 = latest_3_product_image_paths[2]