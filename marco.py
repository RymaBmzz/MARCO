#!/usr/bin/env python

import argparse
import os
import sys
from MarcoPolo import MarcoPolo

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="print more verbose output (constraint indexes)")
    parser.add_argument('-l', '--limit', type=int, default=None,
                        help="limit number of subsets output (MCSes and MUSes)")
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin,
                        help="name of file to process (STDIN if omitted)")
    type_group = parser.add_mutually_exclusive_group()
    type_group.add_argument('--cnf', action='store_true',
                        help="Treat input as DIMACS CNF format.")
    type_group.add_argument('--smt', action='store_true',
                        help="Treat input as SMT2 format.")
    parser.add_argument('--force-minisat', action='store_true',
                        help="use Minisat in place of MUSer2 (NOTE: much slower and usually not worth doing!)")
    args = parser.parse_args()

    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    infile = args.infile

    if args.smt and infile == sys.stdin:
        print >>sys.stderr, "SMT cannot be read from STDIN.  Please specify a filename."
        sys.exit(1)

    # create appropriate constraint solver
    if args.force_minisat:
        from MinisatSubsetSolver import MinisatSubsetSolver
        csolver = MinisatSubsetSolver(infile)
        infile.close()
    elif args.cnf or infile.name.endswith('.cnf') or infile.name.endswith('.cnf.gz'):
        try:
            from MUSerSubsetSolver import MUSerSubsetSolver
            csolver = MUSerSubsetSolver(infile)
        except Exception as e:
            print >>sys.stderr, "ERROR: Unable to use MUSer2 for MUS extraction.\n\n%s\n\nUse --force-minisat to use Minisat instead (NOTE: it will be much slower.)" % str(e)
            sys.exit(1)
            
        infile.close()
    elif args.smt or infile.name.endswith('.smt2') or infile.name.endswith('.smt2.gz'):
        try:
            from Z3SubsetSolver import Z3SubsetSolver
        except ImportError as e:
            print >>sys.stderr, "ERROR: Unable to import z3 module:  %s\n\nPlease install Z3 from https://z3.codeplex.com/" % str(e)
            sys.exit(1)
        # z3 has to be given a filename, not a file object, so close infile and just pass its name
        infile.close()
        csolver = Z3SubsetSolver(infile.name)
    else:
        print >>sys.stderr, \
            "Cannot determine filetype (cnf or smt) of input: %s\n" \
            "Please provide --cnf or --smt option." % infile.name
        sys.exit(1)

    # create a MarcoPolo instance with the constraint solver
    mp = MarcoPolo(csolver)

    # useful for timing just the parsing / setup
    if args.limit == 0:
        return

    # enumerate results
    lim = args.limit
    for result in mp.enumerate():
        if args.verbose:
            print result[0], " ".join([str(x+1) for x in result[1]])
        else:
            print result[0]

        if lim:
            lim -= 1
            if lim == 0: break

if __name__ == '__main__':
    main()

