#! /usr/bin/env python

import os
import project

import suites

REPO = project.get_repo_base()
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]

SUITE = suites.suite_ipc11_sat()

ENV = project.LocalEnvironment(processes=8)

CONFIGS = [
    (f"{index:02d}-{h_nick}", ["--evaluator", f"eval={eval}", "--search", f"eager_greedy([{h}],  preferred=[eval], boost={boost}, cost_type=ONE)"])
    for index, (h_nick, eval, h, boost) in enumerate(
        [
            ("ff-0", "ff()", "eval", "0"),
            ("ls-0", "lsh(patterns=systematic(4), op_order=default, res_order=default, preferred=true)", "eval", "0"),

            ("ff-ls-0", "ff()", "lsh(patterns=systematic(4), op_order=default, res_order=default)", "0"),
            ("ls-ff-0", "lsh(patterns=systematic(4), op_order=default, res_order=default, preferred=true)", "ff()", "0"),
            
            ("ff-1000", "ff()", "eval", "1000"),
            ("ls-1000", "lsh(patterns=systematic(4), op_order=default, res_order=default, preferred=true)", "eval", "1000"),

            ("ff-ls-1000", "ff()", "lsh(patterns=systematic(4), op_order=default, res_order=default)", "1000"),
            ("ls-ff-1000", "lsh(patterns=systematic(4), op_order=default, res_order=default, preferred=true)", "ff()", "1000"),
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
