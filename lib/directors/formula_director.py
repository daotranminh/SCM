import logging

from init import config
from dto.paginated_scm import PaginatedScm
from utilities.scm_logger import ScmLogger

class FormulaDirector:
    logger = ScmLogger(__name__)

    def __init__(self,
                 formula_repo,
                 formula_manager,
                 subformula_manager):
        self.formula_repo = formula_repo
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
        
        self.formula_repo.set_cost_estimation(new_formula_id, total_cost)