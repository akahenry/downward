#! /usr/bin/env python

import os
import project

import suites

from qualityfiters import QualityFilters

REPO = project.get_repo_base()
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]

SUITE = suites.suite_ipc14_sat_strips()

ENV = project.LocalEnvironment(processes=7)

CONFIGS = [
    (f"{index:02d}-{h_nick}", ["--search", f"eager_greedy([{h}])"])
    for index, (h_nick, h) in enumerate(
        [
        	("ff-normal", "ff(transform=adapt_costs(cost_type=NORMAL))"),
            ("ff-one", "ff(transform=adapt_costs(cost_type=ONE))"),

            ("red-black-normal", "RB(dag=from_coloring, extract_plan=true, transform=adapt_costs(cost_type=NORMAL))"),
            ("red-black-one", "RB(dag=from_coloring, extract_plan=true, transform=adapt_costs(cost_type=ONE))"),
            
            ("lsh-sys2-normal", "lsh(patterns=systematic(2), transform=adapt_costs(cost_type=NORMAL))"),
            ("lsh-sys2-normal", "lsh(patterns=systematic(2), transform=adapt_costs(cost_type=ONE))"),

            ("lsh-sys4-normal", "lsh(patterns=systematic(pattern_max_size=4, reduce_patterns=false, memory_percentage=1.0), transform=adapt_costs(cost_type=NORMAL))"),
            ("lsh-sys4-one", "lsh(patterns=systematic(pattern_max_size=4, reduce_patterns=false, memory_percentage=1.0), transform=adapt_costs(cost_type=ONE))"),

            ("lsh-sys4-limited-normal", "lsh(patterns=systematic(4), transform=adapt_costs(cost_type=NORMAL))"),
            ("lsh-sys4-limited-one", "lsh(patterns=systematic(4), transform=adapt_costs(cost_type=ONE))"),

            ("pho2-lp-normal", "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(2))], use_integer_operator_counts=false, transform=adapt_costs(cost_type=NORMAL))"),
            ("pho2-lp-one", "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(2))], use_integer_operator_counts=false, transform=adapt_costs(cost_type=ONE))"),

            ("pho2-ip-normal", "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(2))], use_integer_operator_counts=true, transform=adapt_costs(cost_type=NORMAL))"),
            ("pho2-ip-one", "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(2))], use_integer_operator_counts=true, transform=adapt_costs(cost_type=ONE))"),

            ("pho4-lp-normal", "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(4))], use_integer_operator_counts=false, transform=adapt_costs(cost_type=NORMAL))"),
            ("pho4-lp-one", "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(4))], use_integer_operator_counts=false, transform=adapt_costs(cost_type=ONE))"),

            ("pho4-ip-normal", "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(4))], use_integer_operator_counts=true, transform=adapt_costs(cost_type=NORMAL))"),
            ("pho4-ip-one", "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(4))], use_integer_operator_counts=true, transform=adapt_costs(cost_type=ONE))"),
        ],
        start=1,
    )
]

BUILD_OPTIONS = []
DRIVER_OPTIONS = ['--overall-time-limit', '30m', '--overall-memory-limit', '4096M']
REVS = [
    ("main", "main"),
]

ATTRIBUTES = [
    "error",
    "run_dir",
    "search_start_time",
    "search_start_memory",
    "total_time",
    "initial_h_value",
    "h_values",
    "coverage",
    "expansions",
    "memory",
    "plan_length",
    "restrictions",
    "operators",
    "cost",
    "quality",
    project.EVALUATIONS_PER_TIME,
]

exp = project.CommonExperiment(environment=ENV)
for config_nick, config in CONFIGS:
    for rev, rev_nick in REVS:
        algo_name = f"{rev_nick}:{config_nick}" if rev_nick else config_nick
        exp.add_algorithm(
            algo_name,
            REPO,
            rev,
            config,
            build_options=BUILD_OPTIONS,
            driver_options=DRIVER_OPTIONS,
        )
exp.add_suite(BENCHMARKS_DIR, SUITE)

# Add report steps.
quality_filters = QualityFilters()
project.add_absolute_report(
    exp, attributes=ATTRIBUTES, filter=[project.add_evaluations_per_time, quality_filters.store_costs, quality_filters.add_quality],
    #format='tex'
)

exp.run_steps()
