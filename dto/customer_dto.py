import logging

from init import config

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class CustomerDto:
    def __init__(self,
                 customer_id,
                 name,
                 birthday,
                 address,
                 phone,
                 email_address,
                 facebook,
                 recommended_by_id,
                 recommended_by_name,
                 registered_on):
        self.customer_id = customer_id
        self.name = name
        self.birthday = birthday
        self.address = address
        self.phone = phone
        self.email_address = email_address
        self.facebook = facebook
        self.recommended_by_id = recommended_by_id
        self.recommended_by_name = recommended_by_name
        self.registered_on = registered_on
        
