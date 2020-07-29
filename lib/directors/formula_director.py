import os
import logging

from init import config
from dto.formula_dto import FormulaDto
from dto.paginated_scm import PaginatedScm
from utilities.scm_logger import ScmLogger
from utilities.pdf_generator import PdfGenerator

class FormulaDirector:
    logger = ScmLogger(__name__)

    def __init__(self,
                 formula_repo,
                 formula_subformula_repo,
                 product_repo,
                 order_repo,
                 formula_manager,
                 subformula_manager):
        self.formula_repo = formula_repo
        self.formula_subformula_repo = formula_subformula_repo
        self.product_repo = product_repo
        self.order_repo = order_repo
        self.formula_manager = formula_manager
        self.subformula_manager = subformula_manager

    def add_formula(self,
                    formula_name,
                    formula_description,
                    formula_note,
                    subformula_ids,
                    subformula_counts):
        new_formula_id = self.formula_manager.add_formula(formula_name,
                                                          formula_description,
                                                          formula_note,
                                                          subformula_ids,
                                                          subformula_counts)
        total_cost = 0
        for i in range(len(subformula_ids)):
            subformula_cost = self.subformula_manager.estimate_subformula_cost(subformula_ids[i])
            total_cost += subformula_cost * subformula_counts[i]

        self.formula_repo.update_cost_estimation(new_formula_id, total_cost)

    def update_formula(self,
                       formula_id,
                       new_formula_name,
                       new_formula_description,
                       new_formula_note,
                       new_subformula_ids,
                       new_subformula_counts):        
        self.formula_repo.update_formula(formula_id,
                                         new_formula_name,
                                         new_formula_description,
                                         new_formula_note)
        formula_subformula_recs = self.formula_subformula_repo.get_formula_subformulas_of_formula(formula_id)

        self.formula_subformula_repo.delete_subformulas_of_formula(formula_id)
        total_cost = 0
        for i in range(len(new_subformula_ids)):
            self.formula_subformula_repo.add_formula_subformula(
                formula_id, 
                new_subformula_ids[i],
                new_subformula_counts[i])

            subformula_cost = self.subformula_manager.estimate_subformula_cost(
                    subformula_id=new_subformula_ids[i])

            total_cost += subformula_cost * new_subformula_counts[i]
        
        self.formula_repo.update_cost_estimation(formula_id, total_cost)

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

    def get_formula_cost_estimation_details(self, formula_id):
        formula_rec = self.formula_repo.get_formula(formula_id)
        subformula_dtos = self.formula_repo.get_subformula_dtos_of_formula(formula_id)

        current_subformula_cost_estimations = []
        material_cost_estimation_dtos = []
        subformula_recs = []
        subformula_counts = []
        taste_names = []
        begin_material_cost_estimation_dtos = []
        end_material_cost_estimation_dtos = []

        for subformula_rec, taste_name, count in subformula_dtos:
            subformula_recs.append(subformula_rec)
            subformula_counts.append(count)
            taste_names.append(taste_name)

            current_subformula_cost_estimation, material_cost_estimation_dtos_per_subformula = \
                self.subformula_manager.get_cost_estimation(subformula_rec.id)

            current_subformula_cost_estimations.append(current_subformula_cost_estimation)
            begin_material_cost_estimation_dtos.append(len(material_cost_estimation_dtos))
            material_cost_estimation_dtos += material_cost_estimation_dtos_per_subformula
            end_material_cost_estimation_dtos.append(len(material_cost_estimation_dtos))

        return formula_rec, \
            subformula_recs, \
            subformula_counts, \
            taste_names, \
            current_subformula_cost_estimations, \
            material_cost_estimation_dtos, \
            begin_material_cost_estimation_dtos, \
            end_material_cost_estimation_dtos

    def estimate_formula_cost(self, formula_id):
        formula_rec = self.formula_repo.get_formula(formula_id)
        return self.estimate_formula_rec_cost(formula_rec)

    def estimate_formula_rec_cost(self, formula_rec):
        if formula_rec.has_up_to_date_cost_estimation:
            return formula_rec.total_cost

        formula_subformula_recs = self.formula_subformula_repo.get_formula_subformulas_of_formula(formula_rec.id)
        total_cost = 0

        for formula_subformula_rec in formula_subformula_recs:
            subformula_cost = self.subformula_manager.estimate_subformula_cost(formula_subformula_rec.subformula_id)
            total_cost += subformula_cost * formula_subformula_rec.count

        self.formula_repo.update_cost_estimation_formula_rec(formula_rec, total_cost)
        self.__notify_parent_products_about_cost_estimation_changed(formula_rec.id)

        return total_cost

    def __notify_parent_products_about_cost_estimation_changed(self, formula_id):
        message = 'Going to notify (not-yet-fixed) product having formula %s formula_id about cost estimation change' % (formula_id)
        FormulaDirector.logger.info(message)

        parent_product_recs = self.product_repo.get_products_using_formula(formula_id)
        for parent_product_rec in parent_product_recs:
            self.product_repo.set_flag_has_up_to_date_cost_estimation_product_rec(parent_product_rec, False)
            self.order_repo.set_flag_has_up_to_date_cost_estimation(parent_product_rec.order_id, False)

    def export_formula_pdf(self, formula_id):
        pdf_generator = PdfGenerator()

        formula_rec, \
        subformula_recs, \
        subformula_counts, \
        taste_names, \
        material_dtos, \
        begin_material_dtos, \
        end_material_dtos = self.formula_manager.get_formula_details(formula_id)

        jinja_template_filepath = 'formula_pdf.html'
        output_pdf_filepath = 'download/formula_%s.pdf' % formula_id

        template_vars = { 'formula_rec' : formula_rec,
                          'subformula_recs' : subformula_recs,
                          'subformula_counts' : subformula_counts,
                          'taste_names' : taste_names,
                          'material_dtos' : material_dtos,
                          'begin_material_dtos' : begin_material_dtos,
                          'end_material_dtos' : end_material_dtos }

        pdf_generator.generate(
            jinja_template_filepath,
            template_vars,
            output_pdf_filepath)