import logging

from flask_sqlalchemy import sqlalchemy

from init import DecorationTechnique, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class DecorationTechniqueRepository:
    logger = ScmLogger(__name__)
    
    def __init__(self, db):
        self.db = db

    def get_all_decoration_techniques(self):
        return DecorationTechnique.query.all()

    def get_decoration_technique(self, id):
        return DecorationTechnique.query.filter(DecorationTechnique.id == id).first()

    def add_decoration_technique(self,
                                 name,
                                 description):
        try:
            decoration_technique_rec = DecorationTechnique(name=name, description=description)
            self.db.session.add(decoration_technique_rec)
            self.db.session.flush()
            return decoration_technique_rec.id
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add decoration form. Details: %s' % (str(ex))
            DecorationTechniqueRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_DECORATION_TECHNIQUE_FAILED, message)

    def update_decoration_technique(self,
                                    decoration_technique_id,
                                    name,
                                    description):
        decoration_technique_rec = self.get_decoration_technique(decoration_technique_id)
        decoration_technique_rec.name = name
        decoration_technique_rec.description = description
