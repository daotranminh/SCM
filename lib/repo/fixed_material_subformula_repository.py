import logging

from flask_sqlalchemy import sqlalchemy

from init import FixedMaterialSubFormula, config
from utilities.scm_enums import ErrorCodes
from utilities.scm_exceptions import ScmException
from utilities.scm_logger import ScmLogger

class FixedMaterialSubFormulaRepository:
    logger = ScmLogger(__name__)

    def __init__(self, db):
        self.db = db

    def get_fixed_materials_of_fixed_subformula(self, fixed_subformula_id):
        return FixedMaterialSubFormula.query. \
            filter(FixedMaterialSubFormula.fixed_subformula_id == fixed_subformula_id). \
            order_by(FixedMaterialSubFormula.name). \
            all()

    def add_fixed_material_subformula(self,
                                      fixed_subformula_id,
                                      material_id,
                                      material_version_id,
                                      name,
                                      description,
                                      is_organic,
                                      unit_amount,
                                      unit,
                                      unit_price,
                                      amount,
                                      cost):
        try:
            fixed_material_subformula_rec = FixedMaterialSubFormula(fixed_subformula_id=fixed_subformula_id,
                                                                    material_id=material_id,
                                                                    material_version_id=material_version_id,
                                                                    name=name,
                                                                    description=description,
                                                                    is_organic=is_organic,
                                                                    unit_amount=unit_amount,
                                                                    unit=unit,
                                                                    unit_price=unit_price,
                                                                    amount=amount,
                                                                    cost=cost)
            self.db.session.add(fixed_material_subformula_rec)
            self.db.session.flush()
        except sqlalchemy.exc.SQLAlchemyError as ex:
            message = 'Error: failed to add fixed_material_subformula_rec. Details: %s' % (str(ex))
            FixedMaterialSubFormulaRepository.logger.error(message)
            raise ScmException(ErrorCodes.ERROR_ADD_FIXED_MATERIAL_SUBFORMULA_FAILED, message)