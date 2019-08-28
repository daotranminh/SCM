import logging

from init import Customer, config

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
        return Customer.query.filter(Customer.customer_id == customer_id).first()

    def add_customer(self,
                     name,
                     address,
                     phone,
                     email_address,
                     facebook):
        try:
            customer_rec = Customer(name=name,
                                    address=address,
                                    phone=phone,
                                    email_address=email_address,
                                    facebook=facebook)
            self.db.session.add(customer_rec)
        
        except sqlalchemy.exc.SQLAlchemyError as e:
            message = 'Error: failed to add customer. Details: %s' % (str(e))
            logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_CUSTOMER_FAILED, message)

    
