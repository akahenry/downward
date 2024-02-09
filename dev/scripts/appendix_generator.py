import json

metrics = {
    "evaluations": {"name": "Evaluations"},
    "expansions": {"name": "Expansions"},
    "initial_h_value": {"name": "$h(s_0)$-value"},
    "plan_length": {"name": "$\\pi$"},
    "cost": {"name": "$cost(\\pi)$"},
    "total_time": {"name": "Total time"},
}

## TODO: We are grouping sys4 and sys2, which is wrong. We should fix it.

algorithms = {
    "tcc:09-ilsh-sys4-normal": {
        "name": "$h^{pho}_{ilsh}$",
        "type": "Normal",
        "patterns": 4,
    },
    "tcc:12-pho-lp-sys2-one": {
        "name": "$h^{pho}_{LP}$",
        "type": "Unitary",
        "patterns": 2,
    },
    "tcc:10-ilsh-sys4-one": {
        "name": "$h^{pho}_{ilsh}$",
        "type": "Unitary",
        "patterns": 4,
    },
    "tcc:02-hstar-one": {"name": "$h^*$", "type": "Unitary"},
    "tcc:07-ilsh-sys2-normal": {
        "name": "$h^{pho}_{ilsh}$",
        "type": "Normal",
        "patterns": 2,
    },
    "tcc:13-pho-lp-sys4-normal": {
        "name": "$h^{pho}_{LP}$",
        "type": "Normal",
        "patterns": 4,
    },
    "tcc:06-lsh-sys4-one": {
        "name": "$h^{pho}_{lsh}$",
        "type": "Unitary",
        "patterns": 4,
    },
    "tcc:11-pho-lp-sys2-normal": {
        "name": "$h^{pho}_{LP}$",
        "type": "Normal",
        "patterns": 2,
    },
    "tcc:08-ilsh-sys2-one": {
        "name": "$h^{pho}_{ilsh}$",
        "type": "Unitary",
        "patterns": 2,
    },
    "tcc:16-pho-ip-sys2-one": {"name": "$h^{pho}$", "type": "Unitary", "patterns": 2},
    "tcc:17-pho-ip-sys4-normal": {"name": "$h^{pho}$", "type": "Normal", "patterns": 4},
    "tcc:01-hstar-normal": {"name": "$h^*$", "type": "Normal"},
    "tcc:18-pho-ip-sys4-one": {"name": "$h^{pho}$", "type": "Unitary", "patterns": 4},
    "tcc:05-lsh-sys4-normal": {
        "name": "$h^{pho}_{lsh}$",
        "type": "Normal",
        "patterns": 4,
    },
    "tcc:03-lsh-sys2-normal": {
        "name": "$h^{pho}_{lsh}$",
        "type": "Normal",
        "patterns": 2,
    },
    "tcc:14-pho-lp-sys4-one": {
        "name": "$h^{pho}_{LP}$",
        "type": "Unitary",
        "patterns": 4,
    },
    "tcc:04-lsh-sys2-one": {
        "name": "$h^{pho}_{lsh}$",
        "type": "Unitary",
        "patterns": 2,
    },
    "tcc:15-pho-ip-sys2-normal": {"name": "$h^{pho}$", "type": "Normal", "patterns": 2},
}

algorithm_order = [
    "$h^*$",
    "$h^{pho}_{lsh}$",
    "$h^{pho}_{ilsh}$",
    "$h^{pho}_{LP}$",
    "$h^{pho}$",
]

with open("properties.json") as file:
    properties = json.load(file)

domains_by_metric = {metric: {} for metric in metrics.keys()}

for instance in properties.values():
    algorithm = algorithms[instance["algorithm"]]["name"]
    cost_type = algorithms[instance["algorithm"]]["type"]
    patterns = (
        [str(algorithms[instance["algorithm"]]["patterns"])]
        if "patterns" in algorithms[instance["algorithm"]]
        else ["2", "4"]
    )
    domain = instance["domain"]
    problem = instance["problem"]
    for metric in metrics.keys():
        if domain not in domains_by_metric[metric]:
            domains_by_metric[metric][domain] = {}

        if cost_type not in domains_by_metric[metric][domain]:
            domains_by_metric[metric][domain][cost_type] = {}

        for pattern in patterns:
            if pattern not in domains_by_metric[metric][domain][cost_type]:
                domains_by_metric[metric][domain][cost_type][pattern] = {}

            if problem not in domains_by_metric[metric][domain][cost_type][pattern]:
                domains_by_metric[metric][domain][cost_type][pattern][problem] = {}

            if (
                algorithm
                not in domains_by_metric[metric][domain][cost_type][pattern][problem]
            ):
                domains_by_metric[metric][domain][cost_type][pattern][problem][
                    algorithm
                ] = {}

            domains_by_metric[metric][domain][cost_type][pattern][problem][
                algorithm
            ] = instance[metric]

string = """\extrafloats{1000}
\maxdeadcycles=500
\chapter{Appendix}
"""

first = True
biggest_problem = None
biggest_problem_number = 0

for metric, domain_dict in domains_by_metric.items():
    metric = metrics[metric]["name"]

    # string += f"\section{{{metric}}}\n"

    for domain, cost_type_dict in domain_dict.items():
        # string += f"\subsection{{{domain}}}\n\n"

        for cost_type, pattern_dict in cost_type_dict.items():
            for pattern, problem_dict in pattern_dict.items():
                if len(problem_dict) > biggest_problem_number:
                    biggest_problem_number = len(problem_dict)
                    biggest_problem = domain
                # string += f"\subsubsection{{{cost_type}-\\textit{{sys{pattern}}}}}\n\n"

                string += f"""
\\begin{{longtable}}{{l|r|rrrr}}
\caption*{{{metric}-\\textit{{{domain}}}-{cost_type}-\\textit{{sys{pattern}}}}} \\\\
    {metric} & {" & ".join(algorithm_order)} \\\\
    \midrule
"""

                for problem, algorithm_dict in problem_dict.items():
                    string += f"    {problem} & {' & '.join([str(algorithm_dict[algorithm]) for algorithm in algorithm_order])} \\\\\n"
                string = string[:-3] + "\n"

                string += f"""\\end{{longtable}}
"""


with open("test.tex", "w") as file:
    file.write(string)

print(biggest_problem)
print(biggest_problem_number)
