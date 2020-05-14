import logging

from flask_sqlalchemy import sqlalchemy

from init import Customer, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class CustomerRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_all_customers(self):
        return Customer.query. \
            order_by(Customer.name). \
            all()

    def get_paginated_customers(self,
                                page,
                                per_page,
                                search_text):
        customer_recs = Customer.query
        if search_text is not None and search_text != '':
            search_pattern = '%' + search_text + '%'
            customer_recs = customer_recs.filter((Customer.name.ilike(search_pattern)) |
                                                 (Customer.phone.ilike(search_pattern)) |
                                                 (Customer.facebook.ilike(search_pattern)))
        customer_recs = customer_recs.order_by(Customer.name)
        return customer_recs.paginate(page, per_page, error_out=False)
    
    def get_customer(self, customer_id):
        return Customer.query.filter(Customer.id == customer_id).first()

    def add_customer(self,
                     name,
                     birthday,
                     address,
                     phone,
                     email_address,
                     facebook,
                     recommended_by,
                     note):
        try:
            customer_rec = Customer(name=name,
                                    birthday=birthday,
                                    address=address,
                                    phone=phone,
                                    email_address=email_address,
                                    facebook=facebook,
                                    recommended_by=recommended_by,
                                    note=note)
            self.db.session.add(customer_rec)
            self.db.session.flush()
            return customer_rec.id
        
        except sqlalchemy.exc.SQLAlchemyError as e:
            message = 'Error: failed to add customer. Details: %s' % (str(e))
            CustomerRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_CUSTOMER_FAILED, message)

    def update_customer(self,
                        customer_id,
                        name,
                        birthday,
                        address,
                        phone,
                        email_address,
                        facebook,
                        recommended_by,
                        note):
        customer_rec = self.get_customer(customer_id)
        customer_rec.name = name
        customer_rec.birthday = birthday
        customer_rec.address = address
        customer_rec.phone = phone
        customer_rec.email_address = email_address
        customer_rec.facebook = facebook
        customer_rec.recommended_by = recommended_by
        customer_rec.note = note
        self.db.session.flush()
