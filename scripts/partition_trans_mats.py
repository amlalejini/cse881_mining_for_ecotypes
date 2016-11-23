
"""
This script loads transition matrices and partitions out the snapshot matrices.
Outputs snapshot matrices in same directory as transition matrices.
"""

import os, sys

if __name__ == "__main__":
    exp_path = "/Users/amlalejini/Desktop/scratch/cse881"
    treatments = ["limited_res__rep_1"]
    final_update = 25000
    update_step = 5000
    start_update = 5000
    pop_size = 3000
    # final_update = 10
    # update_step = 5
    # start_update = 5
    # pop_size = 5

    processed_path = os.path.join(exp_path, "processed")

    for treatment in treatments:
        print "Analyzing treatment: %s" % treatment
        dist_mats_path = os.path.join(processed_path, treatment, "dist_mats")
        trans_mats = [name for name in os.listdir(dist_mats_path) if "trans__" in name and ".csv" in name]
        for u in range(start_update, final_update, update_step):
            trans_mat = "trans__pop_%d_%d__distmat.csv" % (u, u + update_step)
            print "  Partitioning: " + str(trans_mat)
            if not trans_mat in trans_mats: print "Oh no! It looks like that trans matrix is not where you promised it would be."
            trans_mat_fpath = os.path.join(dist_mats_path, trans_mat)
            # Load trans mat file
            content = None
            with open(trans_mat_fpath, "r") as fp:
                content = fp.read().strip("\n").split("\n")
                content = [line.split(",") for line in content]
            # Top left pop_size x pop_size
            pop1 = "\n".join([",".join(row[:pop_size]) for row in content[:pop_size]])
            with open(os.path.join(dist_mats_path, "snapshot__pop_%d__distmat.csv" % u), "w") as fp:
                fp.write(pop1)
            if u == (final_update - update_step):
                # Bottom right pop_size x pop_size
                pop2 = "\n".join([",".join(row[-1 * pop_size:]) for row in content[-1 * pop_size:]])
                with open(os.path.join(dist_mats_path, "snapshot__pop_%d__distmat.csv" % (u + update_step)), "w") as fp:
                    fp.write(pop2)
