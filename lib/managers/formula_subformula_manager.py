import logging

from init import config
from dto.paginated_scm import PaginatedScm
from utilities.scm_logger import ScmLogger

class FormulaSubFormulaManager:
    logger = ScmLogger(__name__)

    def __init__(self,
                 formula_repo,
                 subformula_repo):
        self.formula_repo = formula_repo
        self.subformula_repo = subformula_repo
