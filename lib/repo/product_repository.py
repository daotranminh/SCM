import logging

from flask_sqlalchemy import sqlalchemy

from init import Product, SubFormula, DecorationForm, DecorationTechnique, SampleImagesGroup, CostEstimation, config
from utilities.scm_enums import ErrorCodes, BoxStatus
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class ProductRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_all_products(self):
        return Product.query.all()

    def get_product(self, id):
        return Product.query.filter(Product.id == id).first()

    def get_products_of_order(self, order_id):
        return Product.query.filter(Product.order_id == order_id).all()

    def get_products_having_subformula(self, subformula_id):
        return Product.query.filter(Product.subformula_id == subformula_id).all()

    def add_product(self,
                    name,
                    amount,
                    order_id,                    
                    formula_id,
                    decoration_form_id,
                    decoration_technique_id,
                    with_box):
        try:
            box_status = int(BoxStatus.BOX_NOT_NEEDED)
            if with_box:
                box_status = int(BoxStatus.BOX_WITH_PRODUCT_IN_PRODUCTION)
                
            product_rec = Product(name=name, 
                                  amount=amount,
                                  order_id=order_id,
                                  formula_id=formula_id,                                  
                                  decoration_form_id=decoration_form_id,
                                  decoration_technique_id=decoration_technique_id,
                                  box_status=box_status)
            self.db.session.add(product_rec)
            self.db.session.flush()
            return product_rec.id
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add product. Details: %s' % (str(ex))
            ProductRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_PRODUCT_FAILED, message)
            
    def delete_product(self, product_id):
        try:
            product_rec = self.get_product(product_id)
            if product_rec is not None:
                self.db.session.delete(product_rec)
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to delete product_rec %s. Detail: %s' % (str(product_id), str(ex))
            ProductRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_DELETE_PRODUCT_FAILED, message)

    def get_product_dto(self, product_id):
        decoration_form_query = self.db.session.query(DecorationForm.id, DecorationForm.name).subquery()
        decoration_technique_query = self.db.session.query(DecorationTechnique.id, DecorationTechnique.name).subquery()
        subformula_query = self.db.session.query(SubFormula.id, SubFormula.name, SubFormula.has_up_to_date_cost_estimation).subquery()
        sample_images_group_query = self.db.session.query(SampleImagesGroup.id, SampleImagesGroup.name).subquery()
        
        cost_estimation_query = self.db.session.query(CostEstimation.id, CostEstimation.total_cost). \
            filter(CostEstimation.is_current == True). \
            subquery()

        product_dto_query = self.db.session.query(Product, \
                                                  decoration_form_query.c.id, \
                                                  decoration_form_query.c.name, \
                                                  decoration_technique_query.c.id, \
                                                  decoration_technique_query.c.name, \
                                                  subformula_query.c.id, \
                                                  subformula_query.c.name, \
                                                  subformula_query.c.has_up_to_date_cost_estimation, \
                                                  sample_images_group_query.c.id, \
                                                  sample_images_group_query.c.name, \
                                                  cost_estimation_query.c.total_cost). \
            filter(Product.id == product_id). \
            join(decoration_form_query, Product.decoration_form_id == decoration_form_query.c.id). \
            join(decoration_technique_query, Product.decoration_technique_id == decoration_technique_query.c.id). \
            outerjoin(subformula_query, Product.subformula_id == subformula_query.c.id). \
            outerjoin(sample_images_group_query, Product.sample_images_group_id == sample_images_group_query.c.id). \
            outerjoin(cost_estimation_query, Product.cost_estimation_id == cost_estimation_query.c.id)
            
        return product_dto_query.first()