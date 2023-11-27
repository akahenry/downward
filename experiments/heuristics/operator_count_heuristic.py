from typing import List, Dict


class OperatorCountHeuristic:
    constraints: List[str]
    constraints_values: Dict[str, int]
    operators: List[str]
    operators_costs: Dict[str, int]
    operators_count: Dict[str, int]
    operators_constraints: Dict[str, List[str]]

    def __init__(
        self, operators_costs: Dict[str, int], constraints_values: Dict[str, int]
    ):
        self.operators = operators_costs.keys()
        self.operators_costs = operators_costs
        self.constraints = constraints_values.keys()
        self.constraints_values = constraints_values
        self.operators_count = {operator: 0 for operator in self.operators}
        self.operators_constraints = self.__compute_operators_constraints()

    def __compute_operators_constraints(self) -> Dict[str, List[str]]:
        # key: operator, value: list of mentioned constraints
        return {
            operator: [
                constraint for constraint in self.constraints if operator in constraint
            ]
            for operator in self.operators
        }

    def _compute_operator_count(self):
        raise NotImplementedError()

    def _update_constraints_with_selected_operator(self, operator: str, times: int = 1):
        for constraint in self.operators_constraints[operator]:
            if self.constraints_values[constraint] > 0:
                self.constraints_values[constraint] -= (
                    self.operators_costs[operator] * times
                )

    def compute(self) -> int:
        self._compute_operator_count()

        response = 0
        for operator in self.operators:
            response += self.operators_count[operator] * self.operators_costs[operator]

        return response