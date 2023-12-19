from typing import List, Dict


class PostHocHeuristic:
    constraints: List[str]
    constraints_values: Dict[str, int]
    operators: List[str]
    operators_costs: Dict[str, int]
    operators_count: Dict[str, int]
    operators_constraints: Dict[str, List[str]]

    def __init__(
        self, operators_costs: Dict[str, int], constraints_values: Dict[str, int]
    ):
        self.__init_operators(operators_costs)
        self.__init_constraints(constraints_values)
        self.operators_constraints = self.__compute_operators_constraints()

    def __init_constraints(self, constraints_values: Dict[str, int]):
        self.constraints = constraints_values.keys()
        self.constraints_values = constraints_values

    def __init_operators(self, operators_costs: Dict[str, int]):
        # Operators with no cost doesn't sum to satisfy a constraint which means that they must be ignored
        # If not ignored, the heuristic algorithm will enter in an endless loop
        relevant_operators = [
            operator for operator, cost in operators_costs.items() if cost > 0
        ]
        self.operators = relevant_operators
        self.operators_costs = {
            operator: operators_costs[operator] for operator in relevant_operators
        }
        self.operators_count = {operator: 0 for operator in relevant_operators}

    def __compute_operators_constraints(self) -> Dict[str, List[str]]:
        # key: operator, value: list of mentioned constraints
        return {
            operator: [
                constraint for constraint in self.constraints if operator in constraint
            ]
            for operator in self.operators
        }

    def _compute_post_hoc(self):
        raise NotImplementedError()

    def _update_constraints_with_selected_operator(self, operator: str, times: int = 1):
        for constraint in self.operators_constraints[operator]:
            self.constraints_values[constraint] -= (
                self.operators_costs[operator] * times
            )

    def compute(self) -> int:
        self._compute_post_hoc()

        response = 0
        for operator in self.operators:
            response += self.operators_count[operator] * self.operators_costs[operator]

        return response
