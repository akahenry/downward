from typing import Tuple

from operator_count_heuristic import OperatorCountHeuristic


class ImprovedLocalSearchHeuristic(OperatorCountHeuristic):
    def __compute_operator_performance(self, operator: str) -> float:
        return sum(
            [
                min(
                    1,
                    float(self.constraints_values[constraint])
                    / self.operators_costs[operator],
                )
                for constraint in self.operators_constraints[operator]
            ]
        )

    def __get_best_operator(self) -> Tuple[str, float]:
        best_operator: str = None
        best_operator_performance: int = None

        for operator in self.operators:
            operator_performance = self.__compute_operator_performance(operator)

            if (
                best_operator == None
                or best_operator_performance < operator_performance
            ):
                best_operator, best_operator_performance = (
                    operator,
                    operator_performance,
                )
                continue

        return best_operator, best_operator_performance

    def __compute_times_to_increment(self, operator: str, performance: float) -> int:
        return max(1, performance // self.operators_costs[operator])

    def _compute_operator_count(self):
        while any([value > 0 for value in self.constraints_values.values()]):
            best_operator, best_operator_performance = self.__get_best_operator()

            times_to_increment = self.__compute_times_to_increment(
                best_operator, best_operator_performance
            )

            self.operators_count[best_operator] += times_to_increment

            self._update_constraints_with_selected_operator(
                best_operator, times_to_increment
            )