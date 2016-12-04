var clusterDataFPath = "data/flat_clusterinfo.csv"
var orgDataFPath = "data/flat_orgdata.csv"
var clusterAccuracyFPath = "data/accuracy_table.csv"

var defaultTreatmentCode = "limited_res__rep_1: db_cluster__ep_0p1__mp_5__mode_phenotype";
var treatmentCodes = [];
var currentTreatmentCode = defaultTreatmentCode;

var codeToHumanReadableSelections = {
  "limited_res__rep_1: db_cluster__ep_0p1__mp_5__mode_both": "Example 1: DBScan, eps = 0.1, minpts = 5, similarity metric: combination",
  "limited_res__rep_1: db_cluster__ep_0p1__mp_5__mode_genotype": "Example 1: DBScan, eps = 0.1, minpts = 5, similarity metric: genotype",
  "limited_res__rep_1: db_cluster__ep_0p1__mp_5__mode_phenotype": "Example 1: DBScan, eps = 0.1, minpts = 5, similarity metric: phenotype",
  "limited_res__rep_1: spec_cluster__nc_6__mode_both": "Example 1: Spectral, Cluster # = 6, similarity metric: genotype",
  "limited_res__rep_1: spec_cluster__nc_6__mode_genotype": "Example 1: Spectral, Cluster # = 6, similarity metric: genotype",
  "limited_res__rep_1: spec_cluster__nc_6__mode_phenotype": "Example 1: Spectral, Cluster # = 6, similarity metric: genotype",
  "limited_res__rep_2: db_cluster__ep_0p1__mp_5__mode_both": "Example 2: DBScan, eps = 0.1, minpts = 5, similarity metric: combination",
  "limited_res__rep_2: db_cluster__ep_0p1__mp_5__mode_genotype": "Example 2: DBScan, eps = 0.1, minpts = 5, similarity metric: genotype",
  "limited_res__rep_2: db_cluster__ep_0p1__mp_5__mode_phenotype": "Example 2: DBScan, eps = 0.1, minpts = 5, similarity metric: phenotype",
  "limited_res__rep_2: spec_cluster__nc_6__mode_both": "Example 2: Spectral, Cluster # = 6, similarity metric: combination",
  "limited_res__rep_2: spec_cluster__nc_6__mode_genotype": "Example 2: Spectral, Cluster # = 6, similarity metric: genotype",
  "limited_res__rep_2: spec_cluster__nc_6__mode_phenotype": "Example 2: Spectral, Cluster # = 6, similarity metric: phenotype"
}
var humanReadableToCodeSelections = {
  "Example 1: DBScan, eps = 0.1, minpts = 5, similarity metric: combination": "limited_res__rep_1: db_cluster__ep_0p1__mp_5__mode_both",
  "Example 1: DBScan, eps = 0.1, minpts = 5, similarity metric: genotype": "limited_res__rep_1: db_cluster__ep_0p1__mp_5__mode_genotype",
  "Example 1: DBScan, eps = 0.1, minpts = 5, similarity metric: phenotype": "limited_res__rep_1: db_cluster__ep_0p1__mp_5__mode_phenotype",
  "Example 1: Spectral, Cluster # = 6, similarity metric: genotype": "limited_res__rep_1: spec_cluster__nc_6__mode_both",
  "Example 1: Spectral, Cluster # = 6, similarity metric: genotype": "limited_res__rep_1: spec_cluster__nc_6__mode_genotype",
  "Example 1: Spectral, Cluster # = 6, similarity metric: genotype": "limited_res__rep_1: spec_cluster__nc_6__mode_phenotype",
  "Example 2: DBScan, eps = 0.1, minpts = 5, similarity metric: combination": "limited_res__rep_2: db_cluster__ep_0p1__mp_5__mode_both",
  "Example 2: DBScan, eps = 0.1, minpts = 5, similarity metric: genotype": "limited_res__rep_2: db_cluster__ep_0p1__mp_5__mode_genotype",
  "Example 2: DBScan, eps = 0.1, minpts = 5, similarity metric: phenotype": "limited_res__rep_2: db_cluster__ep_0p1__mp_5__mode_phenotype",
  "Example 2: Spectral, Cluster # = 6, similarity metric: combination": "limited_res__rep_2: spec_cluster__nc_6__mode_both",
  "Example 2: Spectral, Cluster # = 6, similarity metric: genotype": "limited_res__rep_2: spec_cluster__nc_6__mode_genotype",
  "Example 2: Spectral, Cluster # = 6, similarity metric: phenotype": "limited_res__rep_2: spec_cluster__nc_6__mode_phenotype"
}

