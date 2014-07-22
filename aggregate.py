""" This is a command line runner for rank aggregation. 
    Author: Sibel Adali

    To learn about how to run, simply type:

    python aggregate.py

"""

import sys
import rank_aggregators as r

def print_menu():
        print "Usage: python aggregate.py inputfile aggregator <list of iterative algorithms>"
        print "Aggregator list:"
        print "\tin: indegree"
        print "\tpg alpha: pagerank with given alpha (float between 0-1, default 0.85)"
        print "\trnd k: random with k tries"
        print
        print "Iterative algorithms (executed in the order given)"
        print "\tigf: iterative greedy flip"
        print "\tibf k: iterative best flip (at most k (integer, default 1) rounds"
        print "\tir k: iterative remove up to k (integer, default 1) rankers"
        print
        print "Example: python aggregate.py pg 0.85 ibf"
        print "\tPagerank, followed by ibf"
        print "Example: python aggregate.py in ir 5 ibf"
        print "\tIndegree followed by iterative remove, followed by ibf"

def print_error(msg):
    print
    print "*" * (len(msg)+10)
    print "ERROR >>>", msg
    print "*" * (len(msg)+10)
    print
    print_menu()
    print
    sys.exit()

if __name__ == "__main__":
    if len(sys.argv) <3:
        print_menu()
        sys.exit()

    fname = sys.argv[1]
    try:
        (objects,ranker_names) = r.read_rankers(fname)
    except:
        print_error("Incorrect file provided, cannot read rankers")

    agg = sys.argv[2]
    arguments = sys.argv[3:]
    
    lastloc = 0
    if agg == 'pg':
        alpha = 0.85
        if len(arguments)>0:
            try:
                alpha = float(arguments[0])
                lastloc = 1
            except:
                print_error("Incorrect alpha provided or alpha is omitted")
        ranker, score = r.pagerank_aggregator(objects, 0.000001, alpha)
        print "Pagerank algorithm, alpha =", alpha, ", score:", score

    elif agg == 'in':
        ranker, score = r.indegree_aggregator(objects)
        print "Indegree algorithm, score:", score

    elif agg == 'rnd':
        k=1
        if len(arguments)>0:
            try:
                k = int(arguments[0])
                lastloc = 1
            except:
                print_error("An integer for the number of tries is required")
        print "Random rank algorithm with k =", k
        ranker, score = r.best_random_aggregator(objects, k)
    else:
        print_error("No valid rank aggregation algorithm found")

    arguments = arguments[lastloc:]

    while len(arguments) > 0:
        agg = arguments[0]
        lastloc = 1
        if agg == 'ibf':
            newranker, score = r.iterative_best_flip(objects, ranker)
            print "Iterative best flip, score:", score

        elif agg in ['igf','ir']:
            k = 1
            if len(arguments) > 1:
                try:
                    k = int(arguments[1])
                    lastloc = 2
                except:
                    print_error("An integer k value is needed for algorithm" + agg)
            if agg == 'igf':
                newranker, score, flipped = r.iterative_greedy_flip(objects, ranker, k)
                print "Iterative greedy flip with k =", k, "score:", score
            else:
                newranker, score,  removed, newobjects = r.remove_top_k(objects, ranker_names, ranker, k)
                print "Iterative best removal with k =", k, "score:", score
                objects = newobjects
                line = ""
                for item in removed:
                    line += item + ", "
                print "Removed rankers (in order):", line.strip().strip(",")
            ranker = newranker
        else:
            print_error("Unknown algorithm"+agg)

        arguments = arguments[lastloc:]

    print "Final score:", score
    print "Final ranker:"
    r.print_single_ranker(ranker)
