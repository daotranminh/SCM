import logging

from flask_sqlalchemy import sqlalchemy

from init import Taste, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class TasteRepository:
    def __init__(self, db):
        self.db = db

    def get_all_tastes(self):
        return Taste.query.all()

    def get_taste(self, id):
        return Taste.query.filter(Taste.id == id).first()

    def add_taste(self,
                  name,
                  description):
        try:
            taste_rec = Taste(name=name, description=description)
            self.db.session.add(taste_rec)
            self.db.session.flush()
            return taste_rec.id
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add material. Details: %s' % (str(ex))
            logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_TASTE_FAILED, message)

    def update_taste(self,
                     taste_id,
                     name,
                     description):
        taste_rec = self.get_taste(taste_id)
        taste_rec.name = name
        taste_rec.description = description
