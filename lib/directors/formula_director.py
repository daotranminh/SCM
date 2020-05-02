import logging

from init import config
from dto.formula_dto import FormulaDto
from dto.paginated_scm import PaginatedScm
from utilities.scm_logger import ScmLogger

class FormulaDirector:
    logger = ScmLogger(__name__)

    def __init__(self,
                 formula_repo,
                 formula_subformula_repo,
                 formula_manager,
                 subformula_manager):
        self.formula_repo = formula_repo
        self.formula_subformula_repo = formula_subformula_repo
        self.formula_manager = formula_manager
        self.subformula_manager = subformula_manager

    def add_formula(self,
                    formula_name,
                    formula_description,
                    formula_note,
                    subformula_ids):
        new_formula_id = self.formula_manager.add_formula(formula_name,
                                                          formula_description,
                                                          formula_note,
                                                          subformula_ids)
        total_cost = 0
        for subformula_id in subformula_ids:
            subformula_cost = self.subformula_manager.estimate_subformula_cost(subformula_id)
            total_cost += subformula_cost

        self.formula_repo.update_cost_estimation(new_formula_id, total_cost)

    def get_paginated_formula_dtos(self,
                                   page,
                                   per_page,
                                   search_text):
        paginated_formula_infos = self.formula_repo.get_paginated_formulas(
            page,
            per_page,
            search_text)

        formula_dtos = []
        db_changed = False
        for formula_rec in paginated_formula_infos.items:
            up_to_date_formula_cost = formula_rec.total_cost
            if formula_rec.has_up_to_date_cost_estimation == False:
                up_to_date_formula_cost = self.estimate_formula_rec_cost(formula_rec)
                db_changed = True

            formula_dto = FormulaDto(formula_rec.id,
                                     formula_rec.name,
                                     formula_rec.description,
                                     formula_rec.note,
                                     up_to_date_formula_cost,
                                     formula_rec.registered_on)
            formula_dtos.append(formula_dto)

        paginated_formula_dtos = PaginatedScm(formula_dtos,
                                              paginated_formula_infos.has_prev,
                                              paginated_formula_infos.has_next,
                                              paginated_formula_infos.prev_num,
                                              paginated_formula_infos.next_num,
                                              paginated_formula_infos.page,
                                              paginated_formula_infos.pages)
        return paginated_formula_dtos, db_changed

    def estimate_formula_rec_cost(self, formula_rec):
        if formula_rec.has_up_to_date_cost_estimation:
            return formula_rec.total_cost

        subformula_recs = self.formula_subformula_repo.get_subformulas_of_formula(formula_rec.id)
        total_cost = 0

        for subformula_rec in subformula_recs:
            subformula_cost = self.subformula_manager.estimate_subformula_cost(
                subformula_id=subformula_rec.subformula_id,
                update_parent_formula_cost=False)
            total_cost += subformula_cost

        formula_rec.total_cost = total_cost
        formula_rec.has_up_to_date_cost_estimation = True

        return total_cost

    def formula_cost_estimation_details(self, formula_id):
        formula_rec = self.formula_repo.get_formula(formula_id)
        subformula_dtos = self.formula_repo.get_subformula_dtos_of_formula(formula_id)

        current_subformula_cost_estimations = []
        material_cost_estimation_dtos = []
        subformula_recs = []
        taste_names = []
        begin_material_cost_estimation_dtos = []
        end_material_cost_estimation_dtos = []

        for subformula_rec, taste_name in subformula_dtos:
            subformula_recs.append(subformula_rec)
            taste_names.append(taste_name)

            current_subformula_cost_estimation, material_cost_estimation_dtos_per_subformula = \
                self.subformula_manager.get_cost_estimation(subformula_rec.id)

            current_subformula_cost_estimations.append(current_subformula_cost_estimation)
            begin_material_cost_estimation_dtos.append(len(material_cost_estimation_dtos))
            material_cost_estimation_dtos += material_cost_estimation_dtos_per_subformula
            end_material_cost_estimation_dtos.append(len(material_cost_estimation_dtos))

        return formula_rec, \
            subformula_recs, \
            taste_names, \
            current_subformula_cost_estimations, \
            material_cost_estimation_dtos, \
            begin_material_cost_estimation_dtos, \
            end_material_cost_estimation_dtos