#! /usr/bin/env python

import os
import project

import suites

REPO = project.get_repo_base()
BENCHMARKS_DIR = os.environ["DOWNWARD_BENCHMARKS"]

SUITE = suites.hstar_instances()

ENV = project.LocalEnvironment(processes=7)

CONFIGS = [
    (f"{index:02d}-{h_nick}", ["--search", f"eager_greedy([{h}])"])
    for index, (h_nick, h) in enumerate(
        [
            ("h*", "pdb(manual_pattern([]))"),
            
            ("ff", "ff()"),
            ("red-black", "hrb=RB(dag=from_coloring, extract_plan=true)"),

            ("lm-cut", "lmcut()"),
            ("blind", "blind()"),
            ("cpdbs", "cpdbs(patterns=systematic(4))"),
            
            ("ls-dd", "lsh(patterns=systematic(2), op_order=default, res_order=default)"),

            ("ls-dd", "lsh(patterns=systematic(4), op_order=default, res_order=default)"),
            ("ls-ds", "lsh(patterns=systematic(4), op_order=default, res_order=sort)"),
            ("ls-dr", "lsh(patterns=systematic(4), op_order=default, res_order=random)"),
            ("ls-dr-10", "lsh(patterns=systematic(4), n=10, op_order=default, res_order=random)"),

            ("ls-sd", "lsh(patterns=systematic(4), op_order=sort, res_order=default)"),
            ("ls-ss", "lsh(patterns=systematic(4), op_order=sort, res_order=sort)"),
            ("ls-sr", "lsh(patterns=systematic(4), op_order=sort, res_order=random)"),
            ("ls-sr-10", "lsh(patterns=systematic(4), n=10, op_order=sort, res_order=random)"),

            ("ls-rd", "lsh(patterns=systematic(4), op_order=random, res_order=default)"),
            ("ls-rs", "lsh(patterns=systematic(4), op_order=random, res_order=sort)"),
            ("ls-rr", "lsh(patterns=systematic(4), op_order=random, res_order=random)"),
            ("ls-rr-10", "lsh(patterns=systematic(4), n=10, op_order=random, res_order=random)"),

            ("pho2-LP", "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(2))], use_integer_operator_counts=false)"),
            ("pho2-IP", "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(2))], use_integer_operator_counts=true)"),

            ("pho4-LP", "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(4))], use_integer_operator_counts=false)"),
            ("pho4-IP", "operatorcounting(constraint_generators=[pho_constraints(patterns=systematic(4))], use_integer_operator_counts=true)"),
            
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
