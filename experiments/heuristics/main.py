from itertools import permutations

from local_search_heuristic import LocalSearchHeuristic

operators = ['a', 'b', 'c']

# key: operator, value: cost
operators_costs = {
    'a': 1,
    'b': 1,
    'c': 1
}

# key: operators, value: lower bound
constraints = [ 
    ('a', 1),
    ('b', 1),
    ('c', 1),
    ('ab', 6),
    ('ac', 6),
    ('bc', 6),
]

constraint_permutations = permutations(constraints, len(constraints))

results = dict()

for perm in constraint_permutations: 
    constraints = dict(zip([k[0] for k in perm],  [v[1] for v in perm]))
    
    heuristic = LocalSearchHeuristic(operators, operators_costs, constraints)
    results[perm] = heuristic.compute()


results = {k: v for k, v in sorted(results.items(), key = lambda item: item[1])}

