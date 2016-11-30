// Tree lines:
// 1) Line out from back cluster (if hasn't been drawn already)  |
// 2) Horizontal line used to line up previous line with center of current cluster. ---
// 3) Vertical line from previous line to current cluster center.
// backClusterID = cluster.backClusterID;
// backCluster = clusterLookup[backClusterID];
// if (!hasTreeBranch.has(backClusterID)) {
//   // 1) Draw line out of back cluster.
//   backClusterCanvas.append("line")
//                    .attr({"x1": xScale(backCluster["x_loc"] + (0.5 * backCluster["num_orgs"] * organismWidth)),
//                           "y1": yScale(backCluster["y_loc"] + timeSliceHeight),
//                           "x2": xScale(backCluster["x_loc"] + (0.5 * backCluster["num_orgs"] * organismWidth)),
//                           //"y2": yScale(backCluster["y_loc"] + timeSliceHeight + (0.5 * timeSliceSpace)),
//                           "y2": yScale(backCluster["y_loc"] + timeSliceHeight + backCluster["outgoing_line_offset"]),
//                           "stroke": "black",
//                           "stroke-width": "1"
//                         });
// }
// // 2) Draw line over to from line (1) to current cluster center.
// backClusterCanvas.append("line")
//                  .attr({"x1": xScale(backCluster["x_loc"] + (0.5 * backCluster["num_orgs"] * organismWidth)),
//                         //"y1": yScale(backCluster["y_loc"] + timeSliceHeight + (0.5 * timeSliceSpace)),
//                         "y1": yScale(backCluster["y_loc"] + timeSliceHeight + backCluster["outgoing_line_offset"]),
//                         "x2": xScale(clusterOffset + (0.5 * clusterOrgs.length * organismWidth)),
//                         //"y2": yScale(backCluster["y_loc"] + timeSliceHeight + (0.5 * timeSliceSpace)),
//                         "y2": yScale(backCluster["y_loc"] + timeSliceHeight + backCluster["outgoing_line_offset"]),
//                         "stroke": "black",
//                         "stroke-width": "1"
//                       });
// // // 3) Draw line from (2) to current cluster.
// backClusterCanvas.append("line")
//                  .attr({"x1": xScale(clusterOffset + (0.5 * clusterOrgs.length * organismWidth)),
//                         //"y1": yScale(backCluster["y_loc"] + timeSliceHeight + (0.5 * timeSliceSpace)),
//                         "y1": yScale(backCluster["y_loc"] + timeSliceHeight + backCluster["outgoing_line_offset"]),
//                         "x2": xScale(clusterOffset + (0.5 * clusterOrgs.length * organismWidth)),
//                         "y2": yScale(yStart),
//                         "stroke": "black",
//                         "stroke-width": "1"
//                       });
