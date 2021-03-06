import logging

from sqlalchemy import and_, desc

from init import MaterialVersion, config
from utilities.scm_logger import ScmLogger

class MaterialVersionRepository:
    logger = ScmLogger(__name__)
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

    def get_material_history(self, material_id):
        return MaterialVersion.query. \
            filter(MaterialVersion.material_id == material_id). \
            order_by(desc(MaterialVersion.registered_on)). \
            all()
    
    def add_material_version(self,
                             material_id,
                             unit_price,
                             version):
        try:
            material_version_rec = MaterialVersion(material_id=material_id,
                                                   unit_price=unit_price,
                                                   version=version)
            self.db.session.add(material_version_rec)
            self.db.session.flush()
            
            message = 'Add material_version (material_id, unit_price, version) = (%s, %s, %s)' % (material_id, unit_price, version)
            MaterialVersionRepository.logger.info(message)
        except sqlalchemy.exc.SQLAlchemyError as e:
            message = 'Error: failed to add material version. Details: %s' % (str(e))
            MaterialVersionRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_MATERIAL_VERSION_FAILED, message)
