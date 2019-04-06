import logging

from init import Material, config

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class MaterialRepository:
    def __init__(self, db):
        self.db = db

    def get_all_materials(self):
        return Material.query.all()

    def get_material(self, id):
        return Material.query.filter(Material.id == id).first()

    def add_material(self,
                     name,
                     is_organic,
                     unit,
                     unit_price):
        try:
            material_rec = Material(name=name,
                                    is_organic=is_organic,
                                    unit=unit,
                                    unit_price=unit_price)
            self.db.session.add(material_rec)
        
        except sqlalchemy.exc.SQLAlchemyError as e:
            message = 'Error: failed to add material. Details: %s' % (str(e))
            logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_MATERIAL_FAILED, message)

    
