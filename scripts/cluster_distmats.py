
"""
Given directory of distance matrices:
    * load matrix
    * interpret distances (dist(gen)|dist(phen)) and transform matrix
    * cluster transformed matrix
    * output clusters
"""

import os, math, sys
import numpy as np
from sklearn.cluster import DBSCAN, SpectralClustering
from utilities.utilities import *

MODE = "both"
EPSILON = 0.1
MINPTS = 10
ALGORITHM = "dbscan"
NCLUSTERS = 9

def CalcDist(phen_dist, max_phen_dist, min_phen_dist, gen_dist, max_gen_dist, min_gen_dist):
    """
    Given a genotype distance, max genotype distance, phenotype distance and max phenotype distance,
    calculate normalized distance between two things.
    *** phenotype distance is given as similarity metric -- subtract from 1 to get distance. **
    """
    # TODO: figure out proper calculations when less tired... did I already normalize phenotype stuff? Blah blah.
    phen_dist = 1 - phen_dist
    min_phen_dist = 1 - max_phen_dist
    max_phen_dist = 1 - min_phen_dist
    norm_pdist = (phen_dist - min_phen_dist) / float(max_phen_dist)
    norm_gdist = (gen_dist - min_gen_dist) / float(max_gen_dist)
    if MODE == "both": return (0.5 * norm_pdist) + (0.5 * norm_gdist) # both
    elif MODE == "phenotype": return norm_pdist # Just phenotype
    elif MODE == "genotype": return norm_gdist # Just genotype
    else: return None

def CalcAffinity(phen_dist, max_phen_dist, min_phen_dist, gen_dist, max_gen_dist, min_gen_dist):
    """
    Given a genotype distance, max genotype distance, phenotype distance and max phenotype distance,
    calculate normalized distance between two things.
    *** phenotype distance is given as similarity metric -- subtract from 1 to get distance. **
    """
    # TODO: figure out proper calculations when less tired... did I already normalize phenotype stuff? Blah blah.
    phen_dist = 1 - phen_dist
    min_phen_dist = 1 - max_phen_dist
    max_phen_dist = 1 - min_phen_dist
    norm_pdist = (phen_dist - min_phen_dist) / float(max_phen_dist)
    norm_gdist = (gen_dist - min_gen_dist) / float(max_gen_dist)
    if MODE == "both": return 1 - (0.5 * norm_pdist) + (0.5 * norm_gdist) # both
    elif MODE == "phenotype": return 1 - norm_pdist # Just phenotype
    elif MODE == "genotype": return 1 - norm_gdist # Just genotype
    else: return None

if __name__ == "__main__":
    exp_path = "/Users/amlalejini/Desktop/scratch/cse881"
    treatments = ["limited_res__rep_1"]
    distmat_dir = "dist_mats"
    cluster_dir = "clusters"

    # Sys arg: mode, algorithm, [epsilon], [minpts], [nclusters]
    try:
        print sys.argv
        MODE = str(sys.argv[2])
        ALGORITHM = str(sys.argv[1])
        if ALGORITHM == "spectral":
            NCLUSTERS = int(sys.argv[3])
        elif ALGORITHM == "dbscan":
            EPSILON = float(sys.argv[3])
            MINPTS = int(sys.argv[4])
    except:
        print "Could not load parameters (epsilon, minpts, mode, algorithm)"
        exit(-1)

    if ALGORITHM == "spectral":
        print "Alg: spectral, Mode: %s, Nclusters: %s" % (MODE, str(NCLUSTERS))
    elif ALGORITHM == "dbscan":
        print "Alg: dbscan, Mode: %s, EPSILON: %s, MINPTS: %s" % (MODE, str(EPSIOLON), str(MINPTS))
    processed_path = os.path.join(exp_path, "processed")

    for treatment in treatments:
        print "Processing treatment: %s" % treatment
        treatment_path = os.path.join(processed_path, treatment)
        dist_mats_path = os.path.join(treatment_path, distmat_dir)
        if ALGORITHM == "dbscan":
            cluster_params = "db_cluster__ep_%s__mp_%s__mode_%s" % (str(EPSILON).replace(".", "p"), str(MINPTS), MODE)
        elif ALGORITHM == "spectral":
            cluster_params = "spec_cluster__nc_%s__mode_%s" % (str(NCLUSTERS), str(MODE))
        else:
            cluster_params = None
        cluster_path = os.path.join(treatment_path, cluster_dir, cluster_params)
        mkdir_p(cluster_path)
        mats = [name for name in os.listdir(dist_mats_path) if ".csv" in name]
        for mat in mats:
            print "  Processing distance matrix: %s" % mat
            # Load matrix.
            content = None
            with open(os.path.join(dist_mats_path, mat), "r") as fp:
                content = fp.read().strip("\n").split("\n")
            dist_mat = np.zeros((len(content), len(content)))
            affin_mat = np.zeros((len(content), len(content)))
            # Get max phenotype and genotype dist (for normalization)
            max_gen_dist = -1
            min_gen_dist = float('inf')
            max_phen_dist = -1
            min_phen_dist = float('inf')
            for i in range(0, len(content)):
                line = content[i].split(",")
                for j in range(0, len(line)):
                    entry = line[j].split("|")
                    gdist = float(entry[0])
                    pdist = float(entry[1])
                    if i == j: pdist = 1.0 # Correct for mistakes along diagonal
                    if gdist > max_gen_dist: max_gen_dist = gdist
                    if pdist > max_phen_dist: max_phen_dist = pdist
                    if pdist < min_phen_dist: min_phen_dist = pdist
                    if gdist < min_gen_dist: min_gen_dist = gdist
                content[i] = line
            print "  Gen dist range: [%f, %f]" % (min_gen_dist, max_gen_dist)
            print "  Phen dist range: [%f, %f]" % (min_phen_dist, max_phen_dist)
            # Compute transfromed distance matrix.
            for i in range(0, len(content)):
                for j in range(0, len(content[i])):
                    entry = content[i][j].split("|")
                    gdist = float(entry[0])
                    pdist = float(entry[1])
                    if i == j: pdist = 1.0 # Correct for mistake with phen dist along diagonal.
                    dist_mat[i][j] = CalcDist(pdist, max_phen_dist, min_phen_dist, gdist, max_gen_dist, min_gen_dist)
                    affin_mat[i][j] = CalcAffinity(pdist, max_phen_dist, min_phen_dist, gdist, max_gen_dist, min_gen_dist)
            print "  Clustering..."
            if ALGORITHM == "dbscan":
                db = DBSCAN(eps = EPSILON, min_samples = MINPTS, metric = 'precomputed').fit(dist_mat)
            elif ALGORITHM == "spectral":
                db = SpectralClustering(n_clusters = NCLUSTERS, affinity = 'precomputed').fit(affin_mat)
            # clusters = {}
            cluster_content = ""
            for i in range(0, len(db.labels_)):
                cluster_content += "%d," % db.labels_[i]
                # if not db.labels_[i] in clusters:
                #     clusters[db.labels_[i]] = []
                # clusters[db.labels_[i]].append(i)
            # print clusters
            cluster_content = cluster_content[:-1] + "\n"
            mat_name = mat.split(".")[0]
            with open(os.path.join(cluster_path, mat_name + ".csv"), "w") as fp:
                fp.write(cluster_content)
