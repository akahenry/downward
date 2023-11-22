#! /usr/bin/env python

import os
import project

from downward.reports.absolute import AbsoluteReport
from downward.reports.scatter import ScatterMatplotlib, ScatterPlotReport
from downward.reports.compare import ComparativeReport
from downward.reports import Attribute

from lab.experiment import Experiment
from lab.reports.filter import FilterReport
from lab import reports

from plan import MeuPlotReport

from qualityfiters import QualityFilters


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
    "cost",
    "quality",
    project.EVALUATIONS_PER_TIME,
]

exp = Experiment()

'''
    SAT 11, SAT 14, SAT 18 (remove all domains with conditional effects and axioms).
    
    NORMAL: FF, RB, SYS2-LP, SYS2-IP, SYS4-LP, SYS4-IP, LSH, SYS4 completo LSH
    ONE: FF, RB, SYS2-LP, SYS2-IP, SYS4-LP, SYS4-IP, LSH, SYS4 completo LSH
'''

project.fetch_algorithm(exp, 'ff',          'main:02-ff-one',                   new_algo='1.ff')
project.fetch_algorithm(exp, 'red-black',   'main:02-red-black-one',            new_algo='2.rb')
project.fetch_algorithm(exp, 'pho',         'main:10-pho2-ip-one',              new_algo='3.sys2-ip')
project.fetch_algorithm(exp, 'pho',         'main:12-pho4-ip-one',              new_algo='4.sys4-ip')
project.fetch_algorithm(exp, 'pho',         'main:07-pho2-lp-one',              new_algo='5.sys2-lp')
project.fetch_algorithm(exp, 'pho',         'main:09-pho4-lp-one',              new_algo='6.sys4-lp')
project.fetch_algorithm(exp, 'lsh-sys',     'main:08-lsh-sys2-one',             new_algo='7.lsh-sys2')
project.fetch_algorithm(exp, 'lsh-sys',     'main:10-lsh-sys4-one',             new_algo='8.lsh-sys4')
project.fetch_algorithm(exp, 'lsh-sys',     'main:12-lsh-sys4-limited-one',     new_algo='9.lsh-sys4-limited')

# Add report steps.
quality_filters = QualityFilters()
project.add_absolute_report(
    exp, attributes=ATTRIBUTES, filter=[project.add_evaluations_per_time, quality_filters.store_costs, quality_filters.add_quality],
    #format='tex'
)

exp.run_steps()

exit()
