class FormulaDto:
    def __init__(self,
                 formula_id,
                 name,
                 description,
                 note,
                 total_cost,
                 registered_on):
        self.formula_id = formula_id
        self.name = name
        self.description = description
        self.note = note
        self.total_cost = total_cost
        self.registered_on = registered_on