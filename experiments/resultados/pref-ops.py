#! /usr/bin/env python

import os
import project

import suites

REPO = project.get_repo_base()
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]

SUITE = ["gripper:prob01.pddl"]# suites.suite_ipc11_sat()

ENV = project.LocalEnvironment(processes=2)

CONFIGS = [
    (f"{index:02d}-{h_nick}", ["--evaluator", f"eval={eval}", "--search", f"eager_greedy([{h}], preferred=[eval])"])
    for index, (h_nick, eval, h) in enumerate(
        [
            ("pref-ff-normal", "ff(transform=adapt_costs(cost_type=NORMAL))", "eval"),
            ("pref-ls-normal", "lsh(patterns=systematic(4), preferred=true, transform=adapt_costs(cost_type=NORMAL))", "eval"),
            ("pref-ff-ls-normal", "ff()", "lsh(patterns=systematic(4), transform=adapt_costs(cost_type=NORMAL))"),
            ("pref-ls-ff-normal", "lsh(patterns=systematic(4), preferred=true)", "ff(transform=adapt_costs(cost_type=NORMAL))"),

            ("pref-ff-one", "ff(transform=adapt_costs(cost_type=ONE))", "eval"),
            ("pref-ls-one", "lsh(patterns=systematic(4), preferred=true, transform=adapt_costs(cost_type=ONE))", "eval"),
            ("pref-ff-ls-one", "ff()", "lsh(patterns=systematic(4), transform=adapt_costs(cost_type=ONE))"),
            ("pref-ls-ff-one", "lsh(patterns=systematic(4), preferred=true)", "ff(transform=adapt_costs(cost_type=ONE))"),

            ("pref-ff-plusone", "ff(transform=adapt_costs(cost_type=PLUSONE))", "eval"),
            ("pref-ls-plusone", "lsh(patterns=systematic(4), preferred=true, transform=adapt_costs(cost_type=PLUSONE))", "eval"),
            ("pref-ff-ls-plusone", "ff()", "lsh(patterns=systematic(4), transform=adapt_costs(cost_type=PLUSONE))"),
            ("pref-ls-ff-plusone", "lsh(patterns=systematic(4), preferred=true)", "ff(transform=adapt_costs(cost_type=PLUSONE))"),
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
