#! /usr/bin/env python

import os
import project

import suites

REPO = project.get_repo_base()
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]

SUITE = suites.suite_ipc11_sat()

ENV = project.LocalEnvironment(processes=8)

CONFIGS = [
    (f"{index:02d}-{h_nick}", ["--evaluator", f"eval={eval}", "--search", f"eager_greedy([{h}],  preferred=[eval], boost={boost}, cost_type={cost})"])
    for index, (h_nick, eval, h, boost, cost) in enumerate(
        [
            ("ls-with-ff-normal", "lsh(patterns=systematic(4), op_order=default, res_order=default, ff=true)", "eval", "0", "NORMAL"),
            ("ls-with-ff-one", "lsh(patterns=systematic(4), op_order=default, res_order=default, ff=true)", "eval", "0", "ONE"),
            ("ls-with-ff-pone", "lsh(patterns=systematic(4), op_order=default, res_order=default, ff=true)", "eval", "0", "PLUSONE"),
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
