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


project.fetch_algorithm(exp, 'melhor', 'melhor:01-ls2.1', new_algo='mv3.1')
project.fetch_algorithm(exp, 'teste', 'old:01-ls2.1', new_algo='ov3.1')
project.fetch_algorithm(exp, 'teste', 'new:01-ls2.1', new_algo='nv3.1')

project.fetch_algorithm(exp, 'melhor', 'melhor:02-ls2.5', new_algo='mv3.5')
project.fetch_algorithm(exp, 'teste', 'old:02-ls2.5', new_algo='ov3.5')
project.fetch_algorithm(exp, 'teste', 'new:02-ls2.5', new_algo='nv3.5')

project.fetch_algorithm(exp, 'melhor', 'melhor:03-ls2.10', new_algo='mv3.10')
project.fetch_algorithm(exp, 'teste', 'old:03-ls2.10', new_algo='ov3.10')
project.fetch_algorithm(exp, 'teste', 'new:03-ls2.10', new_algo='nv3.10')











#project.fetch_algorithm(exp, '', '', new_algo='')

project.add_absolute_report(
    exp, attributes=ATTRIBUTES, filter=[project.add_evaluations_per_time]
)


exp.run_steps()



