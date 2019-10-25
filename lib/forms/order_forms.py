import logging

from init import config
from utilities import scm_constants

from wtforms import Form, BooleanField, StringField, SelectField, DateTimeField, SubmitField, validators, widgets, TextAreaField
from wtforms.fields.html5 import DateField

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class AddOrderForm(Form):
    customer = SelectField('Customer', coerce=int)
    taste = SelectField('Taste', coerce=int)
    decoration = SelectField('Decoration', coerce=int)  
    ordered_on = DateField('Ordered on', format='%Y-%m-%d', validators=(validators.Optional(),))
    delivered_on = DateField('Delivered on', format='%Y-%m-%d', validators=(validators.Required(),))
    delivery_method = SelectField('Delivery method', coerce=int)    
    message = TextAreaField('Note', render_kw={"rows": 5, "cols": 80})

    def __init__(self,
                 form,
                 customer_choices,
                 taste_choices,
                 decoration_choices,
                 delivery_method_choices):
        super(AddOrderForm, self).__init__(form)
        self.customer.choices = customer_choices
        self.taste.choices = taste_choices
        self.decoration.choices = decoration_choices
        self.delivery_method.choices = delivery_method_choices

class UpdateOrderForm(AddOrderForm):
    def __init__(self,
                 form,
                 customer_choices,
                 taste_choices,
                 decoration_choices,
                 delivery_method_choices,
                 order_rec):
        super(UpdateOrderForm, self).__init__(form,
                                                 customer_choices,
                                                 taste_choices,
                                                 decoration_choices,
                                                 delivery_method_choices)
        
        if order_rec is not None:
            self.customer.data = order_rec.customer_id
            self.taste.data = order_rec.taste_id
            self.decoration.data = order_rec.decoration_id
            self.delivery_method.data = order_rec.delivery_method_id
            self.message.data = order_rec.message
