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

class AddMaterialForm(Form):
    #name = StringField(_('Material name*'), [validators.InputRequired(), validators.Length(min=1, max=50)])
    #unit = SelectField(_('Unit'))
    #unit_price = StringField(_('Unit price*'), [validators.InputRequired(), validators.Regexp('^\d*[.,]?\d*$', message=_('Unit price must be a decimal number'))])
    #is_organic = BooleanField(_('Is organic'))
    name = StringField('Material name*', [validators.InputRequired(), validators.Length(min=1, max=50)])
    unit = SelectField('Unit')
    unit_price = StringField('Unit price*', [validators.InputRequired(), validators.Regexp('^\d*[.,]?\d*$', message='Unit price must be a decimal number')])
    is_organic = BooleanField('Is organic')

    def __init__(self, form):
        super(AddMaterialForm, self).__init__(form)
        self.unit.choices = scm_constants.UNIT_CHOICES
