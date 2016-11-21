var clusterDataFPath = "data/ordered_cluster_data.csv"
var orgDataFPath = "data/testorgdata.csv"

var margin = {top: 20, right: 20, bottom: 20, left: 20};
var frameWidth = 940;
var frameHeight = 1500;
var canvasWidth = frameWidth - margin.left - margin.right;
var canvasHeight = frameHeight - margin.top - margin.bottom;

var tempColors = ["red", "green", "blue", "orange", "white"];

var timeSliceHeight = 80;
var timeSliceSpace = 150;
var organismWidth = 10;

var orgData = null;
var clusterData = null;
var ancestorLookup = {};
var clusterLookup = {}; // cluster: {x: <>, y: <>, size: <>}
var validTimes = new Set();
var maxPopulationSize = 500;

var orgDataAccessor = function(row) {
  var orgID = row.org_id;
  var time = row.time;
  var clusterID = row.cluster_id;
  var ancestor = row.ancestor_id;
  // Keep track of each time point.
  validTimes.add(time);
  // Keep track of ancestor organisms.
  if (!ancestorLookup.hasOwnProperty(ancestor)) {
    ancestorLookup[ancestor] = {};
  }
  return {
    orgID: orgID,
    time: time,
    clusterID: clusterID,
    ancestor: ancestor
  };
}

var clusterDataAccessor = function(row) {
  var clusterID = row.cluster_id;
  var time = row.time;
  var backClusterID = row.back_cluster_id;
  var order = row.order;
  if (!clusterLookup.hasOwnProperty(clusterID)) {
    clusterLookup[clusterID] = {};
  }
  return {
    clusterID: clusterID,
    time: time,
    backClusterID: backClusterID,
    order: order
  };
}

