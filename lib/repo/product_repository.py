import logging

from flask_sqlalchemy import sqlalchemy

from init import Product, Formula, Taste, DecorationForm, DecorationTechnique, SampleImagesGroup, config
from utilities.scm_enums import ErrorCodes, BoxStatus
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

    def get_products_of_order(self, order_id):
        return Product.query.filter(Product.order_id == order_id).all()

    def add_product(self,
                    name,
                    order_id,
                    taste_id,
                    decoration_form_id,
                    decoration_technique_id,
                    with_box):
        try:
            box_status = int(BoxStatus.BOX_NOT_NEEDED)
            if with_box:
                box_status = int(BoxStatus.BOX_WITH_PRODUCT_IN_PRODUCTION)
                
            product_rec = Product(name=name, 
                                  order_id=order_id,
                                  taste_id=taste_id,
                                  decoration_form_id=decoration_form_id,
                                  decoration_technique_id=decoration_technique_id,
                                  box_status=box_status)
            self.db.session.add(product_rec)
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add product. Details: %s' % (str(ex))
            logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_PRODUCT_FAILED, message)

    def update_product(self,
                       product_id,
                       product_name,
                       taste_id,
                       decoration_form_id,
                       decoration_technique_id,
                       formula_id):
        product_rec = self.get_product(product_id)
        product_rec.name = product_name
        product_rec.taste_id = taste_id
        product_rec.decoration_form_id = decoration_form_id
        product_rec.decoration_technique_id = decoration_technique_id
        product_rec.formula_id = formula_id
            
    def delete_product(self, product_id):
        try:
            product_rec = self.get_product(product_id)
            if product_rec is not None:
                self.db.session.delete(product_rec)
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to delete product_rec %s. Detail: %s' % (str(product_id), str(ex))
            logger.error(message)
            raise ScmException(ErrorCodes.ERROR_DELETE_PRODUCT_FAILED, message)

    def get_product_dto(self, product_id):        
        taste_query = self.db.session.query(Taste.id, Taste.name).subquery()
        decoration_form_query = self.db.session.query(DecorationForm.id, DecorationForm.name).subquery()
        decoration_technique_query = self.db.session.query(DecorationTechnique.id, DecorationTechnique.name).subquery()
        formula_query = self.db.session.query(Formula.id, Formula.name).subquery()
        sample_images_group_query = self.db.session.query(SampleImagesGroup.id, SampleImagesGroup.name).subquery()

        product_dto_query = self.db.session.query(Product, \
                                                  taste_query.c.id, \
                                                  taste_query.c.name, \
                                                  decoration_form_query.c.id, \
                                                  decoration_form_query.c.name, \
                                                  decoration_technique_query.c.id, \
                                                  decoration_technique_query.c.name, \
                                                  formula_query.c.id, \
                                                  formula_query.c.name, \
                                                  sample_images_group_query.c.id, \
                                                  sample_images_group_query.c.name). \
            filter(Product.id == product_id). \
            join(taste_query, Product.taste_id == taste_query.c.id). \
            join(decoration_form_query, Product.decoration_form_id == decoration_form_query.c.id). \
            join(decoration_technique_query, Product.decoration_technique_id == decoration_technique_query.c.id). \
            outerjoin(formula_query, Product.formula_id == formula_query.c.id). \
            outerjoin(sample_images_group_query, Product.sample_images_group_id == sample_images_group_query.c.id)
            
        return product_dto_query.first()