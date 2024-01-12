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
            ("lsh-sys1-normal", "lsh(patterns=systematic(pattern_max_size=1, reduce_patterns=false, memory_percentage=1.0), transform=adapt_costs(cost_type=NORMAL))"),
            ("lsh-sys2-normal", "lsh(patterns=systematic(pattern_max_size=2, reduce_patterns=false, memory_percentage=1.0), transform=adapt_costs(cost_type=NORMAL))"),
            ("lsh-sys3-normal", "lsh(patterns=systematic(pattern_max_size=3, reduce_patterns=false, memory_percentage=1.0), transform=adapt_costs(cost_type=NORMAL))"),
            ("lsh-sys4-normal", "lsh(patterns=systematic(pattern_max_size=4, reduce_patterns=false, memory_percentage=1.0), transform=adapt_costs(cost_type=NORMAL))"),
            ("lsh-sys3-limited-normal", "lsh(patterns=systematic(pattern_max_size=3), transform=adapt_costs(cost_type=NORMAL))"),
            ("lsh-sys4-limited-normal", "lsh(patterns=systematic(pattern_max_size=4), transform=adapt_costs(cost_type=NORMAL))"),

            ("lsh-sys1-one", "lsh(patterns=systematic(pattern_max_size=1, reduce_patterns=false, memory_percentage=1.0), transform=adapt_costs(cost_type=ONE))"),
            ("lsh-sys2-one", "lsh(patterns=systematic(pattern_max_size=2, reduce_patterns=false, memory_percentage=1.0), transform=adapt_costs(cost_type=ONE))"),
            ("lsh-sys3-one", "lsh(patterns=systematic(pattern_max_size=3, reduce_patterns=false, memory_percentage=1.0), transform=adapt_costs(cost_type=ONE))"),
            ("lsh-sys4-one", "lsh(patterns=systematic(pattern_max_size=4, reduce_patterns=false, memory_percentage=1.0), transform=adapt_costs(cost_type=ONE))"),
            ("lsh-sys3-limited-one", "lsh(patterns=systematic(pattern_max_size=3), transform=adapt_costs(cost_type=ONE))"),
            ("lsh-sys4-limited-one", "lsh(patterns=systematic(pattern_max_size=4), transform=adapt_costs(cost_type=ONE))"),

            ("lsh-sys1-plusone", "lsh(patterns=systematic(pattern_max_size=1, reduce_patterns=false, memory_percentage=1.0), transform=adapt_costs(cost_type=PLUSONE))"),
            ("lsh-sys2-plusone", "lsh(patterns=systematic(pattern_max_size=2, reduce_patterns=false, memory_percentage=1.0), transform=adapt_costs(cost_type=PLUSONE))"),
            ("lsh-sys3-plusone", "lsh(patterns=systematic(pattern_max_size=3, reduce_patterns=false, memory_percentage=1.0), transform=adapt_costs(cost_type=PLUSONE))"),
            ("lsh-sys4-plusone", "lsh(patterns=systematic(pattern_max_size=4, reduce_patterns=false, memory_percentage=1.0), transform=adapt_costs(cost_type=PLUSONE))"),
            ("lsh-sys3-limited-plusone", "lsh(patterns=systematic(pattern_max_size=3), transform=adapt_costs(cost_type=PLUSONE))"),
            ("lsh-sys4-limited-plusone", "lsh(patterns=systematic(pattern_max_size=4), transform=adapt_costs(cost_type=PLUSONE))"),
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
