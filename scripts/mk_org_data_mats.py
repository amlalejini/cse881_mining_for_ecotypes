
"""
Given:
    * Ground truth info
    * Snapshot data matrices
    * cluster assignment info
    * cluster info

Create:
    * Organism data file
        - org id, time, ...org info..., cluster_id, back_cluster_id, ancestor_id, ancestor_cluster_id

    * Org data file will be used in visualization and in calculation of phylogenetic relationship accuracy
"""

import os, math, sys
from utilities.utilities import *

if __name__ == "__main__":
    exp_path = "/Users/amlalejini/Desktop/scratch/cse881"
    treatments = ["limited_res__rep_1"]
    cluster_treats = ["spec_cluster__nc_9__mode_both"]

    final_update = 25000
    update_step = 5000
    start_update = 5000
    pop_size = 3000

    processed_path = os.path.join(exp_path, "processed")
    final_out_path = os.path.join(exp_path, "final_out")
    mkdir_p(final_out_path)

    orgdata_header = "genotype_id,time,cluster_id,back_cluster_id,ancestor_id,ancestor_cluster_id,tree_depth,genome_length,genome_sequence,is_viable,gestation_time,fitness,phenotype_signature,not,nand,and,ornot,andnot,nor,xor,equals".split(",")
    print "Data to pull together: " + str(orgdata_header)
    for treatment in treatments:
        print "Processing treatments: %s" % treatment
        treatment_path = os.path.join(processed_path, treatment)
        treatment_final_out_path = os.path.join(final_out_path, treatment)
        orig_data_mats_path = os.path.join(treatment_path, "population_data_matrices")
        mkdir_p(treatment_final_out_path)

        ##########################################
        ### Pull ground truth info for this treatment
        ground_truth_fname = "%s__ancestor_gt.csv" % treatment
        ground_truth_fpath = os.path.join(exp_path, "ground_truth", ground_truth_fname)
        ground_truth = ""
        with open(ground_truth_fpath, "r") as fp:
            ground_truth = fp.read().strip("\n").split("\n")
        gt_lookup = {} # will contain gt info for each genotype/org id
        gt_header = ground_truth[0].split(",")
        ground_truth = ground_truth[1:]
        for line in ground_truth:
            line = line.split(",")
            info = {gt_header[i]:line[i] for i in range(0, len(line))}
            gt_lookup[info["org_id"]] = info
        ##########################################

        for ctreat in cluster_treats:
            print "  processing clustering: %s" % ctreat
            ctreat_final_out_path = os.path.join(treatment_final_out_path, ctreat)
            mkdir_p(ctreat_final_out_path)

            ##########################################
            ### Pull out cluster relationship info
            cluster_relation_fname = "clusterinfo___%s.csv" % ctreat
            cluster_relation_fpath = os.path.join(treatment_path, "clusters_agg", cluster_relation_fname)
            cluster_relations = ""
            with open(cluster_relation_fpath, "r") as fp:
                cluster_relations = fp.read().strip("\n").split("\n")
            cluster_relation_lookup = {} # will contain cluster relation info for each cluster id
            cr_header = cluster_relations[0].split(",")
            cluster_relations = cluster_relations[1:]
            for line in cluster_relations:
                line = line.split(",")
                info = {cr_header[i]:line[i] for i in range(0, len(line))}
                cluster_relation_lookup[info["cluster_id"]] = info
            ##########################################
            org_cluster_lookup = {} # {"gen_id": cluster_id, ...}
            orgdata = [] # [{"attr":attr_value, ...}, {}, ...., {}]
            for u in range(start_update, final_update + 1, update_step):
                ##########################################
                ### 1: Pull org info from snapshot file
                snapshot_fname = "snapshot__pop_%d.csv" % u
                snapshot_fpath = os.path.join(orig_data_mats_path, snapshot_fname)
                snapshot = ""
                with open(snapshot_fpath, "r") as fp:
                    snapshot = fp.read().strip("\n").split("\n")
                # Get header info
                snap_header = snapshot[0].split(",")
                # Strip header
                snapshot = snapshot[1:]
                ##########################################

                ##########################################
                ### 2: Pull cluster assignment
                cluster_assignment_fname = "snapshot__pop_%d__distmat.csv" % u
                cluster_assignment_fpath = os.path.join(treatment_path, "clusters", ctreat, cluster_assignment_fname)
                cluster_assignment = ""
                with open(cluster_assignment_fpath, "r") as fp:
                    cluster_assignment = fp.read().strip("\n").split(",")
                ##########################################

                for snapshot_line, cid in zip(snapshot, cluster_assignment):
                    snapshot_line = snapshot_line.split(",")
                    info = {snap_header[i]: snapshot_line[i] for i in range(0, len(snapshot_line))}
                    cid = "%d_%s" % (u, cid)
                    info["cluster_id"] = cid
                    if info["genotype_id"] in org_cluster_lookup:
                        if cid != org_cluster_lookup[info["genotype_id"]]:
                            print "Funky stuff"
                    org_cluster_lookup[info["genotype_id"]] = cid
                    info["ancestor_id"] = gt_lookup[info["genotype_id"]]["ancestor_id"]
                    if info["ancestor_id"] == "none":
                        info["back_cluster_id"] = "none"
                        info["ancestor_cluster_id"] = "none"
                    else:
                        info["back_cluster_id"] = cluster_relation_lookup[cid]["back_cluster_id"]
                        info["ancestor_cluster_id"] = org_cluster_lookup[info["ancestor_id"]]
                    info["time"] = str(u)
                    orgdata.append(info)

            ##########################################
            ### Write out org data to file
            out_fname = "orgdata.csv"
            content = ",".join(orgdata_header) + "\n" + "\n".join([",".join([org[attr] for attr in orgdata_header]) for org in orgdata])
            with open(os.path.join(ctreat_final_out_path, out_fname), "w") as fp:
                fp.write(content)
