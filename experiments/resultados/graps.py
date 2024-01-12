#! /usr/bin/env python

import os
import project
from downward.reports.scatter import ScatterMatplotlib, ScatterPlotReport

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


project.fetch_algorithm(exp, 'merge-normal', 'ff', new_algo='ff-normal')
project.fetch_algorithm(exp, 'merge-normal', 'red-black', new_algo='rb-normal')
project.fetch_algorithm(exp, 'merge-normal', 'ls4-dd', new_algo='ls-normal')

project.fetch_algorithm(exp, 'merge-one', 'ff', new_algo='ff-one')
project.fetch_algorithm(exp, 'merge-one', 'red-black', new_algo='rb-one')
project.fetch_algorithm(exp, 'merge-one', 'ls4-dd', new_algo='ls-one')

project.fetch_algorithm(exp, 'merge-plus-one', 'ff', new_algo='ff-plusone')
project.fetch_algorithm(exp, 'merge-plus-one', 'red-black', new_algo='rb-plusone')
project.fetch_algorithm(exp, 'merge-plus-one', 'ls4-dd', new_algo='ls-plusone')


#project.add_absolute_report(
#    exp, attributes=ATTRIBUTES, filter=[project.add_evaluations_per_time]
#)
matplotlib_options = {
    "font.family": "serif",
    "font.weight": "normal",
    # Used if more specific sizes not set.
    "font.size": 20,
    "axes.labelsize": 20,
    "axes.titlesize": 30,
    "legend.fontsize": 22,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "lines.markersize": 10,
    "lines.markeredgewidth": 0.25,
    "lines.linewidth": 1,
    # Width and height in inches.
    "figure.figsize": [8, 8],
    "savefig.dpi": 100,
}

# ls ff normal
exp.add_report(
    ScatterPlotReport(
        attributes=["expansions"],
        filter_algorithm=["ls-normal", "ff-normal"],
        format="tex",
    ),
    name="ls-ff-normal-evals",
)
exp.add_report(
    ScatterPlotReport(
        attributes=[project.EVALUATIONS_PER_TIME],
        filter=[project.add_evaluations_per_time],
        filter_algorithm=["ls-normal", "ff-normal"],
        format="tex",
    ),
    name="ls-ff-normal-evals-per-time",
)

# ls ff one
exp.add_report(
    ScatterPlotReport(
        attributes=["expansions"],
        filter_algorithm=["ls-one", "ff-one"],
        format="tex",
    ),
    name="ls-ff-one-evals",
)
exp.add_report(
    ScatterPlotReport(
        attributes=[project.EVALUATIONS_PER_TIME],
        filter=[project.add_evaluations_per_time],
        filter_algorithm=["ls-one", "ff-one"],
        format="tex",
    ),
    name="ls-ff-one-evals-per-time",
)

# ls ff plus one
exp.add_report(
    ScatterPlotReport(
        attributes=["expansions"],
        filter_algorithm=["ls-plusone", "ff-plusone"],
        format="tex",
    ),
    name="ls-ff-plusone-evals",
)
exp.add_report(
    ScatterPlotReport(
        attributes=[project.EVALUATIONS_PER_TIME],
        filter=[project.add_evaluations_per_time],
        filter_algorithm=["ls-plusone", "ff-plusone"],
        format="tex",
    ),
    name="ls-ff-plusone-evals-per-time",
)

# ls rb normal
exp.add_report(
    ScatterPlotReport(
        attributes=["expansions"],
        filter_algorithm=["ls-normal", "rb-normal"],
        format="tex",
    ),
    name="ls-rb-normal-evals",
)
exp.add_report(
    ScatterPlotReport(
        attributes=[project.EVALUATIONS_PER_TIME],
        filter=[project.add_evaluations_per_time],
        filter_algorithm=["ls-normal", "rb-normal"],
        format="tex",
    ),
    name="ls-rb-normal-evals-per-time",
)

# ls rb one
exp.add_report(
    ScatterPlotReport(
        attributes=["expansions"],
        filter_algorithm=["ls-one", "rb-one"],
        format="tex",
    ),
    name="ls-rb-one-evals",
)
exp.add_report(
    ScatterPlotReport(
        attributes=[project.EVALUATIONS_PER_TIME],
        filter=[project.add_evaluations_per_time],
        filter_algorithm=["ls-one", "rb-one"],
        format="tex",
    ),
    name="ls-rb-one-evals-per-time",
)

# ls rb plus one
exp.add_report(
    ScatterPlotReport(
        attributes=["expansions"],
        filter_algorithm=["ls-plusone", "rb-plusone"],
        format="tex",
    ),
    name="ls-rb-plusone-evals",
)
exp.add_report(
    ScatterPlotReport(
        attributes=[project.EVALUATIONS_PER_TIME],
        filter=[project.add_evaluations_per_time],
        filter_algorithm=["ls-plusone", "rb-plusone"],
        format="tex",
    ),
    name="ls-rb-plusone-evals-per-time",
)

exp.run_steps()