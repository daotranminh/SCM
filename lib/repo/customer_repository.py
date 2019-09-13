import logging

from flask_sqlalchemy import sqlalchemy

from init import Customer, config
from utilities.scm_exceptions import ScmException

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class CustomerRepository:
    def __init__(self, db):
        self.db = db

    def get_all_customers(self):
        return Customer.query.all()

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
        
        except sqlalchemy.exc.SQLAlchemyError as e:
            message = 'Error: failed to add customer. Details: %s' % (str(e))
            logger.error(message)
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
