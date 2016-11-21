from sklearn.cluster import DBSCAN
from comp_ops import EditDistance, SimpleMatchingSimilarity
import numpy as np

EPSILON = 0.07
MIN_PTS = 5

def AvidaOrgDist(a, b):
    """
    Given two data points, calculate distance between them.
    """
    if a["genotype_id"] == b["genotype_id"]: return 0.0
    genDist = EditDistance(a["genome_sequence"], b["genome_sequence"]) / float(max(len(a["genome_sequence"]), len(b["genome_sequence"])))
    phenDist = 1 - SimpleMatchingSimilarity(a["phenotype_signature"], b["phenotype_signature"])
    return (0.5 * genDist + 0.5 * phenDist)

def main():
    data_fpath = "../testdata/snapshot__pop_2000_dm.csv"

    content = None
    with open(data_fpath, "r") as fp:
        content = fp.read().strip("\n")
    content = content.split("\n")

    distMat = np.zeros((len(content), len(content)), dtype = np.float64)
    for i in range(0, len(content)):
        line = content[i].split(",")
        for j in range(0, len(line)):
            distMat[i][j] = line[j]

    db = DBSCAN(eps = EPSILON, min_samples = MIN_PTS, metric = 'precomputed').fit(distMat)
    print db.labels_
    clusters = {}
    for i in range(0, len(db.labels_)):
        if not db.labels_[i] in clusters:
            clusters[db.labels_[i]] = []
        clusters[db.labels_[i]].append(i)
    print clusters


if __name__ == "__main__":
    main()
