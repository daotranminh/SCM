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

class AddDecorationFormForm(Form):
    name = StringField('Name*', [validators.InputRequired(), validators.Length(min=1, max=50)])
    description = TextAreaField('Description', render_kw={"rows": 10, "cols": 80})
    def __init__(self, form):
        super(AddDecorationFormForm, self).__init__(form)

class UpdateDecorationFormForm(AddDecorationFormForm):
    def __init__(self, form, decoration_form_rec):
        super(UpdateDecorationFormForm, self).__init__(form)

        if decoration_form_rec is not None:
            self.name.data = decoration_form_rec.name
            self.description.data = decoration_form_rec.description
