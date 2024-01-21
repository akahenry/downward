from greedy_local_search_heuristic import GreedyLocalSearchHeuristic


class ImprovedLocalSearchHeuristic(GreedyLocalSearchHeuristic):
    def _compute_operator_performance(self, operator: str) -> float:
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

    def _compute_times_to_increment(self, operator: str) -> int:
        return max(
            1,
            min(
                self.constraints_values[constraint]
                for constraint in self.operators_constraints[operator]
            )
            // self.operators_costs[operator],
        )
