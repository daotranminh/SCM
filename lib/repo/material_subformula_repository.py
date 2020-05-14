import logging

from flask_sqlalchemy import sqlalchemy
from init import Material, MaterialVersion, MaterialSubFormula, SubFormula, config
from utilities.scm_logger import ScmLogger

class MaterialSubFormulaRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_subformulas_having_material(self, material_id):
        material_subformula_query = self.db.session.query(MaterialSubFormula.subformula_id). \
            filter(MaterialSubFormula.material_id == material_id). \
            subquery()

        subformula_recs = self.db.session. \
            query(SubFormula). \
            join(material_subformula_query, SubFormula.id == material_subformula_query.c.subformula_id). \
            all()
        
        return subformula_recs

    def get_materials_of_subformula(self, subformula_id):
        return MaterialSubFormula.query. \
            filter(MaterialSubFormula.subformula_id == subformula_id). \
            all()

    def get_materials_of_subformula_w_uprice(self, subformula_id):
        sub_query_material = self.db.session. \
                             query(Material.id, Material.unit_amount, Material.unit). \
                             subquery()

        sub_query_material_version = self.db.session. \
                                     query(MaterialVersion.id, MaterialVersion.material_id, MaterialVersion.unit_price). \
                                     filter(MaterialVersion.is_current == True). \
                                     subquery()

        material_subformulas_w_uprice = self.db.session. \
                                     query(MaterialSubFormula, \
                                        sub_query_material.c.unit_amount, \
                                        sub_query_material.c.unit, \
                                        sub_query_material_version.c.id, \
                                        sub_query_material_version.c.unit_price). \
                                     filter(MaterialSubFormula.subformula_id == subformula_id). \
                                     join(sub_query_material_version, sub_query_material_version.c.material_id == MaterialSubFormula.material_id). \
                                     join(sub_query_material, sub_query_material.c.id == MaterialSubFormula.material_id). \
                                     all()
        return material_subformulas_w_uprice

    def get_material_dtos_of_subformula(self, subformula_id):
        sub_query_material = self.db.session. \
                             query(Material). \
                             subquery()

        material_subformula_dtos = self.db.session. \
                                    query(MaterialSubFormula, \
                                          sub_query_material.c.name, \
                                          sub_query_material.c.description, \
                                          sub_query_material.c.is_organic, \
                                          sub_query_material.c.unit). \
                                    filter(MaterialSubFormula.subformula_id == subformula_id). \
                                    join(sub_query_material, sub_query_material.c.id == MaterialSubFormula.material_id). \
                                    order_by(sub_query_material.c.name). \
                                    all()
        return material_subformula_dtos
    
    def delete_materials_of_subformula(self, subformula_id):
        MaterialSubFormula.query. \
            filter(MaterialSubFormula.subformula_id == subformula_id). \
            delete()
        self.db.session.flush()

    def add_material_subformula(self,
                             subformula_id,
                             material_id,
                             amount):
        try:
            material_subformula_rec = MaterialSubFormula(subformula_id=subformula_id,
                                                   material_id=material_id,
                                                   amount=amount)
            self.db.session.add(material_subformula_rec)
            self.db.session.flush()
        
        except sqlalchemy.exc.SQLAlchemyError as e:
            message = 'Error: failed to add material_subformula record. Details: %s' % (str(e))
            MaterialSubFormulaRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_MATERIAL_FORMULA_FAILED, message)
