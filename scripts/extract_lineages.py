"""
Quick and dirty lineage extraction script.
"""

import os, sys, json
from utilities.parse_avida_output import *

def LoadSPop(spop_path):
    content = None
    with open(spop_path, "r") as fp:
        content = fp.read().strip("\n").split("\n")
    # First, strip off garbage at top.
    content = content[4:]
    attr_lookup = {}
    data_start = None
    for i in range(0, len(content)):
        line = content[i]
        if line.strip() == "":
            data_start = i + 1
            break
        line = line.split(":")
        attr = line[-1].strip()
        loc = line[0].split(" ")[-1]
        attr_lookup[attr] = int(loc) - 1
    # Collect data
    pop_by_id = {}  # Every organism by ID
    living_pop = set() # ID's of living organisms.
    for i in range(data_start, len(content)):
        line = content[i].strip().split(" ")
        org = {attr:line[attr_lookup[attr]] for attr in attr_lookup if attr_lookup[attr] < len(line)}
        pop_by_id[org["ID"]] = org
        if int(org["Number of currently living organisms"]) > 0:
            living_pop.add(org["ID"])
    return [pop_by_id, living_pop]

if __name__ == "__main__":
    #exp_path = "/Users/amlalejini/Desktop/scratch/cse881"
    exp_path = "/mnt/home/amlalejini/Data/cse881_project"
    final_update = 400000
    data_path = os.path.join(exp_path, "data")
    analysis_path = os.path.join(exp_path, "analysis")
    treatments = ["limited_res__rep_1", "limited_res__rep_2",
                  "limited_res__rep_3", "limited_res__rep_10", "limited_res__rep_11"]
    for treatment in treatments:
        print "Analysing treatment: %s" % treatment
        # pop_path = os.path.join(data_path, treatment, "data", "detail-%d.spop" % final_update)
        # Trace lineage.
        # print "  tracing lineages..."
        # lineages = {} # Lineage for each living organism.
        # for org_id in living_pop:
        #     # Trace org's lineage.
        #     lineage = [pop_by_id[org_id]["Parent ID(s)"]]
        #     while lineage[-1] != "(none)":
        #         lineage.append(pop_by_id[lineage[-1]]["Parent ID(s)"])
        #     lineages[org_id] = lineage

        # For each snapshot that we care about...
        # extract ground truth for lineage stuff:
        #  org_id, time, ancestor_id (from last snapshot)
        ground_truth_lines = []
        prev_living = None
        for u in range(5000, final_update, 5000):
            # Load current living snapshot.
            # snapshot_path = os.path.join(analysis_path, treatment, "pop_%d" % u, "pop_detail.dat")
            # snapshot_orgs = detail_file_extract(snapshot_path)
            # Load appropriate population
            spop_path = os.path.join(data_path, treatment, "data", "detail-%d".spop % u)
            [cur_spop, cur_living] = LoadSPop(spop_path)
            # for each org, make a thingy
            for org_id in cur_living:
                line = None
                if prev_living == None:
                    line = {"time": u, "org_id": org_id, "ancestor_id": "none", "ancestor_time": "none"}
                else:
                    # What is this org_id's ancestor from previous snapshot?
                    #  * Trace ancestors back until one shows up in previous snapshot.
                    ancestor_id = None
                    next_ancestor = org_id
                    while next_ancestor != "(none)":
                        if next_ancestor in prev_living:
                            print "Found ancestor from previous snapshot."
                            ancestor_id = next_ancestor
                            break
                        cur_ancestor = cur_spop[next_ancestor]["Parent ID(s)"]
                    line = {"time": u, "org_id": org_id, "ancestor_id": ancestor_id, "ancestor_time":u - 5000}
                ground_truth_lines.append(line)
            prev_living = cur_living
        print ground_truth_lines
        exit()
