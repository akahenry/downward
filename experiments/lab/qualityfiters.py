
from collections import defaultdict

class QualityFilters:
    """Compute the IPC quality score.
    >>> from downward.reports.absolute import AbsoluteReport
    >>> filters = QualityFilters()
    >>> report = AbsoluteReport(filter=[filters.store_costs, filters.add_quality])
    """

    def __init__(self):
        self.tasks_to_costs = defaultdict(list)

    def _get_task(self, run):
        return (run["domain"], run["problem"])

    def _compute_quality(self, cost, all_costs):
        if cost is None:
            return 0.0
        assert all_costs
        min_cost = min(all_costs)
        if cost == 0:
            assert min_cost == 0
            return 1.0
        return min_cost / cost

    def store_costs(self, run):
        cost = run.get("cost")
        if cost is not None:
            assert run["coverage"]
            self.tasks_to_costs[self._get_task(run)].append(cost)
        return True

    def add_quality(self, run):
        run["quality"] = self._compute_quality(
            run.get("cost"), self .tasks_to_costs[self._get_task(run)]
        )
        return run