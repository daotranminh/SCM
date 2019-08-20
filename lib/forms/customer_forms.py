import logging

from init import config
from utilities import scm_constants

from wtforms import Form, BooleanField, StringField, SelectField, DateTimeField, SubmitField, validators, widgets

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class AddCustomerForm(Form):
    name = StringField('Customer name*', [validators.InputRequired(), validators.Length(min=1, max=50)])
    address = StringField('Address')
    phone = StringField('Phone')
    email_address = StringField('Email')
    facebook = StringField('Facebook')    

    def __init__(self, form):
        super(AddCustomerForm, self).__init__(form)
