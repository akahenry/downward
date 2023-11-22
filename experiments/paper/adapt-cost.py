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
            ("normal", "lsh(patterns=systematic(pattern_max_size=4, max_memory=4, reduce_patterns=true), n=1," +
                        "decrement=iterative, op_order=default, res_order=default, transform=adapt_costs(cost_type=NORMAL))"),
            ("one", "lsh(patterns=systematic(pattern_max_size=4, max_memory=4, reduce_patterns=true), n=1," +
                        "decrement=iterative, op_order=default, res_order=default, transform=adapt_costs(cost_type=ONE))"),
            ("plus-one", "lsh(patterns=systematic(pattern_max_size=4, max_memory=4, reduce_patterns=true), n=1," +
                        "decrement=iterative, op_order=default, res_order=default, transform=adapt_costs(cost_type=PLUSONE))"),
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
