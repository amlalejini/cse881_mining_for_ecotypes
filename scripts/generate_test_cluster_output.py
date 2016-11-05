"""
This script is used to generate a test clustering data set that
can be used to develop the web-visualization.
"""

import random
from utilities.utilities import *

if __name__ == "__main__":
    updates = 400000
    interval = 1000
    pop_size = 500
    organisms = []
    clusters = []

    org_id_cntr = 0
    def GenOrgID():
        global org_id_cntr
        rid = org_id_cntr
        org_id_cntr += 1
        return rid

    prev_clusters = None
    ancestors = {}
    for t in range(0, updates, interval):
        # Build clusters.
        if t == 0:
            num_clusters = 1
        else:
            num_clusters = max(1, min(4, len(clusters[-1]) + random.randint(-1, 1)))
        def GetBackCluster():
            if t == 0:
                return "NONE"
            else:
                return random.choice(prev_clusters)["cluster_id"]
        cur_clusters = [{"cluster_id": "%d_%d" % (t, c), "time": t, "back_cluster_id": GetBackCluster()} for c in range(0, num_clusters)]
        clusters += cur_clusters
        # Set previous clusters to current clusters.
        prev_clusters = cur_clusters

        # Build population slice.
        cur_organisms = [{"org_id": GenOrgID(), "time": t, "cluster_id": random.choice(cur_clusters)["cluster_id"]} for o in range(0, pop_size)]
        for org in cur_organisms:
            if t == 0:
                org["ancestor_id"] = "NONE"
            else:
                c_id = org["cluster_id"]
                bc_id = None
                for clust in cur_clusters:
                    if clust["cluster_id"] == c_id: bc_id = clust["back_cluster_id"]
                org["ancestor_id"] = ancestors[bc_id]["org_id"]

        organisms += cur_organisms
        # pick ancestor representatives for reach cluster id.
        random.shuffle(cur_organisms)
        for org in cur_organisms:
            if org["cluster_id"] in ancestors: continue
            ancestors[org["cluster_id"]] = org

    ### Write out Data files ###
    # Write our organism info data file
    mkdir_p("../testdata")
    org_data_header = ["org_id", "time", "cluster_id", "ancestor_id"]
    cluster_data_header = ["cluster_id", "time", "back_cluster_id"]

    org_data_content = ",".join(org_data_header) + "\n"
    cluster_data_content = ",".join(cluster_data_header) + "\n"

    for org in organisms:
        line = ""
        for attr in org_data_header:
            line += str(org[attr]) + ","
        org_data_content += line.strip(",") + "\n"

    for cluster in clusters:
        line = ""
        for attr in cluster_data_header:
            line += str(cluster[attr]) + ","
        cluster_data_content += line.strip(",") + "\n"

    with open("../testdata/testorgdata.csv", "w") as fp:
        fp.write(org_data_content)
    with open("../testdata/testclusterdata.csv", "w") as fp:
        fp.write(cluster_data_content)
