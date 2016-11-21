#!/usr/bin/python2

"""
Given target location, call calc dist mats on all data files.
"""

import json, os, subprocess, sys
from utilities.utilities import *

def main():
    target_dir = sys.argv[1]
    dest_dir = sys.argv[2]
    mkdir_p(dest_dir)

    pop_files = [fname for fname in os.listdir(target_dir) if "_pop_" in fname]
    for pfile in pop_files:
        dest = os.path.join(dest_dir, pfile.split(".")[0] + "__distmat.csv")
        src = os.path.join(target_dir, pfile)
        cmd = "./calcdistmats %s %s" % (src, dest)
        return_code = subprocess.call(cmd, shell = True)#, cwd = "/mnt/home/lalejini/exp_ws/cse881_mining_for_ecotypes/scripts")

if __name__ == "__main__":
    main()
