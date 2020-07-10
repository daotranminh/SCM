import logging
from sqlalchemy import desc

from flask_sqlalchemy import sqlalchemy

from init import Product, Formula, DecorationForm, DecorationTechnique, SampleImagesGroup, CostEstimation, Plate, Box, config
from utilities.scm_enums import ErrorCodes, BoxStatus
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class ProductRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_all_products(self):
        return Product.query. \
            order_by(desc(Product.id)). \
            all()

    def get_product(self, id):
        return Product.query.filter(Product.id == id).first()

    def get_products_of_order(self, order_id):
        return Product.query. \
            filter(Product.order_id == order_id). \
            order_by(Product.id). \
            all()

    def get_products_having_formula(self, formula_id):
        return Product.query.filter(Product.formula_id == formula_id).all()
    
    def get_products_having_plate(self, plate_id):
        return Product.query.filter(Product.plate_id == plate_id).all()

    def get_products_having_box(self, box_id):
        return Product.query.filter(Product.box_id == box_id).all()

    def get_product_dto(self, product_id):
        decoration_form_query = self.db.session.query(DecorationForm.id, DecorationForm.name).subquery()
        decoration_technique_query = self.db.session.query(DecorationTechnique.id, DecorationTechnique.name).subquery()
        plate_query = self.db.session.query(Plate.id, Plate.name).subquery()
        box_query = self.db.session.query(Box.id, Box.name).subquery()
        formula_query = self.db.session.query(Formula.id, Formula.name).subquery()
        sample_images_group_query = self.db.session.query(SampleImagesGroup.id, SampleImagesGroup.name).subquery()
        
        cost_estimation_query = self.db.session.query(CostEstimation.id, CostEstimation.total_cost). \
            filter(CostEstimation.is_current == True). \
            subquery()

        product_dto_query = self.db.session.query(Product, \
                                                  decoration_form_query.c.id, \
                                                  decoration_form_query.c.name, \
                                                  decoration_technique_query.c.id, \
                                                  decoration_technique_query.c.name, \
                                                  plate_query.c.id, \
                                                  plate_query.c.name, \
                                                  box_query.c.id, \
                                                  box_query.c.name, \
                                                  formula_query.c.id, \
                                                  formula_query.c.name, \
                                                  sample_images_group_query.c.id, \
                                                  sample_images_group_query.c.name). \
            filter(Product.id == product_id). \
            join(decoration_form_query, Product.decoration_form_id == decoration_form_query.c.id). \
            join(decoration_technique_query, Product.decoration_technique_id == decoration_technique_query.c.id). \
            outerjoin(plate_query, Product.plate_id == plate_query.c.id). \
            outerjoin(box_query, Product.box_id == box_query.c.id). \
            outerjoin(formula_query, Product.formula_id == formula_query.c.id). \
            outerjoin(sample_images_group_query, Product.sample_images_group_id == sample_images_group_query.c.id)
            
        return product_dto_query.first()

    def get_products_using_formula(self, formula_id):
        return Product.query.filter(Product.formula_id == formula_id).all()

    def add_product(self,
                    name,
                    amount,
                    order_id,                    
                    formula_id,
                    formula_amount,
                    decoration_form_id,
                    decoration_technique_id,
                    plate_id,
                    box_id,
                    box_to_be_returned):
        try:
            box_status = int(BoxStatus.BOX_NOT_NEEDED_TO_BE_RETURNED)
            if box_to_be_returned:
                box_status = int(BoxStatus.BOX_WITH_PRODUCT_IN_PRODUCTION)
                
            product_rec = Product(name=name, 
                                  amount=amount,
                                  order_id=order_id,
                                  formula_id=formula_id,
                                  formula_amount=formula_amount,                            
                                  decoration_form_id=decoration_form_id,
                                  decoration_technique_id=decoration_technique_id,
                                  plate_id=plate_id,
                                  box_id=box_id,
                                  box_status=box_status)
            self.db.session.add(product_rec)
            self.db.session.flush()
            return product_rec.id
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add product. Details: %s' % (str(ex))
            ProductRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_PRODUCT_FAILED, message)

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
                       sample_images_group_id):
        product_rec = self.get_product(product_id)
        self.update_product_rec(product_rec,
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

    def update_product_rec(self, 
                           product_rec,
                           product_name,
                           product_amount,
                           decoration_form_id,
                           decoration_technique_id,
                           plate_id,
                           box_id,
                           formula_id,
                           box_status,
                           box_returned_on,
                           sample_images_group_id):        
        product_rec.name = product_name
        product_rec.amount = product_amount
        product_rec.decoration_form_id = decoration_form_id
        product_rec.decoration_technique_id = decoration_technique_id
        product_rec.plate_id = plate_id
        product_rec.box_id = box_id
        product_rec.formula_id = formula_id
        product_rec.box_status = box_status
        product_rec.box_returned_on = box_returned_on
        product_rec.sample_images_group_id = sample_images_group_id
        self.db.session.flush()
            
    def delete_product(self, product_id):
        try:
            product_rec = self.get_product(product_id)
            if product_rec is not None:
                self.db.session.delete(product_rec)
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to delete product_rec %s. Detail: %s' % (str(product_id), str(ex))
            ProductRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_DELETE_PRODUCT_FAILED, message)

    def update_cost_product_rec(self, product_rec, new_total_cost):
        product_rec.total_cost = new_total_cost
        product_rec.has_up_to_date_cost_estimation = True
        self.db.session.flush()

        message = 'Set cost of product %s to %s' % (product_rec.id, new_total_cost)
        ProductRepository.logger.info(message)

    def set_product_rec_fixed_flag(self, product_rec, flag=True):
        product_rec.is_fixed = flag
        self.db.session.flush()

        message = 'Set fixed flag of product %s to %s' % (product_rec.id, flag)
        ProductRepository.logger.info(message)

    def update_price_to_customer_product_rec(self, product_rec, new_price_to_customer):
        product_rec.price_to_customer = new_price_to_customer
        self.db.session.flush()

    def set_flag_has_up_to_date_cost_estimation_product_rec(self, product_rec, flag):
        product_rec.has_up_to_date_cost_estimation = flag
        self.db.session.flush()

        message = 'Set flag of product %s to %s' % (product_rec.id, flag)
        ProductRepository.logger.info(message)