import logging

from init import config
from utilities import scm_constants

from wtforms import Form, BooleanField, StringField, SelectField, DateTimeField, SubmitField, validators

from . import base_elements
#from base_forms import MultiCheckboxField

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class AddMaterialForm(Form):
    name = StringField('Material name*', [validators.InputRequired(), validators.Length(min=1, max=50)])
    description = StringField('Description', [validators.Length(min=1, max=400)])
    unit = SelectField('Unit')
    #unit_price = StringField('Unit price*', [validators.InputRequired(), validators.Regexp('^\d*[.,]?\d*$', message='Unit price must be a decimal number')])
    is_organic = base_elements.MultiCheckboxField('', coerce=int, choices=[(0, 'Is organic')]) 

    def __init__(self, form):
        super(AddMaterialForm, self).__init__(form)
        self.unit.choices = scm_constants.UNIT_CHOICES
