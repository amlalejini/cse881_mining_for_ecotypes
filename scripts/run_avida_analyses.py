#!/usr/bin/python2

"""
This script will run Avida analysis mode for each treatment__rep specified in settings file.

Once done running Avida analyze mode for a treatment, this script will move the data to the specfied
dump location.
"""

import json, os, subprocess

def main():
    """
    Main script.
    """
    settings_fn = "params/settings.json"
    settings = None
    # Load settings from settings file.
    with open(settings_fn) as fp: settings = json.load(fp)["avida_analysis"]
    # Pull out locations of interest.
    exp_loc = settings["experiment_location"]
    configs_loc = os.path.join(exp_loc, "configs")
    analysis_scripts_loc = settings["avida_analysis_scripts_location"]
    # Treatments to analyze?
    treatments = settings["treatments"]
    # Replicates by treatment?
    reps_by_treatment = settings["replicates_by_treatment"]
    # Analyses to run?
    analyses = settings["analysis_scripts_to_run"]
    # Read in the appropriate run_list to scrape the proper arguments per treatment.
    # avida_cmd_args = None
    # with open(os.path.join(configs_loc, "run_list"), "r") as fp:
    #     avida_cmd_args = {line.split(" ")[1].split("__")[0]:line.split("./avida")[-1].replace("-s $seed ", "").strip() for line in fp if "./avida" in line}
    # Run analyses for each treatment.
    for treatment in treatments:
        print "Analyzing %s" % treatment
        # For each of the given analysis scripts, make a temporary script filled out for this treatment.
        for ascript in analyses:
            print "\tRunning %s" % ascript
            ascript_fpath = os.path.join(analysis_scripts_loc, ascript)
            ## Build temporary analysis file. ##
            temp_ascript_content = ""
            with open(ascript_fpath, "r") as fp:
                temp_ascript_content = fp.read()
            temp_ascript_content = temp_ascript_content.replace("<base_experiment_directory>", exp_loc)
            temp_ascript_content = temp_ascript_content.replace("<treatments>", treatment)
            temp_ascript_content = temp_ascript_content.replace("<replicates>", " ".join(map(str, reps_by_treatment[treatment])))
            ## Write out analysis file to run location ##
            temp_ascript = os.path.join(configs_loc, "temp_" + ascript)
            with open(temp_ascript, "w") as fp:
                fp.write(temp_ascript_content)
            ## Build Analysis command ## (test everyone in unlimited resource environment)
            cmd = "./avida -set ENVIRONMENT_FILE env_unlimited_res.cfg -a -set ANALYZE_FILE %s" % "temp_" + ascript
            ## Run Avida analysis ##
            return_code = subprocess.call(cmd, shell = True, cwd = configs_loc)
            ## Clean up analysis script ##
            return_code = subprocess.call("rm %s" % "temp_" + ascript, shell = True, cwd = configs_loc)

if __name__ == "__main__":
    main()
