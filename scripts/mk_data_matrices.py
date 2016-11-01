#!/usr/bin/python2

"""
This script will look through specified treatment/reps analysis detail files,
building data matrices.

Matrix Columns:
-- Meta data --
Organism ID
Tree Depth

-- Genotype data --
Genome Length
Genome Sequence

instr--a
instr--b
instr--c
instr--d
instr--e
instr--f
instr--g
instr--h
instr--i
instr--j
instr--k
instr--l
instr--m
instr--n
instr--o
instr--p
instr--q
instr--r
instr--s
instr--t
instr--u
instr--v
instr--w
instr--x
instr--y
instr--z

-- Phenotype data --
Is Viable
Gestation Time ()
Fitness
Phenotype Signature: NOT, NAND, AND, ORNOT, OR, ANDNOT, NOT, XOR, EQU
NOT
NAND
AND
ORNOT
OR
ANDNOT
NOR
XOR
EQU
"""

import json, os, subprocess
from utilities.parse_avida_output import *
from utilities.utilities import *

matrix_attrs = ["genotype id", "tree depth", "genome length", "genome sequence",
                "is viable (0/1)", "gestation time", "fitness", "phenotype signature",
                "not", "nand", "and", "ornot", "andnot", "nor", "xor", "equals"]

phenotype_signature = ["not", "nand", "and", "ornot", "andnot", "nor", "xor", "equals"]

instruction_map = {"a":"nop-A",
                   "b":"nop-B",
                   "c":"nop-C",
                   "d":"if-n-equ",
                   "e":"if-less",
                   "f":"if-label",
                   "g":"mov-head",
                   "h":"jmp-head",
                   "i":"get-head",
                   "j":"set-flow",
                   "k":"shift-r",
                   "l":"shift-l",
                   "m":"inc",
                   "n":"dec",
                   "o":"push",
                   "p":"pop",
                   "q":"swap-stk",
                   "r":"swap" ,
                   "s":"add",
                   "t":"sub",
                   "u":"nand",
                   "v":"h-copy",
                   "w":"h-alloc",
                   "x":"h-divide",
                   "y":"IO",
                   "z":"h-search"
                  }


def main():
    """
    Main Script
    """
    settings_fn = "params/settings.json"
    settings = None
    # Load settings from settings file.
    with open(settings_fn) as fp: settings = json.load(fp)["data_matrix_construction"]
    # Pull out locations of interest.
    exp_loc = settings["experiment_location"]
    analysis_loc = os.path.join(exp_loc, "analysis")
    # Treatments to analyze?
    treatments = settings["treatments"]
    if settings["replicates_by_treatment"] == "all":
        to_process = [r for r in os.listdir(analysis_loc) if "__rep_" in r and r.split("__rep_")[0] in treatments]
    else:
        replicates_by_treatment = settings["replicates_by_treatment"]

    # Analyze each run that needs to be processed
    matrix_header = (",".join(matrix_attrs)).replace(" (0/1)", "").replace(" ", "_") + "\n"
    for run in to_process:
        print "Processing " + run
        run_analysis_loc = os.path.join(analysis_loc, run)
        run_processed_loc = os.path.join(exp_loc, "processed", run)
        mkdir_p(run_processed_loc)
        mkdir_p(os.path.join(run_processed_loc, "population_data_matrices"))
        mkdir_p(os.path.join(run_processed_loc, "transition_data_matrices"))
        # * Make a .csv for each population.
        # * Make a .csv for each transition.
        prev_content = None
        prev_pop = None
        cur_content = None
        cur_pop = None
        populations = [(int(p.split("_")[-1]), p) for p in os.listdir(run_analysis_loc) if "pop_" in p]
        populations.sort()
        for pop in populations:
            pop = pop[-1]
            pop_details_fn = os.path.join(run_analysis_loc, pop, "pop_detail.dat")
            with open(pop_details_fn, "r") as fp: pop_details = detail_file_extract(fp)
            prev_content = cur_content
            prev_pop = cur_pop
            cur_content = ""
            cur_pop = pop
            # for each genotype:
            for genotype in pop_details:
                genotype_details = pop_details[genotype]
                # Repeat for num cpus
                num_observations = int(genotype_details["number of cpus"])
                for _ in range(0, num_observations):
                    observation = []
                    for attr in matrix_attrs:
                        # Special case: phenotype signature
                        if attr == "phenotype signature":
                            observation.append(''.join([genotype_details[task] for task in phenotype_signature]))
                        # General case
                        else:
                            observation.append(genotype_details[attr])
                    observation = ','.join(observation) + "\n"
                    cur_content += observation
            # Write out pop_slice (cur content)
            with open(os.path.join(run_processed_loc, "population_data_matrices", "snapshot__" + pop + ".csv"), "w") as fp:
                fp.write(matrix_header + cur_content)
            # Write out transition (prev_content + cur_content)
            if prev_content != None:
                with open(os.path.join(run_processed_loc, "transition_data_matrices", "transition__" + prev_pop + "--" + cur_pop + ".csv"), "w") as fp:
                    fp.write(matrix_header + prev_content + cur_content)
    print ("Done")






if __name__ == "__main__":
    main()
