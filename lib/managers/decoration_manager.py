import logging

from init import config
from dto.decoration_dto import DecorationDto
from dto.paginated_scm import PaginatedScm

logger = logging.getLogger(__name__)
handler = logging.FileHandler(config['DEFAULT']['log_file'])
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class DecorationManager:
    def __init__(self,
                 decoration_repo,
                 topic_repo,
                 decoration_form_repo,
                 decoration_technique_repo):
        self.decoration_repo = decoration_repo
        self.topic_repo = topic_repo
        self.decoration_form_repo = decoration_form_repo
        self.decoration_technique_repo = decoration_technique_repo

    def get_paginated_decoration_dtos(self,
                                   page,
                                   per_page,
                                   search_text):
        paginated_decorations = self.decoration_repo.get_paginated_decorations(page, per_page, search_text)
        paginated_decoration_dtos = self.__convert_to_paginated_decoration_dtos(paginated_decorations)

        return paginated_decoration_dtos

    def __convert_to_paginated_decoration_dtos(self,
                                               paginated_decorations):
        decoration_dtos = []
        for decoration_rec, topic_name, decoration_form, decoration_technique in paginated_decorations.items:
            decoration_dto = DecorationDto(decoration_rec.id,
                                           decoration_rec.name,
                                           decoration_rec.description,
                                           topic_name,
                                           decoration_form,
                                           decoration_technique,
                                           decoration_rec.registered_on)
            decoration_dtos.append(decoration_dto)
            
        paginated_decoration_dtos = PaginatedScm(decoration_dtos,
                                                 paginated_decorations.has_prev,
                                                 paginated_decorations.has_next,
                                                 paginated_decorations.prev_num,
                                                 paginated_decorations.next_num,
                                                 paginated_decorations.page,
                                                 paginated_decorations.pages)
            
        return paginated_decoration_dtos

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

    def get_decoration_info(self,
                            decoration_id):
        decoration_rec = self.decoration_repo.get_decoration(decoration_id)
        topic_rec = self.topic_repo.get_topic(decoration_rec.topic_id)
        decoration_form_rec = self.decoration_form_repo.get_decoration_form(decoration_rec.decoration_form_id)
        decoration_technique_rec = self.decoration_technique_repo.get_decoration_technique(decoration_rec.decoration_technique_id)
        template_path_recs = self.decoration_repo.get_template_paths(decoration_id)

        template_paths = []
        for template_path_rec in template_path_recs:
            template_paths.append(template_path_rec.template_path)

        return decoration_rec, topic_rec, decoration_form_rec, decoration_technique_rec, template_paths
