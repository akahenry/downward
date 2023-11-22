#! /usr/bin/env python

import os
import project

import suites

from qualityfiters import QualityFilters

REPO = project.get_repo_base()
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]

SUITE = suites.hstar_instances()

ENV = project.LocalEnvironment(processes=7)

CONFIGS = [
    (f"{index:02d}-{h_nick}", ["--search", f"eager_greedy([{h}])"])
    for index, (h_nick, h) in enumerate(
        [
            ("h*", "pdb(manual_pattern([]))"),
            ("lsh2", "lsh(patterns=systematic(2))"),
            ("lsh4", "lsh(patterns=systematic(4))"),
            ("lsh4r", "lsh(patterns=systematic(4), res_order=random)"),
            ("lsh4r10", "lsh(patterns=systematic(4), res_order=random, n=10)"),
            ("pho2-lp", "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(2))], use_integer_operator_counts=false)"),
            ("pho2-ip", "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(2))], use_integer_operator_counts=true)"),
            ("pho4-lp", "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(4))], use_integer_operator_counts=false)"),
            ("pho4-ip", "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(4))], use_integer_operator_counts=true)"),
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
    "mean_mentions",
    "mean_operators",
    "lazy_values",
    "eager_values",
    "min_lowerbound",
    "mean_lowerbound",
    "max_lowerbound",
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
