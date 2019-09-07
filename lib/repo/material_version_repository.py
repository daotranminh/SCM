import logging

from sqlalchemy import and_

from init import MaterialVersion, config

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class MaterialVersionRepository:
    def __init__(self, db):
        self.db = db

    def get_material_version(self, id):
        return MaterialVersion.query. \
            filter(MaterialVersion.id == id). \
            first()

    def get_latest_version_of_material(self, material_id):
        return MaterialVersion.query. \
            filter(and_(MaterialVersion.material_id == material_id, MaterialVersion.is_current == True)). \
            first()
    
    def add_material_version(self,
                             material_id,
                             unit_price):
        try:
            material_version_rec = MaterialVersion(material_id=material_id,
                                                   unit_price=unit_price)
            self.db.session.add(material_version_rec)
        
        except sqlalchemy.exc.SQLAlchemyError as e:
            message = 'Error: failed to add material version. Details: %s' % (str(e))
            logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_MATERIAL_VERSION_FAILED, message)
