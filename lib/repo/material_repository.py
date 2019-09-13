import logging

from flask_sqlalchemy import sqlalchemy

from init import Material, config
from utilities.scm_exceptions import ScmException

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class MaterialRepository:
    def __init__(self, db):
        self.db = db

    def get_all_materials(self):
        return Material.query.all()

    def get_material(self, id):
        return Material.query.filter(Material.id == id).first()

    def add_material(self,
                     name,
                     description,
                     is_organic,
                     unit):
        try:
            material_rec = Material(name=name,
                                    description=description,
                                    is_organic=is_organic,
                                    unit=unit)
            self.db.session.add(material_rec)
            self.db.session.flush()
            return material_rec.id
        
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add material. Details: %s' % (str(ex))
            logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_MATERIAL_FAILED, message)

    
