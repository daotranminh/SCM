import logging

from init import config
from dto.formula_dto import FormulaDto
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
                 taste_repo):
        self.formula_repo = formula_repo
        self.material_formula_repo = material_formula_repo
        self.taste_repo = taste_repo

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
