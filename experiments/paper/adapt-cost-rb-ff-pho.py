#! /usr/bin/env python

import os
import project

import suites

REPO = project.get_repo_base()
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]

SUITE = suites.suite_ipc11_sat()

ENV = project.LocalEnvironment(processes=8)

CONFIGS = [
    (f"{index:02d}-{h_nick}", ["--search", f"eager_greedy([{h}], )"])
    for index, (h_nick, h) in enumerate(
        [
            ("ff-one", "ff(transform=adapt_costs(cost_type=ONE))"),
            ("ff-po", "ff(transform=adapt_costs(cost_type=PLUSONE))"),

            ("red-black-one", "RB(dag=from_coloring, extract_plan=true, transform=adapt_costs(cost_type=ONE))"),
            ("red-black-po", "RB(dag=from_coloring, extract_plan=true, transform=adapt_costs(cost_type=PLUSONE))"),
            
            ("pho2-lp-one", "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(2))], use_integer_operator_counts=false," +
                " transform=adapt_costs(cost_type=ONE))"),
            ("pho2-lp-po", "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(2))], use_integer_operator_counts=false," +
                " transform=adapt_costs(cost_type=PLUSONE))"),
            
            ("pho4-lp-one", "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(pattern_max_size=4, max_memory=4, reduce_patterns=true))]," +
                " use_integer_operator_counts=false, transform=adapt_costs(cost_type=ONE))"),
            ("pho4-lp-po", "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(pattern_max_size=4, max_memory=4, reduce_patterns=true))]," +
                " use_integer_operator_counts=false, transform=adapt_costs(cost_type=PLUSONE))"),
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

project.add_absolute_report(
    exp, attributes=ATTRIBUTES, filter=[project.add_evaluations_per_time]
)

exp.run_steps()
