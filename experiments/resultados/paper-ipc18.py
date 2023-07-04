#! /usr/bin/env python

import os
import project

import suites

from qualityfiters import QualityFilters

REPO = project.get_repo_base()
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]

SUITE = suites.suite_ff_or_rb_can_solve_and_lsh_not_or_the_opposite()

ENV = project.LocalEnvironment(processes=7)

CONFIGS = [
    (f"{index:02d}-{h_nick}", ["--search", f"eager_greedy([{h}])"])
    for index, (h_nick, h) in enumerate(
        [
        	("ff-normal", "ff(transform=adapt_costs(cost_type=NORMAL))"),

            ("lsh-sys2-normal", "lsh(patterns=systematic(2), transform=adapt_costs(cost_type=NORMAL))"),
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
