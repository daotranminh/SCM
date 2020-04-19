import logging

from init import config
from dto.formula_dto import FormulaDto
from dto.material_dto import MaterialFormulaDto
from dto.material_cost_estimation_dto import MaterialCostEstimationDto
from dto.paginated_scm import PaginatedScm
from utilities.scm_logger import ScmLogger

class FormulaManager:
    logger = ScmLogger(__name__)

    def __init__(self,
                 formula_repo,
                 material_formula_repo,
                 taste_repo,
                 material_version_cost_estimation_repo,
                 cost_estimation_repo,
                 product_repo,
                 order_repo):
        self.formula_repo = formula_repo
        self.material_formula_repo = material_formula_repo
        self.taste_repo = taste_repo
        self.material_version_cost_estimation_repo = material_version_cost_estimation_repo
        self.cost_estimation_repo = cost_estimation_repo
        self.product_repo = product_repo
        self.order_repo = order_repo

    def get_formula_info(self, formula_id):
        formula_rec = self.formula_repo.get_formula(formula_id)
        material_formulas_w_uprice = self.material_formula_repo.get_materials_of_formula_w_uprice(formula_id)

        total_cost = 0
        material_formulas = []

        for material_formula_rec, unit_amount, _, _, unit_price in material_formulas_w_uprice:
            material_formulas.append(material_formula_rec)
            total_cost += material_formula_rec.amount * unit_price / unit_amount

        return formula_rec, material_formulas, total_cost

    def get_formula_details(self, formula_id):
        formula_rec, taste_rec = self.formula_repo.get_formula_dto(formula_id)
        material_formula_dtos = self.material_formula_repo.get_material_dtos_of_formula(formula_id)

        material_dtos = []

        for material_formula_dto in material_formula_dtos:
            material_dto = MaterialFormulaDto(material_formula_dto[0].id,
                                              material_formula_dto[1],
                                              material_formula_dto[2],
                                              material_formula_dto[3],
                                              material_formula_dto[4],
                                              material_formula_dto[0].amount)
            material_dtos.append(material_dto)
            
        return formula_rec, taste_rec, material_dtos
        
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
        message = 'Added new formula "%s" with new_formula_id=%s' % (formula_name, new_formula_id)
        FormulaManager.logger.info(message)

        for i in range(len(material_ids)):
            self.material_formula_repo.add_material_formula(new_formula_id,
                                                            material_ids[i],
                                                            amounts[i])
            message = 'Added material (%s, %s) to formula %s' % (material_ids[i],
                                                                 amounts[i],
                                                                 new_formula_id)
            FormulaManager.logger.info(message)

        return new_formula_id

    def update_formula(self,
                       formula_id,
                       formula_name,
                       taste_id,
                       description,
                       note,
                       material_ids,
                       amounts):
        formula_rec = self.formula_repo.get_formula(formula_id)
        formula_rec.name = formula_name
        formula_rec.taste_id = taste_id
        formula_rec.description = description
        formula_rec.note = note

        existing_material_formula_recs = self.material_formula_repo.get_materials_of_formula(formula_id)        
        if self.__materials_of_formula_changed(existing_material_formula_recs,
                                               material_ids,
                                               amounts):
            message = 'Detected materials changed for formula %s' % formula_id
            FormulaManager.logger.info(message)
            formula_rec.has_up_to_date_cost_estimation = False

            message = 'Going to delete all existing material_formula of formula %s' % formula_id
            FormulaManager.logger.info(message)
            self.material_formula_repo.delete_materials_of_formula(formula_id)

            message = 'Going to add new material_formula of formula %s' % formula_id
            FormulaManager.logger.info(message)
            for i in range(len(material_ids)):                
                self.material_formula_repo.add_material_formula(formula_id,
                                                                material_ids[i],
                                                                amounts[i])
                message = 'Added (%s, %s) to formula %s' % (material_ids[i],
                                                            amounts[i],
                                                            formula_id)
                FormulaManager.logger.info(message)

    def __materials_of_formula_changed(self,
                                       existing_material_formula_recs,
                                       material_ids,
                                       amounts):
        if len(existing_material_formula_recs) != len(material_ids):
            return True
        
        checked = []
        for i in range(len(material_ids)):
            checked.append(False)
       
        for existing_material_formula_rec in existing_material_formula_recs:
            material_changed = True
            for i in range(len(material_ids)):                
                if checked[i] == False and existing_material_formula_rec.material_id == material_ids[i] and existing_material_formula_rec.amount == amounts[i]:
                    material_changed = False
                    checked[i] = True
                    break
            if material_changed:
                return True

        return False

    def get_paginated_formula_dtos(self,
                                   taste_id,
                                   page,
                                   per_page,
                                   search_text):
        paginated_formula_infos = self.formula_repo.get_paginated_formulas(
            taste_id,
            page,
            per_page,
            search_text)

        formula_dtos = []
        db_changed = False
        for formula_rec, formula_cost in paginated_formula_infos.items:
            up_to_date_formula_cost = formula_cost
            if formula_rec.has_up_to_date_cost_estimation == False:
                up_to_date_formula_cost = self.estimate_formula_cost(formula_rec.id)
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

    def estimate_formula_cost(self, formula_id):
        formula_rec = self.formula_repo.get_formula(formula_id)
        current_cost_estimation = self.cost_estimation_repo.get_current_cost_estimation_of_formula(formula_id)

        if formula_rec.has_up_to_date_cost_estimation == True:
            message = 'Formula %s has up-to-date cost estimation (%s). Return %s' % (formula_id, 
                                                                                     current_cost_estimation.id,
                                                                                     current_cost_estimation.total_cost)
            FormulaManager.logger.info(message)
            return current_cost_estimation.total_cost
        else:
            if current_cost_estimation is not None:
                current_cost_estimation.is_current = False

            new_cost_estimation_id = self.cost_estimation_repo.add_cost_estimation(formula_id)

            material_formulas_w_uprice = self.material_formula_repo.get_materials_of_formula_w_uprice(formula_id)
            total_cost = 0
        
            message = 'Formula %s does not has up-to-date cost estimation. Going to calculate new cost estimation' % formula_id
            FormulaManager.logger.info(message)

            for material_formula_rec, unit_amount, unit, material_version_id, unit_price in material_formulas_w_uprice:
                single_cost = material_formula_rec.amount * unit_price / unit_amount
                self.material_version_cost_estimation_repo.add_material_version_cost_estimation(
                    material_formula_rec.material_id,
                    material_version_id,
                    new_cost_estimation_id,
                    unit_amount,
                    unit,
                    unit_price,
                    material_formula_rec.amount,
                    single_cost)            
                total_cost += single_cost
                message = 'Added current cost %s of material %s to formula_cost' % (single_cost, material_formula_rec.material_id)
                FormulaManager.logger.info(message)

            message = 'Total formula cost = %s' % total_cost
            FormulaManager.logger.info(message)

            self.cost_estimation_repo.update_total_cost(new_cost_estimation_id, total_cost)
            self.formula_repo.set_flag_has_up_to_date_cost_estimation(formula_id, True)
            self.__update_product_cost_estimation(formula_id, new_cost_estimation_id, total_cost)
            
            return total_cost

    def __update_product_cost_estimation(self, 
                                         formula_id,
                                         new_cost_estimation_id,
                                         total_cost):
        message = 'Update product cost of (non-fixed) products having formula %s with cost estimation %s and total_cost %s' % (formula_id,
                                                                                                                               new_cost_estimation_id,
                                                                                                                               total_cost)
        FormulaManager.logger.info(message)

        product_recs = self.product_repo.get_products_having_formula(formula_id)
        order_ids_set = set()

        for product_rec in product_recs:
            if product_rec.is_fixed == False:                
                product_rec.cost_estimation_id = new_cost_estimation_id
                product_rec.total_cost = total_cost
                order_ids_set.add(product_rec.order_id)

                message = 'Updated product %s' % product_rec.id
        
        if len(order_ids_set) > 0:
            message = 'Update total cost of affected orders'
            FormulaManager.logger.info(message)

        for order_id in order_ids_set:
            order_rec = self.order_repo.get_order(order_id)
            order_cost = 0
            product_recs = self.product_repo.get_products_of_order(order_id)
            for product_rec in product_recs:
                if product_rec.total_cost is not None:
                    order_cost += product_rec.total_cost * product_rec.amount
            order_rec.total_cost = order_cost

            message = 'New cost of order %s is %s' % (order_id, order_cost)
            FormulaManager.logger.info(message)

    def get_cost_estimation(self, formula_id):        
        current_cost_estimation = self.cost_estimation_repo.get_current_cost_estimation_of_formula(formula_id)
        material_version_cost_estimations = self.material_version_cost_estimation_repo.get_material_version_cost_estimation_of_cost_estimation(current_cost_estimation.id)

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

    def get_taste_formula_dict(self):
        taste_formula_dict = {}
        formula_dict = {}

        formula_recs = self.formula_repo.get_all_formulas()
        for formula_rec in formula_recs:
            formula_dict[formula_rec.id] = formula_rec.name
            if formula_rec.taste_id in taste_formula_dict:
                taste_formula_dict[formula_rec.taste_id].append(formula_rec.id)
            else:
                taste_formula_dict[formula_rec.taste_id] = [formula_rec.id]

        return taste_formula_dict, formula_dict
