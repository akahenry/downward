from operator_count_heuristic import OperatorCountHeuristic

class LocalSearchHeuristic(OperatorCountHeuristic):
    def _compute_operator_count(self):
        for constraint in self.constraints.keys():
            var = 0 
            while self.constraints[constraint] > 0:
                operator = constraint[var]
                self.operators_count[operator] += 1

                for other in self.operators_constraints[operator]:
                    if self.constraints[other] > 0:
                        self.constraints[other] -= self.operators_costs[operator]
                
                var = (var + 1) % len(constraint)