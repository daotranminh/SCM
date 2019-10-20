import logging

from flask_sqlalchemy import sqlalchemy

from init import DecorationForm, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class DecorationFormRepository:
    def __init__(self, db):
        self.db = db

    def get_all_decoration_forms(self):
        return DecorationForm.query.all()

    def get_decoration_form(self, id):
        return DecorationForm.query.filter(DecorationForm.id == id).first()

    def add_decoration_form(self,
                            name,
                            description):
        try:
            decoration_form_rec = DecorationForm(name=name, description=description)
            self.db.session.add(decoration_form_rec)
            self.db.session.flush()
            return decoration_form_rec.id
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add decoration form. Details: %s' % (str(ex))
            logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_DECORATION_FORM_FAILED, message)

    def update_decoration_form(self,
                               decoration_form_id,
                               name,
                               description):
        decoration_form_rec = self.get_decoration_form(decoration_form_id)
        decoration_form_rec.name = name
        decoration_form_rec.description = description