var margin = {top: 20, right: 20, bottom: 20, left: 20};
var frameWidth = 940;
var frameHeight = 1500;
var canvasWidth = frameWidth - margin.left - margin.right;
var canvasHeight = frameHeight - margin.top - margin.bottom;

var tooltip = d3.select("body")
                        .append("div")
                        .attr({"class": "well"})
                        .style("position", "absolute")
                        .style("z-index", "10")
                        .style("visibility", "hidden");

var cb_colors = ['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#ffff33','#a65628','#f781bf','#999999'];
var GetColor = function(i) { return cb_colors[i % cb_colors.length]; }

var timeSliceHeight = 80;
var timeSliceSpace = 150;
var organismWidth = 20;

var orgData = null;
var clusterData = null;
var clusterAccuracyData = null;
var ancestorLookup = {};
var clusterLookup = {}; // cluster: {x: <>, y: <>, size: <>}
var validTimes = new Set();
var maxPopulationSize = 3000;


var buildOrgToolTipHTML = function(org) {
  var content = "<ul class='list-unstyled'>" +
    "<li>" + "Genotype ID: " + org.orgID + "</li>" +
    "<li>" + "Cluster ID: " + org.clusterID + "</li>" +
    "<li>" + "Fitness: " + org.fitness + "</li>" +
    "<li>" + "Viability (0/1): " + org.viable + "</li>" +
    "<li>" + "Generation Length: " + org.generationLength + "</li>" +
    "<li>" + "Phenotype Signature: " + org.phenotypeSignature + "</li>" +
  "</ul>";

  return content;
}

var buildClusterRelationToolTipHTML = function(cluster) {

  var content = "<ul class='list-unstyled'>" +
    "<li>" + "Cluster Relationship: " + cluster.backClusterID + " &#8594; " + cluster.clusterID + "</li>" +
    "<li>" + "Time: " + cluster.backClusterID.split("_")[0] + " &#8594; "  + cluster.time + "</li>" +
    "<li>" + "Number Predictions Correct: " + cluster.numCorrect + "</li>" +
    "<li>" + "Number Predictions Wrong: " + cluster.numWrong + "</li>" +
    "<li>" + "Prediction Accuracy: " + cluster.percentCorrect + "</li>" +
  "</ul>";
  return content;
}

var orgDataAccessor = function(row) {
  var treatment = row.treatment;
  var cluster_params = row.cluster_params;
  var orgID = row.genotype_id;
  var time = row.time;
  var clusterID = row.cluster_id;
  var ancestor = row.ancestor_id;
  var genome = row.genome_sequence;
  var viable = row.is_viable;
  var generationLength = row.gestation_time;
  var fitness = row.fitness;
  var phenotypeSignature = row.phenotype_signature;
  var not = row.not;
  var nand = row.nand;
  var and = row.and;
  var ornot = row.ornot;
  var andnot = row.andnot;
  var nor = row.nor;
  var xor = row.xor;
  var equals = row.equals;

  var treatmentCode = treatment + ": " + cluster_params;
  if (treatmentCodes.indexOf(treatmentCode) == -1) {
    treatmentCodes.push(treatmentCode);
  }

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
    ancestor: ancestor,
    genome: genome,
    viable: viable,
    generationLength: generationLength,
    fitness: fitness,
    phenotypeSignature: phenotypeSignature,
    not: not,
    nand: nand,
    and: and,
    ornot: ornot,
    andnot: andnot,
    nor: nor,
    xor: xor,
    equals: equals,
    treatment: treatment,
    clusterParams: cluster_params
  };
}

var clusterDataAccessor = function(row) {
  var treatment = row.treatment;
  var cluster_params = row.cluster_params;
  var clusterID = row.cluster_id;
  var time = row.time;
  var backClusterID = row.back_cluster_id;
  var order = row.order;
  var numCorrect = Number(row.num_correct);
  var numWrong = Number(row.num_wrong);
  var total = Number(row.total);
  var percentCorrect = numCorrect / total;
  if (!clusterLookup.hasOwnProperty(clusterID)) {
    clusterLookup[clusterID] = {};
  }
  return {
    clusterID: clusterID,
    time: time,
    backClusterID: backClusterID,
    order: order,
    numCorrect: numCorrect,
    numWrong: numWrong,
    total: total,
    percentCorrect: percentCorrect,
    treatment: treatment,
    clusterParams: cluster_params
  };
}

