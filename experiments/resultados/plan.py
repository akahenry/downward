# -*- coding: utf-8 -*-

import os
from lab import tools
from matplotlib import pyplot
from collections import defaultdict
from downward.reports import PlanningReport

import numpy as np

class MeuPlotReport(PlanningReport):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def write(self):
        data = defaultdict(list)

        
        domain_scores = dict()
        for domain in self.domains:
            problem_scores = dict()

            for problem in self.domains[domain]:
                problem_scores[problem] = dict()

                for algo in self.algorithms:
                    if self.runs[(domain, problem, algo)]['coverage'] == 0:
                        problem_scores[problem][algo] = -1
                    else:
                        problem_scores[problem][algo] = self.runs[(domain, problem, algo)]['plan_length']

            for (problem, algo) in problem_scores.items():    
                try:
                    min_value = min(i for i in algo.values() if i > 0)
                    for name in algo:
                        if algo[name] == -1:
                            algo[name] = 0
                        else:
                            algo[name] = min_value / algo[name]
                except:
                    for name in algo:
                        algo[name] = 0

            scores_by_domain = dict()
            for algo in self.algorithms:
                scores_by_domain[algo] = 0

            for problem in problem_scores.values():
                for algo in scores_by_domain:
                    scores_by_domain[algo] += problem[algo]
            
            domain_scores[domain] = scores_by_domain

            #print(domain, scores_by_domain)

        final = dict()
        for algo in self.algorithms:
            final[algo] = 0

        for domain in domain_scores.values():
            for algo in final:
                final[algo] += domain[algo]
        
        print('sum:', final)
            

        



        '''
        domain_problem_algo_cost = dict()
        for (domain_algo, problems) in self.domain_algorithm_runs.items():

            scores = dict()
            for problem in problems:
                print(domain_algo[0], problem['problem'], domain_algo[1])
         '''
            
