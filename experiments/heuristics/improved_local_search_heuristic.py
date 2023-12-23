from typing import Dict, Callable, Iterable

from post_hoc_heuristic import PostHocHeuristic

from math import ceil
from enum import Enum


class TieBreakingOperation(Enum):
    MAX_CONSTRAINT = 1
    SUM_CONSTRAINTS = 2
    SUM_SQUARE_CONSTRAINTS = 3


class ImprovedLocalSearchHeuristic(PostHocHeuristic):

    tie_breaking_operation: TieBreakingOperation

    def __init__(
        self,
        operators_costs: Dict[str, int],
        constraints_values: Dict[str, int],
        tie_breaking_operation: TieBreakingOperation = TieBreakingOperation.SUM_SQUARE_CONSTRAINTS,
    ):
        super().__init__(operators_costs, constraints_values)
        self.tie_breaking_operation = tie_breaking_operation

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

    def __compute_tie_breaking(self, a: str, b: str) -> str:
        if self.tie_breaking_operation == TieBreakingOperation.MAX_CONSTRAINT:
            return self.__compute_tie_breaking_max_constraint(a, b)
        elif self.tie_breaking_operation == TieBreakingOperation.SUM_CONSTRAINTS:
            return self.__compute_tie_breaking_sum_constraints(a, b)
        elif self.tie_breaking_operation == TieBreakingOperation.SUM_SQUARE_CONSTRAINTS:
            return self.__compute_tie_breaking_sum_square_constraints(a, b)

        raise Exception("TieBreakingOperation not found")

    def __compute_tie_breaking_max_constraint(self, a: str, b: str) -> str:
        a_max_constraint_value = self.__get_max_constraint_value_for_operator(a)
        b_max_constraint_value = self.__get_max_constraint_value_for_operator(b)

        return b if a_max_constraint_value < b_max_constraint_value else a

    def __compute_tie_breaking_sum_constraints(self, a: str, b: str) -> str:
        a_sum_constraints_values = self.__get_sum_constraint_value_for_operator(a)
        b_sum_constraints_values = self.__get_sum_constraint_value_for_operator(b)

        return b if a_sum_constraints_values < b_sum_constraints_values else a

    def __compute_tie_breaking_sum_square_constraints(self, a: str, b: str) -> str:
        a_sum_constraints_values = self.__get_sum_square_constraint_value_for_operator(
            a
        )
        b_sum_constraints_values = self.__get_sum_square_constraint_value_for_operator(
            b
        )

        return b if a_sum_constraints_values < b_sum_constraints_values else a

    def __get_max_constraint_value_for_operator(self, a: str) -> int:
        return self.__get_lambda_constraint_value_for_operator(a, max)

    def __get_sum_constraint_value_for_operator(self, a: str) -> int:
        return self.__get_lambda_constraint_value_for_operator(a, sum)

    def __get_sum_square_constraint_value_for_operator(self, a: str) -> int:
        return self.__get_lambda_constraint_value_for_operator(
            a, lambda it: sum(x**2 for x in it)
        )

    def __get_lambda_constraint_value_for_operator(
        self, a: str, aggregator: Callable[[Iterable], int]
    ) -> int:
        max_constraint_value = aggregator(
            self.constraints_values[constraint]
            for constraint in self.operators_constraints[a]
        )

        return max_constraint_value

    def __get_best_operator(self) -> str:
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

            if best_operator_performance == operator_performance:
                best_operator = self.__compute_tie_breaking(best_operator, operator)

        return best_operator

    def __compute_times_to_increment(self, operator: str) -> int:
        return max(
            1,
            min(
                self.constraints_values[constraint]
                for constraint in self.operators_constraints[operator]
            )
            // self.operators_costs[operator],
        )

    def _compute_post_hoc(self):
        self.__update_operators_with_simple_constraints()

        while any([value > 0 for value in self.constraints_values.values()]):
            best_operator = self.__get_best_operator()

            times_to_increment = self.__compute_times_to_increment(best_operator)

            self.operators_count[best_operator] += times_to_increment

            self._update_constraints_with_selected_operator(
                best_operator, times_to_increment
            )

    def __update_operators_with_simple_constraints(self):
        for constraint in self.constraints:
            if len(constraint) == 1:
                operator = constraint
                times_to_increment = ceil(
                    self.constraints_values[constraint] / self.operators_costs[operator]
                )
                self.operators_count[operator] = max(
                    self.operators_count[operator], times_to_increment
                )

        for operator in self.operators:
            self._update_constraints_with_selected_operator(
                operator, self.operators_costs[operator]
            )
