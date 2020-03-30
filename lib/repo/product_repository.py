import logging

from flask_sqlalchemy import sqlalchemy

from init import Product, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class ProductRepository:
    def __init__(self, db):
        self.db = db

    def get_all_products(self):
        return Product.query.all()

    def get_product(self, id):
        return Product.query.filter(Product.id == id).first()

    def add_product(self,
                    name,
                    order_id,
                    taste_id,
                    decoration_form_id,
                    decoration_technique_id):
        try:
            product_rec = Product(name=name, 
                                  order_id=order_id,
                                  taste_id=taste_id,
                                  decoration_form_id=decoration_form_id,
                                  decoration_technique_id=decoration_technique_id)
            self.db.session.add(product_rec)
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add product. Details: %s' % (str(ex))
            logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_PRODUCT_FAILED, message)
            
    def delete_product(self, product_id):
        try:
            product_rec = self.get_product(product_id)
            if product_rec is not None:
                self.db.session.delete(product_rec)
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to delete product_rec %s. Detail: %s' % (str(product_id), str(ex))
            logger.error(message)
            raise ScmException(ErrorCodes.ERROR_DELETE_PRODUCT_FAILED, message)