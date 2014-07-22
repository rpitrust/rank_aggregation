""" Simple rank aggregation program.
    Author: Sibel Adali

    Call using::

       python rankers.py filename

    Input text file should be:
    *  comma separated
    *  contain a header row
    *  first column is the object ids, assumed to be integers
    *  each column is a separate ranker
    *  if an object is not ranked by a ranker, leave that value empty.

    Data structures used:

    Objects is a dictionary where object names are key, and the ranks with 
    respect to each ranker is a value (None if the ranker does not rank 
    a given object)

    Example: Two rankers, 3 objects (a,b,c)
    {'a': [1,1,2], 'b':[2,None,1], 'c':[None,2,3]}

    A ranker is a single value version of this, for example
    {'a': 1, 'b': 2, 'c': 3}
    Rankers are assumed to be total, i.e. have a rank for each
    object. It is not necessary for ranks to be increasing order. Ties
    are possible, but are disregarded in processing.

    To Do: 
    -----------
    1. Handle ties

"""

import sys
import random
import pagerank as pg
import time
import copy

##################################################
######### Input Output functions
##################################################
def read_rankers(fname):
    f = open(fname)
    header = f.readline()
    ranker_names = header.strip().split(",")
    ranker_names = ranker_names[1:]
    objects = {}
    oid = 0
    for line in f:
        oid += 1
        m = line.strip().split(",")
        objects[oid] = m[1:]
        for i in range(len(objects[oid])):
            if len(objects[oid][i].strip()) == 0:
                objects[oid][i] = None
            else:
                objects[oid][i] = int(objects[oid][i])
    return (objects, ranker_names)


def print_rankers(objects, ranker_names):
    line = "Obj:\t"
    for name in ranker_names:
        line += name + "\t"
    print line
    for key in objects:
        line = "%d:\t" %key
        for val in objects[key]:
            if val == None:
                line += "None\t"
            else:
                line += "%d\t" %val
        print line

def print_single_ranker(ranker):
    ranked = []
    for key in ranker.keys():
        ranked.append( (ranker[key], key) )
    ranked.sort() ## low rank is good
    for (val, key) in ranked:
        print key,
    print

##################################################
######### Evaluation: Kendall tau
##################################################

def kendall_tau(objects, cmp_ranker):
    agree = 0
    disagree = 0
    obj = objects.keys()
    n = len(obj)
    num_rankers = len(objects[obj[0]])
    for i in range(n-1):
        for j in range(i+1,n):
            key1 = obj[i]
            key2 = obj[j]
            for ranker in range(len(objects[key1])):
                r11 = objects[key1][ranker]
                r12 = objects[key2][ranker]
                if r11 != None and r12 != None:
                    r21 = cmp_ranker[key1]
                    r22 = cmp_ranker[key2]
                    if r21 != None and r22 != None:
                        if r11 > r12:
                            if r21 > r22:
                                agree += 1
                            else:
                                disagree += 1
                        elif r11 < r12:
                            if r21 < r22:
                                agree += 1
                            else:
                                disagree += 1

    return float(agree - disagree)/(0.5*n*(n-1)*num_rankers)


def compare_two(objects, key1, key2):
    """Compares only a specific pair of objects for all the rankers.
    It is assumed that key1 is lower ranked than key2 in comparison.
    Hence, a flip is ordering key2 above key1.

    """

    agree = 0
    disagree = 0
    for ranker in range(len(objects[key1])):
        r1 = objects[key1][ranker]
        r2 = objects[key2][ranker]
        if r1 != None and r2 != None:
            if r1 < r2:
                agree += 1
            elif r2 < r1:
                disagree += 1
    return agree, disagree

def kendall_tau_partial(objects, ranker, oldscore, key1, key2):
    """Computes the change in kendall tau assuming the objects
    at key1 and key2 are being switched. It updates the old
    score and sends the new score

    """

    if ranker[key1] > ranker[key2]: ##switch so that key1 is the smaller rank
        tmp = key1
        key1 = key2
        key2 = tmp


    a1,d1,a2,d2 = 0,0,0,0
    for obj in set(ranker.keys())-set([key1,key2]):
        if ranker[obj] > ranker[key1] and \
           ranker[obj] < ranker[key2]:
            a,d = compare_two(objects, key1, obj)
            a1 += a
            d1 += d
            a,d = compare_two(objects, obj, key2)
            a2 += a
            d2 += d
    a3,d3 = compare_two(objects, key1, key2)

    n = len(objects.keys())
    num_rankers = len(objects[key1])
    multiplier = (0.5*n*(n-1)*num_rankers)
    newscore = (oldscore*multiplier + 2*(d1+d2+d3) - 2*(a1+a2+a3))/multiplier
    return newscore

##################################################
######### Util functions 
##################################################

def get_ranker(objlist):
    """ Convert a permutation of objects to a ranker dictionary """
    ranker = {}
    for i in range(len(objlist)):
        key = objlist[i]
        ranker[key] = i+1
    return ranker

