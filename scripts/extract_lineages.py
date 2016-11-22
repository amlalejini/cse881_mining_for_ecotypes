"""
Quick and dirty lineage extraction script.
"""

import os, sys, json
from utilities.parse_avida_output import *
from utilities.utilities import *

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
    exp_path = "/Users/amlalejini/Desktop/scratch/cse881"
    #exp_path = "/mnt/home/amlalejini/Data/cse881_project"
    final_update = 400000
    data_path = os.path.join(exp_path, "data")
    analysis_path = os.path.join(exp_path, "analysis")
    gt_path = os.path.join(exp_path, "ground_truth")
    mkdir_p(gt_path)
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
        ground_truth_header = ["org_id", "time", "ancestor_id", "ancestor_time"]
        prev_living = None
        for u in range(5000, final_update, 5000):
            # Load current living snapshot.
            # snapshot_path = os.path.join(analysis_path, treatment, "pop_%d" % u, "pop_detail.dat")
            # snapshot_orgs = detail_file_extract(snapshot_path)
            # Load appropriate population
            spop_path = os.path.join(data_path, treatment, "data", "detail-%d.spop" % u)
            print "Current spop: detail-%d.spop" % u
            print "  loading spop file..."
            [cur_spop, cur_living] = LoadSPop(spop_path)
            print "  len(cur_living): " + str(len(cur_living))
            print "  analysing lineages..."
            # for each org, make a thingy
            for org_id in cur_living:
                line = None
                if prev_living == None:
                    line = {"time": u, "org_id": org_id, "ancestor_id": "none", "ancestor_time": "none"}
                else:
                    # What is this org_id's ancestor from previous snapshot?
                    #  * Trace ancestors back until one shows up in previous snapshot.
                    ancestor_id = None
                    cur_ancestor = org_id
                    while cur_ancestor != "(none)":
                        if cur_ancestor in prev_living:
                            ancestor_id = cur_ancestor
                            break
                        cur_ancestor = cur_spop[cur_ancestor]["Parent ID(s)"]
                    line = {"time": u, "org_id": org_id, "ancestor_id": ancestor_id, "ancestor_time":u - 5000}
                ground_truth_lines.append(line)
            prev_living = cur_living
        ground_truth_content = ",".join(ground_truth_header) + "\n"
        for line in ground_truth_lines:
            ground_truth_content += ",".join([str(line[attr]) for attr in ground_truth_header]) + "\n"
        ground_truth_content = ground_truth_content.strip("\n")
        with open(os.path.join(gt_path, treatment + "__ancestor_gt.csv"), "w") as fp:
            fp.write(ground_truth_content)
