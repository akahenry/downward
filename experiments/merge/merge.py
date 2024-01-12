#! /usr/bin/env python

import os
import project

from lab.experiment import Experiment

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

exp = Experiment()


#project.fetch_algorithm(exp, 'ff-pho', 'main:01-pho2', new_algo='pho2')
project.fetch_algorithm(exp, 'ff-sat', 'main:02-ff', new_algo='ff')

project.fetch_algorithm(exp, 'sys2-sat', 'main:01-ls2-1', new_algo='ls2-1')
#project.fetch_algorithm(exp, 'sys2-sat', 'main:02-ls2-5', new_algo='ls2-5')
#project.fetch_algorithm(exp, 'sys2-sat', 'main:03-ls2-10', new_algo='ls2-10')

project.fetch_algorithm(exp, 'sys3-sat', 'main:01-ls3-1', new_algo='ls3-1')
#project.fetch_algorithm(exp, 'sys3-sat', 'main:02-ls3-5', new_algo='ls3-5')
#project.fetch_algorithm(exp, 'sys3-sat', 'main:03-ls3-10', new_algo='ls3-10')

project.fetch_algorithm(exp, 'multi-sat', 'fisrt:01-1', new_algo='multipdb')

project.fetch_algorithm(exp, 'rb-sat', 'master:01-red-black', new_algo='red-black')

#project.fetch_algorithm(exp, '', '', new_algo='')

project.add_absolute_report(
    exp, attributes=ATTRIBUTES, filter=[project.add_evaluations_per_time]
)

exp.run_steps()



