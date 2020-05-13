import logging

from flask_sqlalchemy import sqlalchemy

from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class PlateManager:
    logger = ScmLogger(__name__)

    def __init__(self, 
                 plate_repo,
                 product_repo,
                 order_repo):
        self.plate_repo = plate_repo
        self.product_repo = product_repo
        self.order_repo = order_repo

    def update_plate(self,
                     plate_id,
                     name,
                     description,
                     unit_count,
                     unit_price):
        plate_rec = self.plate_repo.get_plate(plate_id)
        self.update_plate_rec(plate_rec, name, description, unit_count, unit_price)

    def update_plate_rec(self,
                         plate_rec,
                         name,
                         description,
                         unit_count,
                         unit_price):
        if plate_rec.unit_count != unit_count or plate_rec.unit_price != unit_price:
            parent_product_recs = self.product_repo.get_products_having_plate(plate_rec.id)
            for parent_product_rec in parent_product_recs:
                self.product_repo.set_flag_has_up_to_date_cost_estimation_product_rec(parent_product_rec, False)
                self.order_repo.set_flag_has_up_to_date_cost_estimation(parent_product_rec.order_id, False)

        self.plate_repo.update_plate_rec(plate_rec, name, description, unit_count, unit_price)