var runVisualization = function() {
  console.log("Running visualization!");
  // Setup the canvas.
  var chartArea = d3.select("#chart_area");
  var frame = chartArea.append("svg");
  var canvas = frame.append("g");
  var dataCanvas = canvas.append("g").attr({"class": "data_canvas"});

  var update = function() {
    /*
      Call this function to (re)draw data to screen.
    */

    // Sort time points.
    var timeSeries = [];
    validTimes.forEach(function(val) { timeSeries.push(val); });
    timeSeries.sort(function(a, b) { return a - b; });

    // Update frame/canvas parameters.
    frameWidth = $("#vis_panel").width() - 20;
    frameHeight = timeSeries.length * (timeSliceSpace + timeSliceHeight);
    canvasWidth = frameWidth - margin.left - margin.right;
    canvasHeight = frameHeight - margin.top - margin.bottom;
    frame.attr({"width": frameWidth, "height": frameHeight});
    canvas.attr({"transform": "translate(" + margin.left + "," + margin.top + ")"});
    xDomain = [0, maxPopulationSize * organismWidth]; // Range of values
    yDomain = [0, timeSeries.length * (timeSliceHeight + timeSliceSpace)];

    // Update axes
    // X-AXIS
    // Cleanup old axes.
    canvas.selectAll("g.x_axis").remove();
    // Setup new x-axis
    var xScale = d3.scale.linear();
    xScale.domain(xDomain).range([0, canvasWidth]);
    var xAxis = d3.svg.axis().scale(xScale).tickValues([]).orient("top");
    canvas.append("g").attr({"class": "x_axis"}).call(xAxis);
    // Y-AXIS
    // Clean up old axes.
    canvas.selectAll("g.y_axis").remove();
    // Setup new y-axis.
    var yScale = d3.scale.linear();
    yScale.domain(yDomain).range([0, canvasHeight]);
    var yAxis = d3.svg.axis().scale(yScale).tickValues([]).orient("left");
    canvas.append("g").attr({"class": "y_axis"}).call(yAxis);

    // Draw Data
    // Cleanup old data.
    dataCanvas.selectAll("g").remove();
    var hasTreeBranch = new Set(); // Keeps track of if we've already drawn the out-going tree branch for a cluster.
    for (var t = 0; t < timeSeries.length; t++) {
      var time = timeSeries[t];
      var timeCanvas = dataCanvas.append("g").attr({"class": "time_canvas"});
      var yStart = t * (timeSliceSpace + timeSliceHeight); // Local starting Y
      // Get the clusters relevant to this time point.
      var curClusters = clusterData.filter(function(d) { return d.time == time; });
      // Sort clusters by order.
      curClusters.sort(function(a, b) { return a.order - b.order; });
      // Get the organisms relevant to this time point.
      var curOrgs = orgData.filter(function(d) { return d.time == time; });
      // For each cluster at thie time point:
      var clusterOffset = 0;
      var minOffset = timeSliceSpace * 0.25;
      var maxOffset = timeSliceSpace * 0.5;
      var orderRange = [curClusters[0].order, curClusters[curClusters.length - 1].order];
      for (var ci = 0; ci < curClusters.length; ci++) {
        var cluster = curClusters[ci];
        // Get organisms that make up this cluster.
        var clusterOrgs = curOrgs.filter(function(d) { return d.clusterID == cluster.clusterID; });
        // Draw cluster as box.
        var clusterColor = tempColors[parseInt(cluster.clusterID.split("_")[1])];
        timeCanvas.append("rect")
                  .attr({"width": xScale(clusterOrgs.length * organismWidth),
                         "height": yScale(timeSliceHeight),
                         "x": xScale(clusterOffset),
                         "y": yScale(yStart),
                         "class": "cluster_rect",
                         "id": cluster.clusterID,
                         "fill": clusterColor
                        });
        // Record cluster info for future clusters to use.
        clusterLookup[cluster.clusterID]["x_loc"] = clusterOffset;
        clusterLookup[cluster.clusterID]["y_loc"] = yStart;
        clusterLookup[cluster.clusterID]["num_orgs"] = clusterOrgs.length;
        var treeOffset = null;
        if ((orderRange[1] - orderRange[0]) == 0) { treeOffset = minOffset; }
        else {
          treeOffset = ((cluster.order - orderRange[0]) / (orderRange[1] - orderRange[0])) * (maxOffset - minOffset) + minOffset;
        }
        //console.log("==========");
        // console.log(orderRange);
        // console.log(cluster.order);
        // console.log(minOffset);
        // console.log(maxOffset);
        clusterLookup[cluster.clusterID]["outgoing_line_offset"] = treeOffset;
        //console.log(treeOffset);
        // Draw organisms.
        var clusterCanvas = timeCanvas.append("g").attr({"class": "cluster_canvas"});
        var orgs = clusterCanvas.selectAll("rect").data(clusterOrgs);
        orgs.enter().append("rect");
        orgs.exit().remove();
        orgs.attr({"y": function(d, i) {
                          // If this organism is an ancestor, store its y location.
                          yLoc = yStart;
                          if (ancestorLookup.hasOwnProperty(d.orgID)) {
                            ancestorLookup[d.orgID]["y_loc"] = yLoc
                          }
                          return yScale(yLoc);
                        },
                   "x": function(d, i) {
                          // If this organism is an ancestor, store its x location.
                          xLoc = clusterOffset + (i * organismWidth);
                          if (ancestorLookup.hasOwnProperty(d.orgID)) {
                            ancestorLookup[d.orgID]["x_loc"] = xLoc
                          }
                          return xScale(xLoc);
                        },
                   "width": function(d, i) { return xScale(organismWidth); },
                   "height": function(d, i) { return yScale(timeSliceHeight); },
                   "class": "organism_rect",
                   "id": function(d, i) { return d.orgID; },
                   "fill": clusterColor
                  });
        // Draw line from organism to organism's ancestor.
        if (t > 0) {  // Don't draw these relationships for first time slice.
          var ancestorRelationshipCanvas = clusterCanvas.append("g");
          var ancestorRelationships = ancestorRelationshipCanvas.selectAll("line").data(clusterOrgs);
          ancestorRelationships.enter().append("line");
          ancestorRelationships.exit().remove();
          ancestorRelationships.attr({"x1": function(d, i) { return xScale((clusterOffset + (i * organismWidth)) + 0.5 * organismWidth); },
                                      "y1": function(d, i) { return yScale(yStart); },
                                      "x2": function(d, i) { return xScale(ancestorLookup[d.ancestor]["x_loc"] + 0.5 * organismWidth); },
                                      "y2": function(d, i) { return yScale(ancestorLookup[d.ancestor]["y_loc"] + timeSliceHeight); },
                                      "stroke": "gray",
                                      "stroke-width": "0.25"
                                     });
        }
        // Draw line from current cluster to back cluster.
        if (t > 0) { // Don't draw these relationships for first slice.
          var backClusterCanvas = clusterCanvas.append("g");
          // Straight lines:
          backClusterCanvas.append("line")
                           .attr({"x1": function(d, i) { return xScale(clusterOffset + (0.5 * clusterOrgs.length * organismWidth)); },
                                  "y1": function(d, i) { return yScale(yStart); },
                                  "x2": function(d, i) { return xScale(clusterLookup[cluster.backClusterID]["x_loc"] + (0.5 * clusterLookup[cluster.backClusterID]["num_orgs"] * organismWidth)); },
                                  "y2": function(d, i) { return yScale(clusterLookup[cluster.backClusterID]["y_loc"] + timeSliceHeight); },
                                  "stroke": "black",
                                  "stroke-width": "2"
                                  });
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

        }
        clusterOffset += (clusterOrgs.length * organismWidth);
      }
    }
  }
  update();

}

var main = function() {
  // Load in both cluster data and organism data.
  d3_queue.queue(2)
    .defer(d3.csv, orgDataFPath, orgDataAccessor)
    .defer(d3.csv, clusterDataFPath, clusterDataAccessor)
    .await(function(error, oData, cData) {
      if (error) throw error;
      orgData = oData;
      clusterData = cData;
      runVisualization();
    });
}

main();
