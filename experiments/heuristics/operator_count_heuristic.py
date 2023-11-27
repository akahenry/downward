from typing import List, Dict

class OperatorCountHeuristic:
    def __init__(self, operators: List[str], operators_costs: Dict[str, int], constraints: Dict[str, int]):
        self.operators = operators
        self.operators_costs = operators_costs
        self.constraints = constraints
        self.operators_count = {operator: 0 for operator in operators}
        self.operators_constraints = self.__compute_operators_constraints()

    def __compute_operators_constraints(self) -> Dict[str, List[str]]:
            # key: operator, value: list of mentioned constraints
            return {operator: [constraint for constraint in self.constraints if operator in constraint] for operator in self.operators}

    def _compute_operator_count(self):
        raise NotImplementedError()

    def compute(self) -> int:
        self._compute_operator_count()

        response = 0
        for operator in self.operators:
            response += self.operators_count[operator] * self.operators_costs[operator]

        return response