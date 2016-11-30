# cse881_mining_for_ecotypes
Repo to hold things for CSE881 Semester Project


## Distance matrix format:
d(o1-gen, o1-gen)|d(o1-phen, o1-phen), d(o1-gen, o2-gen)|d(o1-phen, o2-phen)....
...

## Data to use:
  * Treatment: limited_res
    - Reps: 1, 2, 3, 10, 11

## Template to run 'run_distmatrix_computations.py':
  * python run_distmatrix_computations.py ~/Data/cse881_project/processed/limited_res__rep_1/population_data_matrices__reduced/ ~/Data/cse881_project/processed/limited_res__rep_1/population_dist_matrices__reduced


## Data Processing Steps
  * Run avida analysis mode to pull necessary information for data processing
    * Script: run_avida_analyses.py
  * Make data matrices from experiment data that can be used to calculate pairwise distance
    * Script: mk_precluster_data_matrices.py
  * Reduce data
    * Script: reduce_data.py
    * This script reduces the data resolution (1000 update slices --> 5000 update slices)
  * Compute ground truth for each organism
    * Script: extract_lineages.py
    * This will create a ground truth .csv file that contains ancestor
      relationships
  * Compute pairwise distance matrices:
    * Program: calcdistmats (c++ program)
    * Helper script: run_distmatrix_computations.py
  * Partition transition pairwise distance matrices:
    * Script: partition_trans_mats.py
    * This script exists because computing pairwise distances is slow.
      Instead of computing for snapshot_X, transition_X_Y, & snapshot_Y,
      I just compute transition_X_Y. This script will take that transition_X_Y pairwise distance
      matrix and extract snaphot_X and snapshot_Y matrices.
  * Clustering on pairwise distance matrices:
    * Script: cluster_distmats.py
  * Infer phylogenetic relationships based on co-clustering
    * Script: rebuild_phylogeny_from_clusters.py
    * Given cluster assignments, create cluster info file that contains cluster relationship information.
  * Make data matrices that incorporate cluster information
    * Script: mk_postcluster_data_matrices.py
  * Order cluster data to optimize for visualization
    * Script: order_cluster_data.py
    * This script must be run before visualizing data.
  * Calculate phylogeny accuracy:
    * Script: calc_phylogeny_accuracy.py
