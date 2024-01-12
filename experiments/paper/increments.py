#! /usr/bin/env python

import os
import project

import suites

REPO = project.get_repo_base()
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]

SUITE = suites.suite_ipc11_sat()

ENV = project.LocalEnvironment(processes=8)

CONFIGS = [
    (f"{index:02d}-{h_nick}", ["--search", f"eager_greedy([{h}])"])
    for index, (h_nick, h) in enumerate(
        [
            ("lsh-DD", "lsh(patterns=systematic(4), n=1, op_order=default, res_order=default)"),
            ("lsh-DS", "lsh(patterns=systematic(4), n=1, op_order=default, res_order=sort)"),
            ("lsh-DR-1", "lsh(patterns=systematic(4), n=1, op_order=default, res_order=random)"),
            ("lsh-DR-10", "lsh(patterns=systematic(4), n=10, op_order=default, res_order=random)"),

            ("lsh-SD", "lsh(patterns=systematic(4), n=1, op_order=sort, res_order=default)"),
            ("lsh-SS", "lsh(patterns=systematic(4), n=1, op_order=sort, res_order=sort)"),
            ("lsh-SR-1", "lsh(patterns=systematic(4), n=1, op_order=sort, res_order=random)"),
            ("lsh-SR-10", "lsh(patterns=systematic(4), n=10, op_order=sort, res_order=random)"),

            ("lsh-RD-1", "lsh(patterns=systematic(4), n=1, op_order=random, res_order=default)"),
            ("lsh-RS-1", "lsh(patterns=systematic(4), n=1, op_order=random, res_order=sort)"),
            ("lsh-RR-1", "lsh(patterns=systematic(4), n=1, op_order=random, res_order=random)"),

            ("lsh-RD-10", "lsh(patterns=systematic(4), n=10, op_order=random, res_order=default)"),
            ("lsh-RS-10", "lsh(patterns=systematic(4), n=10, op_order=random, res_order=sort)"),
            ("lsh-RR-10", "lsh(patterns=systematic(4), n=10, op_order=random, res_order=random)"),
        ],
        start=1,
    )
]

BUILD_OPTIONS = []
DRIVER_OPTIONS = ['--overall-time-limit', '30m', '--overall-memory-limit', '4096M']
REVS = [
    ("stats", "stats"),
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
    "increments",
    "eval_res",
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
