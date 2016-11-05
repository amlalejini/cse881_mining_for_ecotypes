var clusterDataFPath = "data/testclusterdata.csv"
var orgDataFPath = "data/testorgdata.csv"

var margin = {top: 20, right: 20, bottom: 20, left: 20};
var frameWidth = 940;
var frameHeight = 1500;
var canvasWidth = frameWidth - margin.left - margin.right;
var canvasHeight = frameHeight - margin.top - margin.bottom;

var tempColors = ["red", "green", "blue", "orange", "white"];

var timeSliceHeight = 50;
var timeSliceSpace = 40;
var organismWidth = 10;

var orgData = null;
var clusterData = null;
var ancestorLookup = {};
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
  return {
    clusterID: clusterID,
    time: time,
    backClusterID
  };
}

var runVisualization = function() {
  console.log("Running visualization!");
  console.log("Org data: "); console.log(orgData);
  console.log("Cluster data: "); console.log(clusterData);
  console.log("ancestors: "); console.log(ancestorLookup);
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
    for (var t = 0; t < timeSeries.length; t++) {
      var time = timeSeries[t];
      var timeCanvas = dataCanvas.append("g").attr({"class": "time_canvas"});
      var yStart = t * (timeSliceSpace + timeSliceHeight); // Local starting Y
      // Get the clusters relevant to this time point.
      var curClusters = clusterData.filter(function(d) { return d.time == time; });
      // Get the organisms relevant to this time point.
      var curOrgs = orgData.filter(function(d) { return d.time == time; });
      // For each cluster at thie time point:
      clusterOffset = 0;
      for (var ci = 0; ci < curClusters.length; ci++) {
        cluster = curClusters[ci];
        // Get organisms that make up this cluster.
        clusterOrgs = curOrgs.filter(function(d) { return d.clusterID == cluster.clusterID; });
        // Draw cluster as box.
        clusterColor = tempColors[parseInt(cluster.clusterID.split("_")[1])];
        timeCanvas.append("rect")
                  .attr({"width": xScale(clusterOrgs.length * organismWidth),
                         "height": yScale(timeSliceHeight),
                         "x": xScale(clusterOffset),
                         "y": yScale(yStart),
                         "class": "cluster_rect",
                         "id": cluster.clusterID,
                         "fill": clusterColor
                        });
        // TODO: Draw organisms.
        var clusterCanvas = timeCanvas.append("g").attr({"class": "cluster_canvas"});
        var orgs = clusterCanvas.selectAll("rect").data(clusterOrgs);
        orgs.enter().append("rect");
        orgs.exit().remove();
        orgs.attr({"y": function(d, i) { return yScale(yStart); },
                   "x": function(d, i) { return xScale(clusterOffset + (i * organismWidth)); },
                   "width": function(d, i) { return xScale(organismWidth); },
                   "height": function(d, i) { return yScale(timeSliceHeight); },
                   "class": "organism_rect",
                   "id": function(d, i) { return d.orgID; },
                   "fill": clusterColor
                  });
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
