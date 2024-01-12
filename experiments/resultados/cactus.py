# -*- coding: utf-8 -*-

import os
from lab import tools
from matplotlib import pyplot
from collections import defaultdict
from downward.reports import PlanningReport

class CactusPlotReport(PlanningReport):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def write(self):
        data = defaultdict(list)

        for algo in self.algorithms:
            runtimes = []
            for run in self.runs.values():
                
                if run["algorithm"] != algo:
                    continue
                if run["coverage"]:
                    runtimes.append(int(run["total_time"] + int(run['search_start_time'])))
            runtimes.sort()
            coverage = len(runtimes)
            coords = []
            last_runtime = None
            for runtime in reversed(runtimes):
                if last_runtime is None or runtime < last_runtime:
                    x = runtime
                    y = coverage
                    coords.append((x, y))
                coverage -= 1
                last_runtime = runtime

            coords.insert(0, (1800, coords[0][1]))            
            coords = reversed(coords)
            
            data[algo] = coords
        
        plt = pyplot

        for algo in data:
            plt.plot(*zip(*data[algo]), label=algo)

        plt.xscale("log")
        plt.legend()

        plt.xlabel('Search time in seconds')
        plt.ylabel('Solved tasks')

        plt.savefig(self.outfile)

