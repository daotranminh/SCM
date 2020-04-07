import logging

from init import config
from dto.formula_dto import FormulaDto
from dto.material_dto import MaterialFormulaDto
from dto.paginated_scm import PaginatedScm

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class FormulaManager:
    def __init__(self,
                 formula_repo,
                 material_formula_repo,
                 taste_repo,
                 material_version_cost_estimation_repo,
                 cost_estimation_repo):
        self.formula_repo = formula_repo
        self.material_formula_repo = material_formula_repo
        self.taste_repo = taste_repo
        self.material_version_cost_estimation_repo = material_version_cost_estimation_repo
        self.cost_estimation_repo = cost_estimation_repo

    def get_formula_info(self, formula_id):
        formula_rec = self.formula_repo.get_formula(formula_id)
        material_formulas_w_uprice = self.material_formula_repo.get_materials_of_formula(formula_id)

        total_cost = 0
        material_formulas = []

        for material_formula_rec, unit_amount, _, unit_price in material_formulas_w_uprice:
            material_formulas.append(material_formula_rec)
            total_cost += material_formula_rec.amount * unit_price / unit_amount

        return formula_rec, material_formulas, total_cost

    def get_formula_details(self, formula_id):
        formula_rec, taste_rec = self.formula_repo.get_formula_dto(formula_id)
        material_formula_dtos = self.material_formula_repo.get_material_dtos_of_formula(formula_id)

        material_dtos = []

        for material_formula_dto in material_formula_dtos:
            material_dto = MaterialFormulaDto(material_formula_dto[0].id,
                                              material_formula_dto[1],
                                              material_formula_dto[2],
                                              material_formula_dto[3],
                                              material_formula_dto[4],
                                              material_formula_dto[0].amount)
            material_dtos.append(material_dto)
            
        return formula_rec, taste_rec, material_dtos
        
    def add_formula(self,
                    formula_name,
                    taste_id,
                    description,
                    note,
                    material_ids,
                    amounts):
        new_formula_id = self.formula_repo.add_formula(formula_name,
                                                       taste_id,
                                                       description,
                                                       note)
        for i in range(len(material_ids)):
            self.material_formula_repo.add_material_formula(new_formula_id,
                                                            material_ids[i],
                                                            amounts[i])

    def update_formula(self,
                       formula_id,
                       formula_name,
                       taste_id,
                       description,
                       note,
                       material_ids,
                       amounts):
        formula_rec = self.formula_repo.get_formula(formula_id)
        formula_rec.name = formula_name
        formula_rec.taste_id = taste_id
        formula_rec.description = description
        formula_rec.note = note

        self.material_formula_repo.delete_materials_of_formula(formula_id)
        for i in range(len(material_ids)):
            self.material_formula_repo.add_material_formula(formula_id,
                                                            material_ids[i],
                                                            amounts[i])

    def get_paginated_formula_dtos(self,
                                   page,
                                   per_page,
                                   search_text):
        tastes_dict = self.taste_repo.get_tastes_dict()

        paginated_formula_recs = self.formula_repo.get_paginated_formulas(page,
                                                                          per_page,
                                                                          search_text)

        return self.__convert_to_paginated_formula_dtos(tastes_dict,
                                                        paginated_formula_recs)

    def __convert_to_formula_dtos(self,
                                 tastes_dict,
                                 formula_recs):
        formula_dtos = []
        for formula_rec in formula_recs:
            formula_dto = FormulaDto(formula_rec.id,
                                     formula_rec.name,
                                     tastes_dict[formula_rec.taste_id].name,
                                     formula_rec.description,
                                     formula_rec.note,
                                     formula_rec.registered_on)
            formula_dtos.append(formula_dto)

        return formula_dtos

    def __convert_to_paginated_formula_dtos(self,
                                            tastes_dict,
                                            paginated_formula_recs):
        formula_dtos = self.__convert_to_formula_dtos(tastes_dict,
                                                      paginated_formula_recs.items)
        paginated_formula_dtos = PaginatedScm(formula_dtos,
                                              paginated_formula_recs.has_prev,
                                              paginated_formula_recs.has_next,
                                              paginated_formula_recs.prev_num,
                                              paginated_formula_recs.next_num,
                                              paginated_formula_recs.page,
                                              paginated_formula_recs.pages)
        return paginated_formula_dtos

    def estimate_formula_cost(self, formula_id):
        material_recs = material_formula_repo.get_materials_of_formula(formula_id)