import logging

from init import config
from dto.material_dto import MaterialDto
from utilities.scm_logger import ScmLogger

class MaterialManager:
    logger = ScmLogger(__name__)

    def __init__(self,
                 material_repo,
                 material_version_repo,
                 material_subformula_repo):
        self.material_repo = material_repo
        self.material_version_repo = material_version_repo
        self.material_subformula_repo = material_subformula_repo

    def add_material(self,
                     name,
                     description,
                     is_organic,
                     unit_amount,
                     unit,
                     unit_price):
        new_material_id = self.material_repo.add_material(name,
                                                          description,
                                                          is_organic,
                                                          unit_amount,
                                                          unit)
        self.material_version_repo.add_material_version(new_material_id,
                                                        unit_price,
                                                        0)

    def update_material(self,
                        material_id,
                        name,
                        description,            
                        unit_price):
        material_rec = self.material_repo.get_material(material_id)
        material_version_rec = self.material_version_repo.get_latest_version_of_material(material_id)

        material_rec.name = name
        material_rec.description = description
        
        if material_version_rec.unit_price != unit_price:
            material_version_rec.is_current = False
            material_rec.latest_version += 1
            self.material_version_repo.add_material_version(material_id, 
                                                            unit_price,
                                                            material_rec.latest_version)
            
            subformula_recs = self.material_subformula_repo.get_subformulas_having_material(material_rec.id)
            for subformula_rec in subformula_recs:
                subformula_rec.has_up_to_date_cost_estimation = False
        
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
