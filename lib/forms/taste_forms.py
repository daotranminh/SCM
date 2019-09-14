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

class AddTasteForm(Form):
    name = StringField('Name*', [validators.InputRequired(), validators.Length(min=1, max=50)])
    description = TextAreaField('Description', render_kw={"rows": 10, "cols": 80})    
    def __init__(self, form):
        super(AddTasteForm, self).__init__(form)

class UpdateTasteForm(AddTasteForm):
    def __init__(self, form, taste_rec):
        super(UpdateTasteForm, self).__init__(form)

        if taste_rec is not None:
            self.name.data = taste_rec.name
            self.description.data = taste_rec.description
        
