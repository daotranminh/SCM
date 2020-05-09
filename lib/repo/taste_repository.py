import logging

from flask_sqlalchemy import sqlalchemy

from init import Taste, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class TasteRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_all_tastes(self):
        return Taste.query.all()

    def get_taste(self, id):
        return Taste.query.filter(Taste.id == id).first()

    def get_first_taste(self):
        return Taste.query.first()

    def get_tastes_dict(self):
        taste_recs = self.get_all_tastes()
        tastes_dict = {}

        for taste_rec in taste_recs:
            tastes_dict[taste_rec.id] = taste_rec

        return tastes_dict

    def add_taste(self,
                  name,
                  description):
        try:
            taste_rec = Taste(name=name, description=description)
            self.db.session.add(taste_rec)
            self.db.session.flush()
            return taste_rec.id
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add taste. Details: %s' % (str(ex))
            TasteRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_TASTE_FAILED, message)

    def update_taste(self,
                     taste_id,
                     name,
                     description):
        taste_rec = self.get_taste(taste_id)
        taste_rec.name = name
        taste_rec.description = description
        self.db.session.flush()
        
