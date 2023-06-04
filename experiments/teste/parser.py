#! /usr/bin/env python

import logging
import re

from lab.parser import Parser


class CommonParser(Parser):
    def add_repeated_pattern(
        self, name, regex, file="run.log", required=False, type=int
    ):
        def find_all_occurences(content, props):
            matches = re.findall(regex, content)
            if required and not matches:
                logging.error(f"Pattern {regex} not found in file {file}")
            props[name] = [type(m) for m in matches]

        self.add_function(find_all_occurences, file=file)

    def add_bottom_up_pattern(
        self, name, regex, file="run.log", required=False, type=int
    ):
        def search_from_bottom(content, props):
            reversed_content = "\n".join(reversed(content.splitlines()))
            match = re.search(regex, reversed_content)
            if required and not match:
                logging.error(f"Pattern {regex} not found in file {file}")
            if match:
                props[name] = type(match.group(1))

        self.add_function(search_from_bottom, file=file)

def main():
    parser = CommonParser()
    parser.add_bottom_up_pattern(
        "search_start_time",
        r"\[t=(.+)s, \d+ KB\] g=0, 1 evaluated, 0 expanded",
        type=float,
    )
    parser.add_bottom_up_pattern(
        "search_start_memory",
        r"\[t=.+s, (\d+) KB\] g=0, 1 evaluated, 0 expanded",
        type=int,
    )
    parser.add_pattern(
        "initial_h_value",
        r"f = (\d+) \[1 evaluated, 0 expanded, t=.+s, \d+ KB\]",
        type=int,
    )
    parser.add_repeated_pattern(
        "h_values",
        r"New best heuristic value for .+: (\d+)\n",
        type=int,
    )
    parser.add_pattern(
        "restrictions", 
        r"Restrictions: (\d+)", 
        type=int)
    parser.add_pattern(
        "operators", 
        r"Operators: (\d+)", 
        type=int)
    parser.add_pattern(
        "increments", 
        r"Increments: (\d+)", 
        type=int)
    
    #sga
    parser.add_pattern(
        "time_sga", 
        r"Time to build SGA patterns: (.+)s", 
        type=float)
    parser.add_pattern(
        "memory_sga", 
        r"Memory used to SGA patterns: (\d+)", 
        type=int)

    # combined
    parser.add_pattern(
        "time_combined", 
        r"Time to build combined patterns:(.+)s", 
        type=float)
    parser.add_pattern(
        "memory_combined", 
        r"Memory used to combined patterns: (\d+)", 
        type=int)
    
    # reduced
    parser.add_pattern(
        "time_reduced", 
        r"Time to build get reduced patterns:(.+)s", 
        type=float)
    parser.add_pattern(
        "memory_reduced", 
        r"Memory used to get reduced patterns: (\d+)", 
        type=int)

    # compute
    parser.add_pattern(
        "time_compute", 
        r"Time to build compute PDBs: (.+)s", 
        type=float)
    parser.add_pattern(
        "memory_compute", 
        r"Memory used to compute PDBs: (\d+)", 
        type=int)  

    parser.add_pattern(
        "initial_h", 
        r"Heuristic for initial state: (\d+)", 
        type=int)  

    parser.parse()



if __name__ == "__main__":
    main()
