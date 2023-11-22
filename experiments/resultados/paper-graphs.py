#! /usr/bin/env python

import os
import project
from downward.reports.scatter import ScatterMatplotlib, ScatterPlotReport

from lab.experiment import Experiment

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

exp = Experiment('data/paper-graphs')

'''

exp = Experiment()

project.fetch_algorithm(exp, 'ff',          'main:01-ff-normal',                new_algo='ff')
project.fetch_algorithm(exp, 'red-black',   'main:01-red-black-normal',         new_algo='rb')
project.fetch_algorithm(exp, 'pho',         'main:04-pho2-ip-normal',           new_algo='sys2-ip')
project.fetch_algorithm(exp, 'pho',         'main:06-pho4-ip-normal',           new_algo='sys4-ip')
project.fetch_algorithm(exp, 'pho',         'main:01-pho2-lp-normal',           new_algo='sys2-lp')
project.fetch_algorithm(exp, 'pho',         'main:03-pho4-lp-normal',           new_algo='sys4-lp')
project.fetch_algorithm(exp, 'lsh-sys',     'main:02-lsh-sys2-normal',          new_algo='lsh-sys2')
project.fetch_algorithm(exp, 'lsh-sys',     'main:04-lsh-sys4-normal',          new_algo='lsh-sys4')
project.fetch_algorithm(exp, 'lsh-sys',     'main:06-lsh-sys4-limited-normal',  new_algo='lsh-sys4-limited')

project.fetch_algorithm(exp, 'ff',          'main:02-ff-one',                   new_algo='ff-one')
project.fetch_algorithm(exp, 'red-black',   'main:02-red-black-one',            new_algo='rb-one')
project.fetch_algorithm(exp, 'pho',         'main:10-pho2-ip-one',              new_algo='sys2-ip-one')
project.fetch_algorithm(exp, 'pho',         'main:12-pho4-ip-one',              new_algo='sys4-ip-one')
project.fetch_algorithm(exp, 'pho',         'main:07-pho2-lp-one',              new_algo='sys2-lp-one')
project.fetch_algorithm(exp, 'pho',         'main:09-pho4-lp-one',              new_algo='sys4-lp-one')
project.fetch_algorithm(exp, 'lsh-sys',     'main:08-lsh-sys2-one',             new_algo='lsh-sys2-one')
project.fetch_algorithm(exp, 'lsh-sys',     'main:10-lsh-sys4-one',             new_algo='lsh-sys4-one')
project.fetch_algorithm(exp, 'lsh-sys',     'main:12-lsh-sys4-limited-one',     new_algo='lsh-sys4-limited-one')
'''

'''
quality_filters = QualityFilters()
project.add_absolute_report(
    exp, attributes=ATTRIBUTES, filter=[project.add_evaluations_per_time, quality_filters.store_costs, quality_filters.add_quality]
)
'''


matplotlib_options = {
    
    "xtick.labelsize": 0,
    "ytick.labelsize": 0,

    "lines.markersize": 10,
    "lines.markeredgewidth": 0.1,
    "lines.linewidth": 1,  

    # Width and height in inches.
    "figure.figsize": [4, 4],
    "savefig.dpi": 100,
}

base_normal = ['lsh-sys4-limited', 'lsh-sys2']
algo_normal = [
    'ff', 'rb', 
    'sys2-ip', 'sys4-ip', 'sys2-lp', 'sys4-lp', 
    'lsh-sys2', 'lsh-sys4', 'lsh-sys4-limited'
]

base_one = ['lsh-sys4-limited-one', 'lsh-sys2-one']
algo_one = [
    'ff-one', 'rb-one', 
    'sys2-ip-one', 'sys4-ip-one', 'sys2-lp-one', 'sys4-lp-one', 
    'lsh-sys2-one', 'lsh-sys4-one', 'lsh-sys4-limited-one'
]

def aaaa(exp, base, algo):
    for algo_base in base:
        for algo_comp in algo:

            if algo_base == algo_comp:
                continue
            
            name = algo_base + '-vs-' + algo_comp

            exp.add_report(
                ScatterPlotReport(
                    attributes=[project.EVALUATIONS_PER_TIME],
                    filter=[project.add_evaluations_per_time],
                    filter_algorithm=[algo_base, algo_comp],
                    show_missing=False,
                    format="png",
                ),
                name=name + '-view',
            )

            exp.add_report(
                ScatterPlotReport(
                    attributes=[project.EVALUATIONS_PER_TIME],
                    filter=[project.add_evaluations_per_time],
                    filter_algorithm=[algo_base, algo_comp],
                    show_missing=False, title=" ", xlabel=" ", ylabel=" ",
                    matplotlib_options=matplotlib_options,
                    format='tex'
                ),
                name=name,
            )

aaaa(exp, base_normal,  algo_normal)
aaaa(exp, base_one,     algo_one)

exp.run_steps()