#! /usr/bin/env python

import os
import project

import suites

from qualityfiters import QualityFilters

REPO = project.get_repo_base()
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]

SUITE = suites.hstar_instances()

ENV = project.LocalEnvironment(processes=6)

CONFIGS = [
    (f"{index:02d}-{h_nick}", ["--search", f"eager_greedy([{h}])"])
    for index, (h_nick, h) in enumerate(
        [
            (
                "lsh-sys2-normal",
                "lsh(patterns=systematic(2), transform=adapt_costs(cost_type=NORMAL))",
            ),
            (
                "lsh-sys2-one",
                "lsh(patterns=systematic(2), transform=adapt_costs(cost_type=ONE))",
            ),
            (
                "lsh-sys4-normal",
                "lsh(patterns=systematic(4), transform=adapt_costs(cost_type=NORMAL))",
            ),
            (
                "lsh-sys4-one",
                "lsh(patterns=systematic(4), transform=adapt_costs(cost_type=ONE))",
            ),
            (
                "ilsh-sys2-normal",
                "ilsh(patterns=systematic(2), transform=adapt_costs(cost_type=NORMAL))",
            ),
            (
                "ilsh-sys2-one",
                "ilsh(patterns=systematic(2), transform=adapt_costs(cost_type=ONE))",
            ),
            (
                "ilsh-sys4-normal",
                "ilsh(patterns=systematic(4), transform=adapt_costs(cost_type=NORMAL))",
            ),
            (
                "ilsh-sys4-one",
                "ilsh(patterns=systematic(4), transform=adapt_costs(cost_type=ONE))",
            ),
            (
                "pho-lp-sys2-normal",
                "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(2))], use_integer_operator_counts=false, transform=adapt_costs(cost_type=NORMAL))",
            ),
            (
                "pho-lp-sys2-one",
                "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(2))], use_integer_operator_counts=false, transform=adapt_costs(cost_type=ONE))",
            ),
            (
                "pho-lp-sys4-normal",
                "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(4))], use_integer_operator_counts=false, transform=adapt_costs(cost_type=NORMAL))",
            ),
            (
                "pho-lp-sys4-one",
                "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(4))], use_integer_operator_counts=false, transform=adapt_costs(cost_type=ONE))",
            ),
            (
                "pho-ip-sys2-normal",
                "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(2))], use_integer_operator_counts=true, transform=adapt_costs(cost_type=NORMAL))",
            ),
            (
                "pho-ip-sys2-one",
                "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(2))], use_integer_operator_counts=true, transform=adapt_costs(cost_type=ONE))",
            ),
            (
                "pho-ip-sys4-normal",
                "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(4))], use_integer_operator_counts=true, transform=adapt_costs(cost_type=NORMAL))",
            ),
            (
                "pho-ip-sys4-one",
                "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(4))], use_integer_operator_counts=true, transform=adapt_costs(cost_type=ONE))",
            ),
        ],
        start=1,
    )
]

BUILD_OPTIONS = []
DRIVER_OPTIONS = ["--overall-time-limit", "30m", "--overall-memory-limit", "2048M"]
REVS = [
    ("tcc", "tcc"),
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
    exp,
    attributes=ATTRIBUTES,
    filter=[
        project.add_evaluations_per_time,
        quality_filters.store_costs,
        quality_filters.add_quality,
    ],
    # format='tex'
)

exp.run_steps()