def get_ranker_for_scores(scores):
    """ Convert a dictionary containing scores for each object to a ranker dictionary """
    oscores = []
    for key in scores:
        oscores.append( (scores[key], key) )
    oscores.sort(reverse=True)
    objlist = []
    for (score, key) in oscores:
        objlist.append(key)
    return( get_ranker(objlist) )

def num_higher(objects, key1, key2):
    """ Counts the number of times key2 is higher than key1 in rankers. """
    count = 0
    for ranker in range(len(objects[key1])):
        x1 = objects[key1][ranker]
        x2 = objects[key2][ranker]
        if x1 != None and x2 != None and x1 > x2:
            count += 1
    return count

def remove_ranker(objects, i):
    for key in objects:
        val = objects[key]
        objects[key] = val[:i] + val[i+1:]


def switch(ranker, key1, key2):
    """ Switch the rankers given by the two keys """
    r = ranker[key1]
    ranker[key1] = ranker[key2]
    ranker[key2] = r


##################################################
######### Rank aggregation functions
##################################################

def best_random_aggregator(objects, tries, debug=False):
    """ Try random rankers given number of tries. Print debug
    info if debug is set to True.

    """

    obj = objects.keys()
    ##initialize
    trial = obj[:]
    random.shuffle(trial)
    bestranker = get_ranker(trial)  #best so far
    bestscore =  kendall_tau(objects, bestranker)

    if debug:
        print bestranker, bestscore

    ## try random choices
    for i in range(tries):
        trial = obj[:]
        random.shuffle(trial)
        ranker = get_ranker(trial)
        score = kendall_tau(objects, ranker)
        if score > bestscore:
            bestscore = score
            bestranker = ranker
            if debug:
                print "changed rankers", bestranker, bestscore

    return bestranker, bestscore


def pagerank_aggregator(objects, threshold, alpha):
    """Implements the pagerank aggregation for a given alpha and epsilon.
    Alpha is for the bias towards surf probability, non-random in this case.
    Epsilon controls the convergence threshold, a small number in practice.

    The program first constructs the graph given the rankers and then calls
    pagerank function repeatedly until the average change in pagerank scores 
    is below epsion. Then, it converts the resulting scores into a ranking.

    """

    ### Construct graph version of the rankers and update indegrees
    indegrees = {}
    total_indegrees = 0.0
    graph = {}
    for key in objects.keys():
        graph[key] = []
        indegrees[key] = 0.0

    for key1 in objects.keys():
        for key2 in objects.keys():
            if key1 != key2:
                count = num_higher(objects, key1, key2) 
                if count > 0:
                    graph[key1].append( (key2,float(count)) )
                    indegrees[key2] += count
                    total_indegrees += count


    ##Normalize to add the outlinks to 1
    for key1 in graph.keys():
        total = 0
        for (key2,val) in graph[key1]:
            total += val
        for i in range(len(graph[key1])):
            (key2, val) = graph[key1][i]
            graph[key1][i] = (key2, val/total)

    ##Normalize indegrees as well
    for key in indegrees.keys():
        indegrees[key] /= total_indegrees


    ### Call page rank
    final_scores = pg.pagerank(graph, indegrees, threshold, alpha)

    #final_scores = pg.pagerank(graph, {}, threshold, alpha)

    ### Convert the final scores to a ranking
    ranker = get_ranker_for_scores(final_scores)

    rankscore = kendall_tau(objects, ranker)
    return ranker, rankscore


def indegree_aggregator(objects):
    """Returns a simple indegree aggregation based on the number of rankers that rank the
    given object higher than the rest.
    """

    ### Construct graph version of the rankers and update indegrees
    indegrees = {}

    for key in objects.keys():
        indegrees[key] = 0.0

    for key1 in objects.keys():
        for key2 in objects.keys():
            if key1 != key2:
                count = num_higher(objects, key1, key2) 
                if count > 0:
                    indegrees[key2] += count

    ### Convert the indegree scores to a ranking
    ranker = get_ranker_for_scores(indegrees)

    rankscore = kendall_tau(objects, ranker)
    return ranker, rankscore

##################################################
######### Iterative flip algorithms
##################################################

def iterative_greedy_flip(objects, inputranker, k=1):
    """ Flip a pair of objects in ranker until k total passes are 
    done or no improvements are possible.

    """

    allkeys = objects.keys()

    pairs = []
    for i in range(len(allkeys)-1):
        for j in range(i+1,len(allkeys)):
            pairs.append( (allkeys[i], allkeys[j]) )
    
    ranker = copy.deepcopy(inputranker) ##copy we will work with
    currentscore = kendall_tau(objects, ranker)
    total_flips = 0
    iter = 0
    while (iter < k):
        iter += 1
        flip_done = False
        random.shuffle(pairs)
        ##One pass, try all pairs in pairs and check if flipping
        ##the given pair of objects improves the error in ranker
        for i in range(len(pairs)):
            key1, key2 = pairs[i]
            ##switch key1 and key2
            newscore = kendall_tau_partial(objects, ranker, currentscore, key1, key2)
            switch(ranker, key1, key2)
            if newscore > currentscore:
                flip_done = True
                total_flips += 1
                currentscore = newscore
            else: ## reverse the switch
                switch(ranker, key1, key2)
        if not flip_done:
            break
    return ranker, currentscore, total_flips


