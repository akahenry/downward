#! /usr/bin/env python

import os
import project

import suites

REPO = project.get_repo_base()
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]

SUITE = suites.suite_ipc11_sat()

ENV = project.LocalEnvironment(processes=7)

CONFIGS = [
    (f"{index:02d}-{h_nick}", ["--search", f"eager_greedy([{h}])"])
    for index, (h_nick, h) in enumerate(
        [
            ("ISS1", "lsh(patterns=systematic(4), n=1, decrement=iterative, op_order=sort, res_order=sort)"),
            ("ISD1", "lsh(patterns=systematic(4), n=1, decrement=iterative, op_order=sort, res_order=default)"),
            ("ISR1", "lsh(patterns=systematic(4), n=1, decrement=iterative, op_order=sort, res_order=random)"),
            ("ISR10", "lsh(patterns=systematic(4), n=10, decrement=iterative, op_order=sort, res_order=random)"),

            ("IDS1", "lsh(patterns=systematic(4), n=1, decrement=iterative, op_order=default, res_order=sort)"),
            ("IDD1", "lsh(patterns=systematic(4), n=1, decrement=iterative, op_order=default, res_order=default)"),
            ("IDR1", "lsh(patterns=systematic(4), n=1, decrement=iterative, op_order=default, res_order=random)"),
            ("IDR10", "lsh(patterns=systematic(4), n=10, decrement=iterative, op_order=default, res_order=random)"),

            ("IRS1", "lsh(patterns=systematic(4), n=1, decrement=iterative, op_order=random, res_order=sort)"),
            ("IRD1", "lsh(patterns=systematic(4), n=1, decrement=iterative, op_order=random, res_order=default)"),
            ("IRR1", "lsh(patterns=systematic(4), n=1, decrement=iterative, op_order=random, res_order=random)"),

            ("IRS10", "lsh(patterns=systematic(4), n=10, decrement=iterative, op_order=random, res_order=sort)"),
            ("IRD10", "lsh(patterns=systematic(4), n=10, decrement=iterative, op_order=random, res_order=default)"),
            ("IRR10", "lsh(patterns=systematic(4), n=10, decrement=iterative, op_order=random, res_order=random)"),

            ("BSS1", "lsh(patterns=systematic(4), n=1, decrement=before, op_order=sort, res_order=sort)"),
            ("BSD1", "lsh(patterns=systematic(4), n=1, decrement=before, op_order=sort, res_order=default)"),
            ("BSR1", "lsh(patterns=systematic(4), n=1, decrement=before, op_order=sort, res_order=random)"),
            ("BSR10", "lsh(patterns=systematic(4), n=10, decrement=before, op_order=sort, res_order=random)"),

            ("BDS1", "lsh(patterns=systematic(4), n=1, decrement=before, op_order=default, res_order=sort)"),
            ("BDD1", "lsh(patterns=systematic(4), n=1, decrement=before, op_order=default, res_order=default)"),
            ("BDR1", "lsh(patterns=systematic(4), n=1, decrement=before, op_order=default, res_order=random)"),
            ("BDR10", "lsh(patterns=systematic(4), n=10, decrement=before, op_order=default, res_order=random)"),

            ("BRS1", "lsh(patterns=systematic(4), n=1, decrement=before, op_order=random, res_order=sort)"),
            ("BRD1", "lsh(patterns=systematic(4), n=1, decrement=before, op_order=random, res_order=default)"),
            ("BRR1", "lsh(patterns=systematic(4), n=1, decrement=before, op_order=random, res_order=random)"),

            ("BRS10", "lsh(patterns=systematic(4), n=10, decrement=before, op_order=random, res_order=sort)"),
            ("BRD10", "lsh(patterns=systematic(4), n=10, decrement=before, op_order=random, res_order=default)"),
            ("BRR10", "lsh(patterns=systematic(4), n=10, decrement=before, op_order=random, res_order=random)"),
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
