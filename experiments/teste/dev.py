#! /usr/bin/env python

import os
import project

import suites

REPO = project.get_repo_base()
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]

SUITE = [
        'barman-sat11-strips',
        #'elevators-sat11-strips',
        #'floortile-sat11-strips',
        'nomystery-sat11-strips',
        #'openstacks-sat11-strips',
        #'parcprinter-sat11-strips',
        'parking-sat11-strips',
        'pegsol-sat11-strips',
        'scanalyzer-sat11-strips',
        'sokoban-sat11-strips',
        'tidybot-sat11-strips',
        #'transport-sat11-strips',
        'visitall-sat11-strips',
        'woodworking-sat11-strips',
    ]

ENV = project.LocalEnvironment(processes=7)

CONFIGS = [
    (f"{index:02d}-{h_nick}", ["--search", f"eager_greedy([{h}])"])
    for index, (h_nick, h) in enumerate(
        [
            ('lsh', 'lsh(patterns=systematic(4), n=1)')
        ],
        start=1,
    )
]

BUILD_OPTIONS = []
DRIVER_OPTIONS = ["--overall-time-limit", "30m", "--overall-memory-limit", "4094M"]
REVS = [
    ("sys-random", "sys-random"),
    ("sys-first", "sys-first"),
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
