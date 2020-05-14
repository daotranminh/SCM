import logging

from flask_sqlalchemy import sqlalchemy

from init import SubFormula, FormulaSubFormula, Taste, CostEstimation, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class SubFormulaRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_subformula(self, subformula_id):
        return SubFormula.query.filter(SubFormula.id == subformula_id).first()

    def get_subformula_dto(self, subformula_id):
        return self.db.session.query(SubFormula, Taste). \
            filter(SubFormula.id == subformula_id). \
            filter(SubFormula.taste_id == Taste.id). \
            first()
        
    def get_all_subformulas(self):
        return SubFormula.query.all()

    def get_subformulas_of_taste(self, taste_id):
        return SubFormula.query.filter(SubFormula.taste_id == taste_id).all()

    def get_subformulas_of_formula(self, formula_id):
        formula_subformula_query = self.db.session.query(FormulaSubFormula.subformula_id). \
            filter(FormulaSubFormula.formula_id == formula_id). \
            subquery()

        return self.db.session.query(SubFormula). \
            join(formula_subformula_query, SubFormula.id == formula_subformula_query.c.subformula_id). \
            all()

    def get_paginated_subformulas(self,
                                  page,
                                  per_page,
                                  search_text):
        cost_estimation_query = self.db.session.query(CostEstimation.subformula_id, CostEstimation.total_cost). \
            filter(CostEstimation.is_current == True). \
            subquery()

        subformula_query = self.db.session.query(SubFormula, cost_estimation_query.c.total_cost). \
            outerjoin(cost_estimation_query, SubFormula.id == cost_estimation_query.c.subformula_id)

        if search_text is not None and search_text != '':
            search_pattern = '%' + search_text + '%'
            subformula_query = subformula_query.filter((SubFormula.name.ilike(search_pattern)) |
                                                (SubFormula.description.ilike(search_pattern)))
        return subformula_query.paginate(page, per_page, error_out=False)


    def get_paginated_subformulas_per_taste(self,
                                            taste_id,
                                            page,
                                            per_page,
                                            search_text):
        cost_estimation_query = self.db.session.query(CostEstimation.subformula_id, CostEstimation.total_cost). \
            filter(CostEstimation.is_current == True). \
            subquery()

        subformula_query = self.db.session.query(SubFormula, cost_estimation_query.c.total_cost). \
            filter(SubFormula.taste_id == taste_id). \
            outerjoin(cost_estimation_query, SubFormula.id == cost_estimation_query.c.subformula_id)

        if search_text is not None and search_text != '':
            search_pattern = '%' + search_text + '%'
            subformula_query = subformula_query.filter((SubFormula.name.ilike(search_pattern)) |
                                                (SubFormula.description.ilike(search_pattern)))
        return subformula_query.paginate(page, per_page, error_out=False)

    def add_subformula(self,
                       name,
                       taste_id,
                       subformula_type,
                       description,
                       note):
        try:
            subformula_rec = SubFormula(name=name,
                                  taste_id=taste_id,
                                  subformula_type=subformula_type,
                                  description=description,
                                  note=note)
            self.db.session.add(subformula_rec)
            self.db.session.flush()
            return subformula_rec.id
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add subformula record. Details: %s' % (str(ex))
            SubFormulaRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_SUBFORMULA_FAILED, message)

    def set_flag_has_up_to_date_cost_estimation(self, subformula_id, flag):
        subformula_rec = self.get_subformula(subformula_id)
        self.set_flag_has_up_to_date_cost_estimation_subformula_rec(subformula_rec, flag)

    def set_flag_has_up_to_date_cost_estimation_subformula_rec(self, subformula_rec, flag):        
        subformula_rec.has_up_to_date_cost_estimation = flag
        self.db.session.flush()

        message = 'Set flag of subformula %s to %s' % (subformula_rec.id, flag)
        SubFormulaRepository.logger.info(message)

    def update_total_cost_subformula_rec(self, subformula_rec, new_total_cost):
        subformula_rec.total_cost = new_total_cost
        subformula_rec.has_up_to_date_cost_estimation = True
        self.db.session.flush()

        message = 'Set flag of subformula %s to True' % (subformula_rec.id)
        SubFormulaRepository.logger.info(message)