var clusterAccuracyDataAccessor = function(row) {
  var treatment = row.treatment;
  var clusterParams = row.cluster_params;
  var time = row.time;
  var accuracy = row.accuracy;
  var numCorrect = Number(row.num_correct);
  var numWrong = Number(row.num_wrong);
  var total = numCorrect + numWrong;
  return {
    treatment: treatment,
    clusterParams: clusterParams,
    time: time,
    accuracy: accuracy,
    numCorrect: numCorrect,
    numWrong: numWrong,
    total: total
  }
}

var runVisualization = function() {
  console.log("Running visualization!");
  // Setup the canvas.
  var chartArea = d3.select("#chart_area");
  var frame = chartArea.append("svg");
  var canvas = frame.append("g");
  var dataCanvas = canvas.append("g").attr({"class": "data_canvas"});

  //////// Visualization functions ////////
  var refreshDashboard = function() {
    /* The function refreshes the visualization dashboard. */
    // Update treatment dropdown text.
    var treatmentDropDownButton = $("#treatment_selector").text(codeToHumanReadableSelections[currentTreatmentCode]);
  }
  var treatmentDropdownCallback = function() {
    /* Called on treatment drop down click. */
    var selection = $(this).attr("value");
    // Update the current treatment
    currentTreatmentCode = selection;
    // Refresh the dashboard.
    refreshDashboard();
    // Redraw the visualization.
    update();
  }

  /*
    Create accuracy table.
  */
  var accur_table = $("#accuracy_table");
  var table_content = "<tr><th>Experiment</th><th>Cluster Details</th><th>Accuracy</th><th>N</th></tr>";
  accurData = clusterAccuracyData.filter(function(d) {
                                              return d.time == "total";
                                             });
  for (var ei = 0; ei < accurData.length; ei++) {
    table_content += "<tr>";
    table_content += "<td>" + accurData[ei].treatment + "</td>" // Experiment (treatment)
    table_content += "<td>" + accurData[ei].clusterParams + "</td>" // Cluster parameters (clusterParams)
    table_content += "<td>" + accurData[ei].accuracy + "</td>" // Accuracy (accuracy)
    table_content += "<td>" + accurData[ei].total + "</td>" // N (total)
    table_content += "</tr>";
  }
  accur_table.html(table_content);

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
    // Filter data based on treatment code
    var curTreatment = currentTreatmentCode.split(": ")[0];
    var curClusterParams = currentTreatmentCode.split(": ")[1];
    //  * Filter cluster data
    var filteredClusterData = clusterData.filter(function(d) { return d.treatment == curTreatment && d.clusterParams == curClusterParams; })
    //  * Filter organism data
    var filteredOrgData = orgData.filter(function(d) { return d.treatment == curTreatment && d.clusterParams == curClusterParams; });
    for (var t = 0; t < timeSeries.length; t++) {
      var time = timeSeries[t];
      var timeCanvas = dataCanvas.append("g").attr({"class": "time_canvas"});
      var yStart = t * (timeSliceSpace + timeSliceHeight); // Local starting Y
      // TODO: Append some text (time) @ yStart
      timeCanvas.append("text").attr({"class": "time_tick",
                                      "x": -5,
                                      "y": yScale(yStart + timeSliceHeight),
                                      "transform": "rotate(-90," + -5 + "," + yScale(yStart + timeSliceHeight) + ")"})
                                .text(time);
      // Get the clusters relevant to this time point.
      var curClusters = filteredClusterData.filter(function(d) { return d.time == time; });
      // Sort clusters by order.
      curClusters.sort(function(a, b) { return a.order - b.order; });
      // Get the organisms relevant to this time point.
      var curOrgs = filteredOrgData.filter(function(d) { return d.time == time; });
      // For each cluster at this time point:
      var clusterOffset = 0;
      var minOffset = timeSliceSpace * 0.25;
      var maxOffset = timeSliceSpace * 0.5;
      var orderRange = [curClusters[0].order, curClusters[curClusters.length - 1].order];
      for (var ci = 0; ci < curClusters.length; ci++) {
        var cluster = curClusters[ci];
        // Get organisms that make up this cluster.
        var clusterOrgs = curOrgs.filter(function(d) { return d.clusterID == cluster.clusterID; });
        // Draw cluster as box.
        var clusterColor = GetColor(parseInt(cluster.clusterID.split("_")[1]));
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
        clusterLookup[cluster.clusterID]["cluster_offset"] = clusterOffset;
        var treeOffset = null;
        if ((orderRange[1] - orderRange[0]) == 0) { treeOffset = minOffset; }
        else {
          treeOffset = ((cluster.order - orderRange[0]) / (orderRange[1] - orderRange[0])) * (maxOffset - minOffset) + minOffset;
        }

        clusterLookup[cluster.clusterID]["outgoing_line_offset"] = treeOffset;
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
                   "fill": clusterColor,
                   "stroke-width": 0
                  });
        // Add tool tips for organisms
        orgs.on("mouseover", function(d) { return tooltip.style("visibility", "visible").html(buildOrgToolTipHTML(d)); })
            .on("mousemove", function(d) { return tooltip.style("top", (event.pageY-10)+"px").style("left",(event.pageX+10)+"px"); })
            .on("mouseout", function(d) { return tooltip.style("visibility", "hidden"); });
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
                                      "stroke-width": "0.25",
                                      "class": "ancestor_line"
                                    });
        }
        clusterOffset += (clusterOrgs.length * organismWidth);
      }

      // Draw back clusters lines
      // Draw line from clusters to back cluster.
      // 1) filter out back_cluster_id = 'none's
      // 2) draw line
      var clusterRelations = curClusters.filter(function(d) { return d.backClusterID != "none" && d.backClusterID.split("_")[1] != "NONE"; });
      var clusterRelationCanvas = timeCanvas.append("g").attr({"class": "cluster_relation_canvas"});
      var backClusterRelations = clusterRelationCanvas.selectAll("line").data(clusterRelations);
      backClusterRelations.enter().append("line");
      backClusterRelations.exit().remove();
      backClusterRelations.attr({"x1": function(d) { return xScale(clusterLookup[d.clusterID]["cluster_offset"] + (0.5 * clusterLookup[d.clusterID]["num_orgs"] * organismWidth)); },
                                 "y1": function(d) { return yScale(yStart); },
                                 "x2": function(d) { return xScale(clusterLookup[d.backClusterID]["x_loc"] + (0.5 * clusterLookup[d.backClusterID]["num_orgs"] * organismWidth))},
                                 "y2": function(d) { return yScale(clusterLookup[d.backClusterID]["y_loc"] + timeSliceHeight); },
                                 "stroke": "black",
                                 "stroke-width": "2",
                                 "class": "back_cluster_line"});
      backClusterRelations.on("mouseover", function(d) { return tooltip.style("visibility", "visible").html(buildClusterRelationToolTipHTML(d)); })
                .on("mousemove", function(d) { return tooltip.style("top", (event.pageY-10)+"px").style("left",(event.pageX+10)+"px"); })
                .on("mouseout", function(d) { return tooltip.style("visibility", "hidden"); });
    }
  }

  //////// Build dashboard ////////
  // Populate the treatment dropdown.
  var treatmentDropdown = $("#treatment-selection-dropdown");
  treatmentDropdown.empty();
  $.each(treatmentCodes, function(i, p) {
    var li = $("<li/>")
              .appendTo(treatmentDropdown);
    var a = $("<a/>")
              .attr({"value": this, "href": "#"})
              .text(codeToHumanReadableSelections[this])
              .appendTo(li);
  });
  var treatmentDropdownButton = $("#treatment_selector").text(codeToHumanReadableSelections[currentTreatmentCode]);
  $("<span/>").attr({"class": "caret"}).appendTo(treatmentDropdownButton);
  // Setup component listeners.
  $(document).ready(function() {
    // Treatment dropdown listener.
    $("#treatment-selection-dropdown li a").click(treatmentDropdownCallback);
    $(window).resize(function() {
      update();
    });
  });

  update();

}

var main = function() {
  // Load in both cluster data and organism data.
  d3_queue.queue(2)
    .defer(d3.csv, orgDataFPath, orgDataAccessor)
    .defer(d3.csv, clusterDataFPath, clusterDataAccessor)
    .defer(d3.csv, clusterAccuracyFPath, clusterAccuracyDataAccessor)
    .await(function(error, oData, cData, aData) {
      if (error) throw error;
      orgData = oData;
      clusterData = cData;
      clusterAccuracyData = aData;
      runVisualization();
    });
}

main();
