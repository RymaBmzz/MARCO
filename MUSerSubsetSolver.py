import os
import tempfile
import subprocess
from MinisatSubsetSolver import MinisatSubsetSolver

class MUSerSubsetSolver(MinisatSubsetSolver):
    def __init__(self, filename):
        MinisatSubsetSolver.__init__(self, filename, store_dimacs=True)
        self.muser_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'muser2-static')
        if not os.path.isfile(self.muser_path):
            raise Exception("MUSer2 binary not found at %s" % self.muser_path)
        try:
            p = subprocess.Popen([self.muser_path])
        except:
            raise Exception("MUSer2 binary %s is not executable.\nIt may be compiled for a different platform." % self.muser_path)

    # override shrink method to use MUSer2
    def shrink(self, seed):
        # Open tmpfile
        with tempfile.NamedTemporaryFile() as cnf:
            # Write CNF
            print >>cnf, "p cnf %d %d" % (self.nvars, len(seed))
            for i in seed:
                print >>cnf, self.dimacs[i],  # dimacs[i] has newline
            cnf.flush()
            # Run MUSer
            p = subprocess.Popen([self.muser_path, '-comp', '-v', '-1', cnf.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out,err = p.communicate()
            result = out

        # Parse result
        import re
        pattern = re.compile(r'^v [\d ]+$', re.MULTILINE)
        matchline = re.search(pattern, result).group(0)
        core = [seed[int(x)-1] for x in matchline.split()[1:-1]]
        return core