def iterative_best_flip(objects, inputranker):
    """Flip a pair of objects in ranker regardless of whether it improves, then perform 
    all other possible flips if they improve performance and record the output.

    Continue for all possible pairs, and return the best performance
    over all such configurations.

    """

    allkeys = objects.keys()

    pairs = []
    for i in range(len(allkeys)-1):
        for j in range(i+1,len(allkeys)):
            pairs.append( (allkeys[i], allkeys[j]) )
    random.shuffle(pairs)
    
    ranker = copy.deepcopy(inputranker) ##copy we will work with
    currentscore = kendall_tau(objects, ranker)
    total_flips = 0
    configs = []
    iter = 0
    max_score = currentscore
    max_ranker = inputranker

    for i in range(len(pairs)):
        key1,key2 = pairs[i] ##current pair being flipped

        iter_ranker = copy.deepcopy(ranker)
        iter_score = kendall_tau_partial(objects, ranker, currentscore, key1, key2)
        switch(iter_ranker, key1, key2)

        ##One pass, try all pairs in pairs and check if flipping
        ##the given pair of objects improves the error in ranker
        for j in range(len(pairs)):
            if i == j:
                continue
            key1, key2 = pairs[j]
            ##switch key1 and key2
            newscore = kendall_tau_partial(objects, ranker, iter_score, key1, key2)
            switch(iter_ranker, key1, key2)
            if newscore > iter_score:
                iter_score = newscore
            else: ## reverse the switch
                switch(iter_ranker, key1, key2)
        if iter_score > max_score:
            max_score = iter_score
            max_ranker = iter_ranker
            
    return max_ranker, max_score


##################################################
######### Function to call aggregators while
######### removing rankers to manage errors
##################################################

def remove_top_k(objects, ranker_names, nullranker, k):
    """ Removes up to k rankers until the error of using the
    input aggregator improves.

    """

    nullscore = kendall_tau(objects, nullranker) ##initial score
    localobjects = copy.deepcopy(objects) ##must not change the original set
    names = ranker_names[:] ##local copy of ranker names

    iter = 0
    removed = []

    while (iter<k): ##iterate at most k times, but break if no improvement
        iter += 1
        
        #######################################################################
        ###Find the best ranker to remove in this iteration
        #######################################################################

        performance = [] ## (score improvement, ranker id) from removing ranker id
        for i in range(len(ranker_names)):
            cur_obj = copy.deepcopy(localobjects)
            remove_ranker(cur_obj, i)  ##remove ranker i

            ##check new score and record performance improvement
            ranker, score = pagerank_aggregator(cur_obj, 0.000001, 0.95)
            performance.append( (score-nullscore, i) )

        performance.sort(reverse=True)
    
        ##Now remove the top performing ranker if score is higher than zero
        if performance[0][0] > 0:
            to_remove = performance[0][1]
            remove_ranker(localobjects, to_remove)
    
            ##get the improved new score and record performance improvement
            nullranker, nullscore = pagerank_aggregator(localobjects, 0.000001, 0.95)
            removed.append( names[to_remove] )
            names = names[:to_remove]+names[to_remove+1:]
        else:
            break ##no further improvements
    
    return nullranker, nullscore, removed, localobjects

##################################################
######### Main body of the code
##################################################

if __name__ == "__main__":
    debug = False
    if len(sys.argv)<2:
        print "Usage python rankers.py filename"
    else:

        start = time.time()
        fname = sys.argv[1]
        (objects,ranker_names) = read_rankers(fname)
        #print_rankers(objects, ranker_names)

        ranker, score = indegree_aggregator(objects)
        print "Indegree", score
        print_single_ranker(ranker)

        ranker, score = pagerank_aggregator(objects, 0.000001, 0.85)
        print "Pagerank:", score
        print_single_ranker(ranker)
     
        ### You can also try random aggregation, but not advisable for large data
        ### Unless you run many trials, this will not work well
        #ranker, score = best_random_aggregator(objects, 10, debug)
        #print "Best random:", score
        #print_single_ranker(ranker)

        ranker2, score, total_flips = iterative_greedy_flip(objects, ranker, 5)
        print "Iterative greedy flip k=5 using pagerank:", score
        print_single_ranker(ranker2)
        print "Total number of flips", total_flips

        ranker1, score, removed, newobjects = remove_top_k(objects, ranker_names, ranker, 5)
        print "Iterative remove with pagerank:", score
        print_single_ranker(ranker1)
        print "Removed", removed

        ranker3, score, total_flips = iterative_greedy_flip(newobjects, ranker1, 5)
        print "Iterative greedy flip after removal:", score
        print_single_ranker(ranker3)
        print "Total number of flips", total_flips

        ranker3, score = iterative_best_flip(objects, ranker)
        print "Iterative best flip using pagerank:", score
        print_single_ranker(ranker3)

        end = time.time()
        print "Took", end-start, "seconds"

