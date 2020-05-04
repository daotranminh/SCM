import logging

from init import config
from dto.paginated_scm import PaginatedScm
from dto.material_dto import MaterialSubFormulaDto
from utilities.scm_logger import ScmLogger

class FormulaManager:
    logger = ScmLogger(__name__)

    def __init__(self,
                 formula_repo,
                 subformula_repo,
                 formula_subformula_repo,
                 material_subformula_repo):
        self.formula_repo = formula_repo
        self.subformula_repo = subformula_repo
        self.formula_subformula_repo = formula_subformula_repo
        self.material_subformula_repo = material_subformula_repo

    def add_formula(self,
                    formula_name,
                    formula_description,
                    formula_note,
                    subformula_ids,
                    subformula_counts):
        new_formula_id = self.formula_repo.add_formula(name=formula_name,
                                                       description=formula_description,
                                                       note=formula_note)
        
        for i in range(len(subformula_ids)):
            self.formula_subformula_repo.add_formula_subformula(new_formula_id,
                                                                subformula_ids[i],
                                                                subformula_counts[i])
        
        return new_formula_id

    def delete_formula(self, formula_id):
        self.formula_subformula_repo.delete_subformulas_of_formula(formula_id)
        self.formula_repo.delete_formula(formula_id)

    def get_subformula_info_of_formula(self, formula_id):
        subformula_recs = self.subformula_repo.get_subformulas_of_formula(formula_id)
        subformula_counts = []

        for subformula_rec in subformula_recs:
            formula_subformula_rec_count = self.formula_subformula_repo.get_count(formula_id, subformula_rec.id)
            subformula_counts.append(formula_subformula_rec_count.count)

        return subformula_recs, subformula_counts

    def get_formula_details(self, formula_id):
        formula_rec = self.formula_repo.get_formula(formula_id)
        subformula_dtos = self.formula_repo.get_subformula_dtos_of_formula(formula_id)

        subformula_recs = []
        subformula_counts = []
        taste_names = []
        begin_material_dtos = []
        end_material_dtos = []
        material_dtos = []
        for subformula_rec, taste_name, count in subformula_dtos:
            subformula_recs.append(subformula_rec)
            subformula_counts.append(count)
            taste_names.append(taste_name)
            
            material_dtos_per_subformula = self.material_subformula_repo.get_material_dtos_of_subformula(subformula_rec.id)

            begin_material_dtos.append(len(material_dtos))
            for material_subformula_rec, \
                material_name, \
                material_description, \
                material_is_organic, \
                material_unit, \
                in material_dtos_per_subformula:
                material_dto = MaterialSubFormulaDto(material_subformula_rec.id,
                                                    material_name,
                                                    material_description,
                                                    material_is_organic,
                                                    material_unit,
                                                    material_subformula_rec.amount)
                material_dtos.append(material_dto)

            end_material_dtos.append(len(material_dtos))

        return formula_rec, \
            subformula_recs, \
            subformula_counts, \
            taste_names, \
            material_dtos, \
            begin_material_dtos, \
            end_material_dtos
