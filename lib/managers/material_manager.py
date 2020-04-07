import logging

from init import config
from dto.material_dto import MaterialDto

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class MaterialManager:
    def __init__(self,
                 material_repo,
                 material_version_repo):
        self.material_repo = material_repo
        self.material_version_repo = material_version_repo

    def add_material(self,
                     name,
                     description,
                     is_organic,
                     unit_amount,
                     unit,
                     unit_price):
        message = 'name=%s, unit=%s, unit_price=%s' % (name,
                                                       unit,
                                                       unit_price)
        logger.debug(message)
        new_material_id = self.material_repo.add_material(name,
                                                          description,
                                                          is_organic,
                                                          unit_amount,
                                                          unit)

        message = 'new_material_id=%s' % new_material_id
        logger.debug(message)
        self.material_version_repo.add_material_version(new_material_id,
                                                        unit_price,
                                                        0)

    def update_material(self,
                        material_id,
                        name,
                        description,                        
                        unit_price,
                        is_organic):
        material_rec = self.material_repo.get_material(material_id)
        material_version_rec = self.material_version_repo.get_latest_version_of_material(material_id)

        material_rec.name = name
        material_rec.description = description        
        material_rec.is_organic = is_organic        
        
        if unit_price != material_version_rec.unit_price:
            material_version_rec.is_current = False
            material_rec.latest_version += 1
            self.material_version_repo.add_material_version(material_id, 
                                                            unit_price,
                                                            material_rec.latest_version)
        
    def get_material_dtos(self):
        materials = self.material_repo.get_all_materials()
        material_dtos = []
        for material in materials:
            material_version = self.material_version_repo.get_latest_version_of_material(material.id)
            material_dto = MaterialDto(material.id,
                                       material.name,
                                       material.description,
                                       material.is_organic,
                                       material.unit_amount,
                                       material.unit,
                                       material_version.id,
                                       material_version.unit_price)
            material_dtos.append(material_dto)

        return material_dtos
