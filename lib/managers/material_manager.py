import logging

from init import config
from dto.material_dto import MaterialDto
from dto.paginated_scm import PaginatedScm
from utilities.scm_logger import ScmLogger

class MaterialManager:
    logger = ScmLogger(__name__)

    def __init__(self,
                 material_repo,
                 material_version_repo,
                 material_subformula_repo,
                 subformula_repo,
                 product_repo,
                 order_repo,
                 formula_subformula_repo,
                 formula_repo):
        self.material_repo = material_repo
        self.material_version_repo = material_version_repo
        self.material_subformula_repo = material_subformula_repo
        self.subformula_repo = subformula_repo
        self.product_repo = product_repo
        self.order_repo = order_repo
        self.formula_subformula_repo = formula_subformula_repo
        self.formula_repo = formula_repo

    def get_material_dtos(self):
        material_recs = self.material_repo.get_all_materials()
        
        material_dtos = []
        for material_rec in material_recs:
            material_version = self.material_version_repo.get_latest_version_of_material(material_rec.id)
            material_dto = MaterialDto(material_rec.id,
                                       material_rec.name,
                                       material_rec.description,
                                       material_rec.is_organic,
                                       material_rec.unit_amount,
                                       material_rec.unit,
                                       material_version.id,
                                       material_version.unit_price)
            material_dtos.append(material_dto)
        return material_dtos

    def get_paginated_material_dtos(self,
                                    page,
                                    per_page,
                                    search_text,
                                    sorting_criteria):
        pageinated_material_recs = self.material_repo.get_paginated_materials(page,
                                                                              per_page,
                                                                              search_text,
                                                                              sorting_criteria)
        material_dtos = []
        for material in pageinated_material_recs.items:
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

        paginated_material_dtos = PaginatedScm(material_dtos,
                                               pageinated_material_recs.has_prev,
                                               pageinated_material_recs.has_next,
                                               pageinated_material_recs.prev_num,
                                               pageinated_material_recs.next_num,
                                               pageinated_material_recs.page,
                                               pageinated_material_recs.pages)

        return paginated_material_dtos

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
        self.__notify_subformula_about_price_change(material_rec.id)
    
    def __notify_subformula_about_price_change(self, material_id):            
        subformula_recs = self.material_subformula_repo.get_subformulas_having_material(material_id)
        for subformula_rec in subformula_recs:
            self.subformula_repo.set_flag_has_up_to_date_cost_estimation_subformula_rec(subformula_rec, False)

            formula_subformula_recs = self.formula_subformula_repo.get_formulas_of_subformula(subformula_rec.id)
            for formula_subformula_rec in formula_subformula_recs:
                self.formula_repo.set_flag_has_up_to_date_cost_estimation(formula_subformula_rec.formula_id, False)

                product_recs = self.product_repo.get_products_having_formula(formula_subformula_rec.formula_id)
                for product_rec in product_recs:
                    self.product_repo.set_flag_has_up_to_date_cost_estimation_product_rec(product_rec, False)
                    self.order_repo.set_flag_has_up_to_date_cost_estimation(product_rec.order_id, False)

