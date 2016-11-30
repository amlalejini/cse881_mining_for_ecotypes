"""
This script will generate the following file:

cluster_phylo_data
    * cluster_id, time, back_cluster_id
        - cluster_id: id of this cluster
        - back_cluster_id: id of back cluster
        - time: time that this cluster exists at
"""

import os, math, sys
from utilities.utilities import *

if __name__ == "__main__":
    exp_path = "/Users/amlalejini/Desktop/scratch/cse881"
    treatments = ["limited_res__rep_1"]
    cluster_dir = "clusters"
    cluster_treats = ["spec_cluster__nc_9__mode_both"]

    final_update = 25000
    update_step = 5000
    start_update = 5000
    pop_size = 3000

    processed_path = os.path.join(exp_path, "processed")

    for treatment in treatments:
        print "Processing treatment: %s" % treatment
        treatment_path = os.path.join(processed_path, treatment)
        out_cluster_path = os.path.join(treatment_path, "clusters_agg")
        mkdir_p(out_cluster_path)
        for ctreat in cluster_treats:
            print "  processing clustering: %s" % ctreat
            cluster_path = os.path.join(treatment_path, "clusters", ctreat)
            # Calculate relationships.
            cluster_info = "time,cluster_id,back_cluster_id\n"
            for u in range(start_update + update_step, final_update + 1, update_step):
                print "  cur update: " + str(u)
                #############
                # Get all relevant cluster assignment information.
                #############
                # Open back
                back_name = "snapshot__pop_%d__distmat.csv" % (u - update_step)
                back_cids = None
                with open(os.path.join(cluster_path, back_name), "r") as fp:
                    back_cids = fp.read().strip("\n").split(",")
                # Open transition
                trans_name = "trans__pop_%d_%d__distmat.csv" % (u - update_step, u)
                trans_cids = None
                with open(os.path.join(cluster_path, trans_name), "r") as fp:
                    trans_cids = fp.read().strip("\n").split(",")
                # Partition transition
                back_co_cids = trans_cids[:pop_size]
                cur_co_cids = trans_cids[-1 * pop_size:]
                # Open current
                cur_name = "snapshot__pop_%d__distmat.csv" % (u)
                cur_cids = None
                with open(os.path.join(cluster_path, cur_name), "r") as fp:
                    cur_cids = fp.read().strip("\n").split(",")
                #############
                # For each co cluster:
                #   * determine back-cluster makeup
                #   * determine cur-cluster makeup
                # For each cur cluster:
                #   * determine co-cluster makeup
                #   * pick majority co-cluster's majority back-cluster
                coclusters = {}
                curclusters = {}
                for i in range(0, len(back_co_cids)):
                    back_cid = back_cids[i]
                    co_cid = back_co_cids[i]
                    if not co_cid in coclusters:
                        coclusters[co_cid] = {"back":{}, "cur":{}}
                    if not back_cid in coclusters[co_cid]["back"]:
                        coclusters[co_cid]["back"][back_cid] = 0
                    coclusters[co_cid]["back"][back_cid] += 1
                for i in range(0, len(cur_co_cids)):
                    cur_cid = cur_cids[i]
                    co_cid = cur_co_cids[i]
                    if not co_cid in coclusters:
                        coclusters[co_cid] = {"back":{}, "cur":{}}
                    if not cur_cid in coclusters[co_cid]["cur"]:
                        coclusters[co_cid]["cur"][cur_cid] = 0
                    coclusters[co_cid]["cur"][cur_cid] += 1
                    # add co-cluster vote to cur cluster
                    if not cur_cid in curclusters:
                        curclusters[cur_cid] = {"coclusters":{}}
                    if not co_cid in curclusters[cur_cid]["coclusters"]:
                        curclusters[cur_cid]["coclusters"][co_cid] = 0
                    curclusters[cur_cid]["coclusters"][co_cid] += 1

                # For each co-cluster, pick a back cluster rep.
                for co_cid in coclusters:
                    backs = coclusters[co_cid]["back"]
                    if len(backs) == 0:
                        mback = "NONE"
                    else:
                        mback = max(backs, key=backs.get)
                    if mback == "-1": mback = "NONE"
                    coclusters[co_cid]["back-rep"] = mback
                # For each cur cluster, determine which co-cluster the majority of these orgs get assigned to
                for cur_cid in curclusters:
                    cos = curclusters[cur_cid]["coclusters"]
                    mcos = max(cos, key=cos.get)
                    curclusters[cur_cid]["co-rep"] = mcos
                # For each cur cluster, pick a back cluster
                for cur_cid in curclusters:
                    curclusters[cur_cid]["back-cluster"] = coclusters[curclusters[cur_cid]["co-rep"]]["back-rep"]

                print "Coclusters:"
                for cid in coclusters:
                    print "%s: %s" % (cid, str(coclusters[cid]))
                print "Cur clusters:"
                for cid in curclusters:
                    print "%s: %s" % (cid, str(curclusters[cid]))

                # Append info to cluster info file
                time = u
                for cid in curclusters:
                    cluster_id = "%s_%s" % (str(time), str(cid))
                    back_cluster_id = "%s_%s" % (str(time - update_step), str(curclusters[cid]["back-cluster"]))
                    line = "%s,%s,%s\n" % (str(time), cluster_id, back_cluster_id)
                    cluster_info += line

            with open(os.path.join(out_cluster_path, "clusterinfo___%s.csv" % ctreat), "w") as fp:
                fp.write(cluster_info)
