import logging

from flask_sqlalchemy import sqlalchemy

from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class BoxManager:
    logger = ScmLogger(__name__)

    def __init__(self, 
                 box_repo,
                 product_repo,
                 order_repo):
        self.box_repo = box_repo
        self.product_repo = product_repo
        self.order_repo = order_repo

    def update_box(self,
                   box_id,
                   name,
                   description,
                   unit_count,
                   unit_price):
        box_rec = self.box_repo.get_box(box_id)
        self.update_box_rec(box_rec, name, description, unit_count, unit_price)

    def update_box_rec(self,
                       box_rec,
                       name,
                       description,
                       unit_count,
                       unit_price):
        if box_rec.unit_count != unit_count or box_rec.unit_price != unit_price:
            parent_product_recs = self.product_repo.get_products_having_box(box_id)
            for parent_product_rec in parent_product_recs:
                self.product_repo.set_flag_has_up_to_date_cost_estimation_product_rec(parent_product_rec, False)
                self.order_repo.set_flag_has_up_to_date_cost_estimation(parent_product_rec.order_id, False)

        self.box_repo.update_box_rec(box_rec)