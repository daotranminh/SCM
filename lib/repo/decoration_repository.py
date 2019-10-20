import logging

from flask_sqlalchemy import sqlalchemy

from init import Decoration, DecorationTemplatePath, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class DecorationRepository:
    def __init__(self, db):
        self.db = db

    def get_decoration(self, decoration_id):
        return Decoration.query.filter(Decoration.id == decoration_id).first()

    def get_decoration_dto(self, decoration_id):
        pass

    def get_all_decorations(self):
        return Decoration.query.all()

    def get_paginated_decorations(self,
                                  page,
                                  per_page,
                                  search_text):
        pass

    def add_decoration(self,
                       name,
                       description,                       
                       topic_id,
                       decoration_form_id,
                       decoration_technique_id):
        try:
            decoration_rec = Decoration(name=name,
                                        description=description,
                                        topic_id=topic_id,
                                        decoration_form_id=decoration_form_id,
                                        decoration_technique_id=decoration_technique_id)
            self.db.session.add(decoration_rec)
            self.db.session.flush()
            return decoration_rec.id
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add decoration record. Details: %s' % (str(ex))
            logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_DECORATION_FAILED, message)

    def add_decoration_template(self,
                                decoration_id,
                                template_path):
        try:
            decoration_template_path_rec = DecorationTemplatePath(decoration_id=decoration_id,
                                                                  template_path=template_path)
            self.db.session.add(decoration_template_path_rec)
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add decoration record. Details: %s' % (str(ex))
            logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_DECORATION_TEMPLATE_PATH_FAILED, message)

