"""
This script orders cluster data to maximize prettiness it look pretty for visualization.
"""

import sys, os

def OrderClusterData(file_content):
    content = file_content
    content = content.strip("\n").split("\n")
    attrs = content[0].split(",")
    content = content[1:]
    print attrs
    time_slices = {}
    times = set([])
    for line in content:
        line = line.split(",")
        cluster_info = {attrs[i]:line[i] for i in range(0, len(attrs))}
        time = int(cluster_info["cluster_id"].split("_")[0])
        if not time in time_slices:
            time_slices[time] = []
        time_slices[time].append(cluster_info)
        times.add(time)
    times = list(times)
    times.sort()

    # For each time slice: assign an ordering to each cluster in that timeslice.
    ordering_lookup = {}
    order_cnt = 0
    for ti in range(0, len(times)):
        if ti == 0:
            for cluster in time_slices[times[ti]]:
                ordering_lookup[cluster["cluster_id"]] = order_cnt
                order_cnt += 1
        else:
            # Sort clusters by back cluster id
            clusters = [(ordering_lookup[cluster["back_cluster_id"]], cluster) for cluster in time_slices[times[ti]]]
            clusters.sort() # Sort on back_cluster_id
            for cluster in clusters:
                ordering_lookup[cluster[1]["cluster_id"]] = order_cnt
                order_cnt += 1

    # Output cluster data file with ordering information.
    new_content = ",".join(attrs) + ",order\n"
    for line in content:
        cluster_info = {attrs[i]:line.split(",")[i] for i in range(0, len(attrs))}
        new_content += line + "," + str(ordering_lookup[cluster_info["cluster_id"]]) + "\n"
    new_content = new_content.strip("\n")
    return new_content

def main():
    cluster_data = sys.argv[1]

    with open(cluster_data, "r") as fp:
        content = fp.read().strip()
        content = content.split("\n")
        attrs = content[0].split(",")
        content = content[1:]
    print attrs
    time_slices = {}
    times = set([])
    for line in content:
        cluster_info = {attrs[i]:line.split(",")[i] for i in range(0, len(attrs))}
        time = int(cluster_info["cluster_id"].split("_")[0])
        if not time in time_slices:
            time_slices[time] = []
        time_slices[time].append(cluster_info)
        times.add(time)
    times = list(times)
    times.sort()

    # For each time slice: assign an ordering to each cluster in that timeslice.
    ordering_lookup = {}
    order_cnt = 0
    for ti in range(0, len(times)):
        if ti == 0:
            for cluster in time_slices[times[ti]]:
                ordering_lookup[cluster["cluster_id"]] = order_cnt
                order_cnt += 1
        else:
            # Sort clusters by back cluster id
            clusters = [(ordering_lookup[cluster["back_cluster_id"]], cluster) for cluster in time_slices[times[ti]]]
            clusters.sort() # Sort on back_cluster_id
            for cluster in clusters:
                ordering_lookup[cluster[1]["cluster_id"]] = order_cnt
                order_cnt += 1

    # Output cluster data file with ordering information.
    new_content = ",".join(attrs) + ",order\n"
    for line in content:
        cluster_info = {attrs[i]:line.split(",")[i] for i in range(0, len(attrs))}
        new_content += line + "," + str(ordering_lookup[cluster_info["cluster_id"]]) + "\n"
    new_content = new_content.strip("\n")
    with open("ordered_cluster_data.csv", "w") as fp:
        fp.write(new_content)

if __name__ == "__main__":
    main()
