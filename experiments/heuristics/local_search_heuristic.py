from operator_count_heuristic import OperatorCountHeuristic


class LocalSearchHeuristic(OperatorCountHeuristic):
    def _compute_operator_count(self):
        for constraint in self.constraints_values.keys():
            var = 0
            while self.constraints_values[constraint] > 0:
                operator = constraint[var]
                self.operators_count[operator] += 1

                self._update_constraints_with_selected_operator(operator)

                var = (var + 1) % len(constraint)
