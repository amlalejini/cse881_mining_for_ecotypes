
import os, sys
from utilities.utilities import *
from order_cluster_data import OrderClusterData

if __name__ == "__main__":
    exp_path = "/Users/amlalejini/Desktop/scratch/cse881"
    treatments = ["limited_res__rep_1"]
    cluster_treats = ["spec_cluster__nc_9__mode_both",
                      "spec_cluster__nc_5__mode_phenotype",
                      "spec_cluster__nc_5__mode_genotype",
                      "db_cluster__ep_0p1__mp_5__mode_phenotype"]
    processed_path = os.path.join(exp_path, "processed")

    for treatment in treatments:
        print "Processing treatment: %s" % treatment
        treatment_path = os.path.join(processed_path, treatment)
        cluster_agg_path = os.path.join(treatment_path, "clusters_agg")
        treatment_out_path = os.path.join(exp_path, "final_out", treatment)

        for ctreat in cluster_treats:
            print "  processing clustering: %s" % ctreat
            ctreat_out_path = os.path.join(treatment_out_path, ctreat)

            # Load org data
            org_data_content = None
            with open(os.path.join(ctreat_out_path, "orgdata.csv"), "r") as fp:
                org_data_content = fp.read().strip("\n").split("\n")
            org_data_header = org_data_content[0].split(",")
            org_data_content = org_data_content[1:]

            # Load aggregate cluster info
            cluster_info = {}
            agg_cluster_content = None
            with open(os.path.join(cluster_agg_path, "clusterinfo___%s.csv" % ctreat), "r") as fp:
                agg_cluster_content = fp.read().strip("\n").split("\n")
            agg_cluster_header = agg_cluster_content[0].split(",")
            agg_cluster_content = agg_cluster_content[1:]
            cluster_ids = []
            for line in agg_cluster_content:
                line = line.split(",")
                info = {agg_cluster_header[i]:line[i] for i in range(0, len(line))}
                info["num_correct"] = 0
                info["num_wrong"] = 0
                info["total"] = 0
                cluster_info[info["cluster_id"]] = info
                cluster_ids.append(info["cluster_id"])

            # For each org, check if back_cluster matches gt ancestor cluster is correct.
            for line in org_data_content:
                line = line.split(",")
                info = {org_data_header[i]:line[i] for i in range(0, len(line))}
                cluster_id = info["cluster_id"]
                back_cluster_id = info["back_cluster_id"]
                ancestor_cluster_id = info["ancestor_cluster_id"]

                # Handle cases where cluster ID doesn't exist (time slice 0)
                if not cluster_id in cluster_info:
                    # Make a new cluster info
                    new_c_info = {"time": cluster_id.split("_")[0], "cluster_id": cluster_id, "back_cluster_id": "none", "num_correct": 0, "num_wrong":0, "total":0}
                    cluster_info[cluster_id] = new_c_info
                    cluster_ids.insert(0, cluster_id)

                if back_cluster_id == ancestor_cluster_id:
                    cluster_info[cluster_id]["num_correct"] += 1
                else:
                    cluster_info[cluster_id]["num_wrong"] += 1
                cluster_info[cluster_id]["total"] += 1

            # Output results
            agg_cluster_header += ["num_correct", "num_wrong", "total"]
            updated_agg_cluster_content = ",".join(agg_cluster_header) + "\n"
            for cid in cluster_ids:
                line = ",".join([str(cluster_info[cid][attr]) for attr in agg_cluster_header])
                updated_agg_cluster_content += line + "\n"

            updated_agg_cluster_content = OrderClusterData(updated_agg_cluster_content)

            out_fname = "clusterinfo.csv"
            out_fpath = os.path.join(ctreat_out_path, out_fname)
            with open(out_fpath, "w") as fp:
                fp.write(updated_agg_cluster_content)
