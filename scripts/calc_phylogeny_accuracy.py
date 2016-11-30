import os, math, sys
from utilities.utilities import *

if __name__ == "__main__":
    exp_path = "/Users/amlalejini/Desktop/scratch/cse881"
    treatments = ["limited_res__rep_1"]
    cluster_treats = ["spec_cluster__nc_9__mode_both",
                      "spec_cluster__nc_5__mode_phenotype",
                      "spec_cluster__nc_5__mode_genotype",
                      "db_cluster__ep_0p1__mp_5__mode_phenotype"]

    exclude_slices = ["5000"]

    final_out_path = os.path.join(exp_path, "final_out")

    accuracy_table = {}
    content = "treatment,cluster_params,time,accuracy,num_correct,num_wrong\n"
    for treatment in treatments:
        print "Processing treatments: %s" % treatment
        tfout_path = os.path.join(final_out_path, treatment)
        accuracy_table[treatment] = {}
        for ctreat in cluster_treats:
            accuracy_table[treatment][ctreat] = {}
            print "  processing clustering: %s" % ctreat
            cfout_path = os.path.join(tfout_path, ctreat)
            cluster_relation_fpath = os.path.join(cfout_path, "clusterinfo.csv")
            cluster_relations = ""
            with open(cluster_relation_fpath, "r") as fp:
                cluster_relations = fp.read().strip("\n").split("\n")
            cluster_relations_header = cluster_relations[0].split(",")
            cluster_relations = cluster_relations[1:]
            times = []
            for line in cluster_relations:
                line = line.split(",")
                info = {cluster_relations_header[i]:line[i] for i in range(0, len(line))}
                time = info["time"]
                if not time in accuracy_table[treatment][ctreat]:
                    accuracy_table[treatment][ctreat][time] = {"num_correct": 0, "num_wrong": 0, "percent_correct": 0.0}
                accuracy_table[treatment][ctreat][time]["num_correct"] += int(info["num_correct"])
                accuracy_table[treatment][ctreat][time]["num_wrong"] += int(info["num_wrong"])
            total_corr = 0
            total_wrong = 0
            for time in accuracy_table[treatment][ctreat]:
                num_corr = accuracy_table[treatment][ctreat][time]["num_correct"]
                num_wrong = accuracy_table[treatment][ctreat][time]["num_wrong"]
                accuracy_table[treatment][ctreat][time]["percent_correct"] = float(num_corr) / float(num_wrong + num_corr)
                total_corr += num_corr
                total_wrong += num_wrong
                times.append(int(time))
            accuracy_table[treatment][ctreat]["total"] = {}
            accuracy_table[treatment][ctreat]["total"]["num_correct"] = total_corr
            accuracy_table[treatment][ctreat]["total"]["num_wrong"] = total_wrong
            accuracy_table[treatment][ctreat]["total"]["percent_correct"] = total_corr / float(total_corr + total_wrong)

            times.sort()

            for time in times:
                time = str(time)
                if time in exclude_slices: continue
                num_corr = accuracy_table[treatment][ctreat][time]["num_correct"]
                num_wrong = accuracy_table[treatment][ctreat][time]["num_wrong"]
                per_corr = accuracy_table[treatment][ctreat][time]["percent_correct"]
                content += "%s,%s,%s,%s,%s,%s\n" % (treatment, ctreat, time, per_corr, num_corr, num_wrong)

            num_corr = accuracy_table[treatment][ctreat]["total"]["num_correct"]
            num_wrong = accuracy_table[treatment][ctreat]["total"]["num_wrong"]
            per_corr = accuracy_table[treatment][ctreat]["total"]["percent_correct"]
            content += "%s,%s,%s,%s,%s,%s\n" % (treatment, ctreat, "total", per_corr, num_corr, num_wrong)

    # Create output file.
    with open(os.path.join(final_out_path, "accuracy_table.csv"), "w") as fp:
        fp.write(content)
