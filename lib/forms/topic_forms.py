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

class AddTopicForm(Form):
    name = StringField('Name*', [validators.InputRequired(), validators.Length(min=1, max=50)])
    parent_topic = SelectField('Parent topic', coerce=int)    
    description = TextAreaField('Description', render_kw={"rows": 10, "cols": 80})
    def __init__(self, form, topic_choices):
        super(AddTopicForm, self).__init__(form)
        self.parent_topic.choices = topic_choices

class UpdateTopicForm(AddTopicForm):
    def __init__(self, form, topic_rec, topic_choices):
        super(UpdateTopicForm, self).__init__(form, topic_choices)

        if topic_rec is not None:
            self.name.data = topic_rec.name
            self.parent_topic.data = topic_rec.parent_id
            self.description.data = topic_rec.description
        
