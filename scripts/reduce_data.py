
import sys, os
from utilities.utilities import *

if __name__ == "__main__":
    target_dir = sys.argv[1]
    def GetPopUpdate(name):
        return int(name.split(".")[0].split("_")[-1])
    pop_files = [fname for fname in os.listdir(target_dir) if "_pop_" in fname]
    pop_files.sort(key = lambda name: GetPopUpdate(name))
    reduced_pop_files = []
    mkdir_p(os.path.join(target_dir, "..", target_dir + "__reduced"))
    for pi in range(1, len(pop_files)):
        pop_update = GetPopUpdate(pop_files[pi])
        if pop_update % 5000 == 0:
            reduced_pop_files.append(pop_files[pi])
    for ri in range(0, len(reduced_pop_files) - 1):
        pop1 = reduced_pop_files[ri]
        pop2 = reduced_pop_files[ri + 1]
        up1 = GetPopUpdate(pop1)
        up2 = GetPopUpdate(pop2)
        tname = "trans__pops_%d_%d" % (up1, up2)
        # Get content of pop1, pop2, join.
        p1_content = None
        with open(os.path.join(target_dir, pop1)) as fp:
            p1_content = fp.read().strip("\n")
        p2_content = None
        with open(os.path.join(target_dir, pop2)) as fp:
            p2_content = fp.read().strip("\n")
        p2_content = p2_content[1:] # Strip out header in second file.
        content = p1_content + p2_content
        with open(os.path.join(target_dir, "..", target_dir + "__reduced", tname), "w") as fp:
            fp.write(content)
