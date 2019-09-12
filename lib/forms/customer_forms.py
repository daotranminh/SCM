import logging

from init import config
from utilities import scm_constants

from wtforms import Form, BooleanField, StringField, SelectField, DateTimeField, SubmitField, validators, widgets
from wtforms.fields.html5 import DateField

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class AddCustomerForm(Form):
    name = StringField('Customer name*', [validators.InputRequired(), validators.Length(min=1, max=50)])
    birthday = DateField('Birthday', format='%Y-%m-%d')
    address = StringField('Address', [validators.Length(min=0, max=200)])
    phone = StringField('Phone', [validators.Length(min=0, max=50)])
    email_address = StringField('Email', [validators.Length(min=0, max=200)])
    facebook = StringField('Facebook', [validators.Length(min=0, max=200)])    
    recommended_by = SelectField('Recommended by', coerce=int)

    def __init__(self, form, customer_choices):
        super(AddCustomerForm, self).__init__(form)
        self.recommended_by.choices = customer_choices

class UpdateCustomerForm(AddCustomerForm):
    def __init__(self, form, customer_choices, customer_rec):
        super(UpdateCustomerForm, self).__init__(form, customer_choices)
        
        if customer_rec is not None:
            self.name.data = customer_rec.name
            self.birthday.data = customer_rec.birthday
            self.address.data = customer_rec.address
            self.phone.data = customer_rec.phone
            self.email_address.data = customer_rec.email_address
            self.facebook.data = customer_rec.facebook            
            self.recommended_by.data = customer_rec.recommended_by
