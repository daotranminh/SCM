import logging

from init import config
from dto.paginated_scm import PaginatedScm
from utilities.scm_logger import ScmLogger

class FormulaManager:
    logger = ScmLogger(__name__)

    def __init__(self,
                 formula_repo,
                 formula_subformula_repo):
        self.formula_repo = formula_repo
        self.formula_subformula_repo = formula_subformula_repo

    def add_formula(self,
                    formula_name,
                    formula_description,
                    formula_note,
                    subformula_ids):
        new_formula_id = self.formula_repo.add_formula(name=formula_name,
                                                       description=formula_description,
                                                       note=formula_note)
        
        for subformula_id in subformula_ids:
            self.formula_subformula_repo.add_formula_subformula(new_formula_id,
                                                                subformula_id)
        
        return new_formula_id

    def delete_formula(self, formula_id):
        self.formula_subformula_repo.delete_subformulas_of_formula(formula_id)
        self.formula_repo.delete_formula(formula_id)