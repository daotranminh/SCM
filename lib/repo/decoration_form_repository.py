import logging

from flask_sqlalchemy import sqlalchemy

from init import DecorationForm, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class DecorationFormRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_all_decoration_forms(self):
        return DecorationForm.query. \
            order_by(DecorationForm.name). \
            all()

    def get_paginated_decoration_forms(self,
                                       page,
                                       per_page,
                                       search_text):
        decoration_form_recs = DecorationForm.query
        if search_text is not None and search_text != '':
            search_pattern = '%' + search_text + '%'
            decoration_form_recs = decoration_form_recs.filter(DecorationForm.name.ilike(search_pattern))

        decoration_form_recs = decoration_form_recs.order_by(DecorationForm.name)
        return decoration_form_recs.paginate(page, per_page, error_out=False)

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
            DecorationFormRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_DECORATION_FORM_FAILED, message)

    def update_decoration_form(self,
                               decoration_form_id,
                               name,
                               description):
        decoration_form_rec = self.get_decoration_form(decoration_form_id)
        decoration_form_rec.name = name
        decoration_form_rec.description = description
        self.db.session.flush()
