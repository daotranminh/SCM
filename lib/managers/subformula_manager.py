import logging

from init import config
from dto.subformula_dto import SubFormulaDto
from dto.material_dto import MaterialSubFormulaDto
from dto.material_cost_estimation_dto import MaterialCostEstimationDto
from dto.paginated_scm import PaginatedScm
from utilities.scm_logger import ScmLogger

class SubFormulaManager:
    logger = ScmLogger(__name__)

    def __init__(self,
                 subformula_repo,
                 material_subformula_repo,
                 taste_repo,
                 material_version_cost_estimation_repo,
                 cost_estimation_repo,
                 product_repo,
                 order_repo,
                 formula_subformula_repo,
                 formula_repo):
        self.subformula_repo = subformula_repo
        self.material_subformula_repo = material_subformula_repo
        self.taste_repo = taste_repo
        self.material_version_cost_estimation_repo = material_version_cost_estimation_repo
        self.cost_estimation_repo = cost_estimation_repo
        self.product_repo = product_repo
        self.order_repo = order_repo
        self.formula_subformula_repo = formula_subformula_repo
        self.formula_repo = formula_repo

    def get_subformula_info(self, subformula_id):
        subformula_rec = self.subformula_repo.get_subformula(subformula_id)
        material_subformulas_w_uprice = self.material_subformula_repo.get_materials_of_subformula_w_uprice(subformula_id)

        total_cost = 0
        material_subformulas = []

        for material_subformula_rec, unit_amount, _, _, unit_price in material_subformulas_w_uprice:
            material_subformulas.append(material_subformula_rec)
            total_cost += material_subformula_rec.amount * unit_price / unit_amount

        return subformula_rec, material_subformulas, total_cost

    def get_subformula_details(self, subformula_id):
        subformula_rec, taste_rec = self.subformula_repo.get_subformula_dto(subformula_id)
        material_subformula_dtos = self.material_subformula_repo.get_material_dtos_of_subformula(subformula_id)

        material_dtos = []

        for material_subformula_rec, \
            material_name, \
            material_description, \
            material_is_organic, \
            material_unit, \
            in material_subformula_dtos:
            material_dto = MaterialSubFormulaDto(material_subformula_rec.id,
                                                 material_name,
                                                 material_description,
                                                 material_is_organic,
                                                 material_unit,
                                                 material_subformula_rec.amount)
            material_dtos.append(material_dto)
            
        return subformula_rec, taste_rec, material_dtos

    def get_cost_estimation(self, subformula_id):        
        current_cost_estimation = self.cost_estimation_repo.get_current_cost_estimation_of_subformula(subformula_id)
        material_version_cost_estimations = \
            self.material_version_cost_estimation_repo.get_material_version_cost_estimation_of_cost_estimation(current_cost_estimation.id)

        material_cost_estimation_dtos = []
        for material_version_cost_estimation, material_name in material_version_cost_estimations:
            material_cost_estimation_dto = MaterialCostEstimationDto(material_version_cost_estimation.id,
                                                                     material_version_cost_estimation.material_id,
                                                                     material_version_cost_estimation.material_verion_id,
                                                                     material_version_cost_estimation.cost_estimation_id,
                                                                     material_version_cost_estimation.unit_amount,
                                                                     material_version_cost_estimation.unit,
                                                                     material_version_cost_estimation.unit_price,
                                                                     material_version_cost_estimation.amount,
                                                                     material_version_cost_estimation.cost,
                                                                     material_name)
            material_cost_estimation_dtos.append(material_cost_estimation_dto)

        return current_cost_estimation, material_cost_estimation_dtos

    def get_taste_subformula_dict(self):
        taste_subformula_dict = {}
        subformula_dict = {}

        subformula_recs = self.subformula_repo.get_all_subformulas()
        for subformula_rec in subformula_recs:
            subformula_dict[subformula_rec.id] = subformula_rec.name
            if subformula_rec.taste_id in taste_subformula_dict:
                taste_subformula_dict[subformula_rec.taste_id].append(subformula_rec.id)
            else:
                taste_subformula_dict[subformula_rec.taste_id] = [subformula_rec.id]

        return taste_subformula_dict, subformula_dict

    def get_paginated_subformula_dtos(self,
                                   taste_id,
                                   page,
                                   per_page,
                                   search_text):
        paginated_subformula_infos = self.subformula_repo.get_paginated_subformulas(
            taste_id,
            page,
            per_page,
            search_text)

        subformula_dtos = []
        db_changed = False
        for subformula_rec, subformula_cost in paginated_subformula_infos.items:
            up_to_date_subformula_cost = subformula_cost
            if subformula_rec.has_up_to_date_cost_estimation == False:
                up_to_date_subformula_cost = self.estimate_subformula_cost(subformula_rec.id)
                db_changed = True

            subformula_dto = SubFormulaDto(subformula_rec.id,
                                     subformula_rec.name,
                                     subformula_rec.subformula_type,
                                     subformula_rec.description,
                                     subformula_rec.note,
                                     up_to_date_subformula_cost,
                                     subformula_rec.registered_on)
            subformula_dtos.append(subformula_dto)

        paginated_subformula_dtos = PaginatedScm(subformula_dtos,
                                              paginated_subformula_infos.has_prev,
                                              paginated_subformula_infos.has_next,
                                              paginated_subformula_infos.prev_num,
                                              paginated_subformula_infos.next_num,
                                              paginated_subformula_infos.page,
                                              paginated_subformula_infos.pages)
        return paginated_subformula_dtos, db_changed        
        
    def add_subformula(self,
                    subformula_name,
                    taste_id,
                    subformula_type,
                    description,
                    note,
                    material_ids,
                    amounts):
        new_subformula_id = self.subformula_repo.add_subformula(subformula_name,
                                                       taste_id,
                                                       subformula_type,
                                                       description,
                                                       note)
        message = 'Added new subformula "%s" with new_subformula_id=%s' % (subformula_name, new_subformula_id)
        SubFormulaManager.logger.info(message)

        for i in range(len(material_ids)):
            self.material_subformula_repo.add_material_subformula(new_subformula_id,
                                                            material_ids[i],
                                                            amounts[i])
            message = 'Added material (%s, %s) to subformula %s' % (material_ids[i],
                                                                 amounts[i],
                                                                 new_subformula_id)
            SubFormulaManager.logger.info(message)

        return new_subformula_id

    def update_subformula(self,
                       subformula_id,
                       subformula_name,
                       taste_id,
                       subformula_type,
                       description,
                       note,
                       material_ids,
                       amounts):
        subformula_rec = self.subformula_repo.get_subformula(subformula_id)
        subformula_rec.name = subformula_name
        subformula_rec.taste_id = taste_id
        subformula_rec.subformula_type = subformula_type
        subformula_rec.description = description
        subformula_rec.note = note

        existing_material_subformula_recs = self.material_subformula_repo.get_materials_of_subformula(subformula_id)        
        if self.__materials_of_subformula_changed(existing_material_subformula_recs,
                                                  material_ids,
                                                  amounts):
            message = 'Detected materials changed for subformula %s' % subformula_id
            SubFormulaManager.logger.info(message)
            self.subformula_repo.set_flag_has_up_to_date_cost_estimation_subformula_rec(subformula_rec, False)

            message = 'Going to delete all existing material_subformula of subformula %s' % subformula_id
            SubFormulaManager.logger.info(message)
            self.material_subformula_repo.delete_materials_of_subformula(subformula_id)

            message = 'Going to add new material_subformula of subformula %s' % subformula_id
            SubFormulaManager.logger.info(message)
            for i in range(len(material_ids)):                
                self.material_subformula_repo.add_material_subformula(subformula_id,
                                                                material_ids[i],
                                                                amounts[i])
                message = 'Added (%s, %s) to subformula %s' % (material_ids[i],
                                                            amounts[i],
                                                            subformula_id)
                SubFormulaManager.logger.info(message)

    def __materials_of_subformula_changed(self,
                                       existing_material_subformula_recs,
                                       material_ids,
                                       amounts):
        if len(existing_material_subformula_recs) != len(material_ids):
            return True
        
        checked = []
        for i in range(len(material_ids)):
            checked.append(False)
       
        for existing_material_subformula_rec in existing_material_subformula_recs:
            material_changed = True
            for i in range(len(material_ids)):                
                if checked[i] == False and existing_material_subformula_rec.material_id == material_ids[i] and existing_material_subformula_rec.amount == amounts[i]:
                    material_changed = False
                    checked[i] = True
                    break
            if material_changed:
                return True

        return False

    def estimate_subformula_cost(self, subformula_id):
        subformula_rec = self.subformula_repo.get_subformula(subformula_id)

        if subformula_rec.has_up_to_date_cost_estimation == True:
            message = 'SubFormula %s has up-to-date cost estimation. Return %s' % (subformula_id,
                                                                                   subformula_rec.total_cost)
            SubFormulaManager.logger.info(message)
            return subformula_rec.total_cost

        current_cost_estimation = self.cost_estimation_repo.get_current_cost_estimation_of_subformula(subformula_id)
        if current_cost_estimation is not None:
            current_cost_estimation.is_current = False

        new_cost_estimation_id = self.cost_estimation_repo.add_cost_estimation(subformula_id)

        material_subformulas_w_uprice = self.material_subformula_repo.get_materials_of_subformula_w_uprice(subformula_id)
        total_cost = 0
        
        message = 'SubFormula %s does not has up-to-date cost estimation. Going to calculate new cost estimation' % subformula_id
        SubFormulaManager.logger.info(message)

        for material_subformula_rec, unit_amount, unit, material_version_id, unit_price in material_subformulas_w_uprice:
            single_cost = material_subformula_rec.amount * unit_price / unit_amount
            self.material_version_cost_estimation_repo.add_material_version_cost_estimation(
                material_subformula_rec.material_id,
                material_version_id,
                new_cost_estimation_id,
                unit_amount,
                unit,
                unit_price,
                material_subformula_rec.amount,
                single_cost)            
            total_cost += single_cost
            message = 'Added current cost %s of material %s to subformula_cost' % (single_cost, material_subformula_rec.material_id)
            SubFormulaManager.logger.info(message)

        message = 'Total subformula cost = %s' % total_cost
        SubFormulaManager.logger.info(message)

        self.cost_estimation_repo.update_total_cost(new_cost_estimation_id, total_cost)
        self.subformula_repo.update_total_cost_subformula_rec(subformula_rec, total_cost)
        self.__notify_parent_formula_about_cost_estimation_change(subformula_id)
            
        return total_cost

    def __notify_parent_formula_about_cost_estimation_change(self, subformula_id):
        message = 'Going to notify parent formulas of subformula %s about cost estimation change' % subformula_id
        SubFormulaManager.logger.info(message)

        formula_subformula_recs = self.formula_subformula_repo.get_formulas_of_subformula(subformula_id)
        for formula_subformula_rec in formula_subformula_recs:
            self.formula_repo.set_flag_has_up_to_date_cost_estimation(formula_subformula_rec.formula_id, False)

            product_recs = self.product_repo.get_products_having_formula(formula_subformula_rec.formula_id)
            for product_rec in product_recs:
                self.product_repo.set_flag_has_up_to_date_cost_estimation_product_rec(product_rec, False)
                self.order_repo.set_flag_has_up_to_date_cost_estimation(product_rec.order_id, False)
