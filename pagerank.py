"""
    Pagerank utility to be used in aggregations
    Author: Sibel Adali

    Takes as input a graph, given in a dictionary of the form:

    links: key as nodes, a list of pairs of the form: [(outlink, weight),...]

    where weights are assumed to be normalized to add up to 1.

"""

def compute_scores(scores, links, jump_prob, alpha=0.85):
    new_scores = {}
    for item in links:
        new_scores[item] = (1-alpha) * jump_prob[item]
    for p in links:
        for (q,w) in links[p]:
            new_scores[q] += alpha*w*scores[p]
    return new_scores

def compute_diff(score1,score2):
    diff = 0
    for item in score1:
        diff += abs( score1[item] - score2[item] )
    return diff

def pagerank(links, jump_prob={}, threshold=0.00001, alpha=0.85):
    num_nodes = float(len(links.keys()))
    
    if len(jump_prob.keys()) == 0: ##no random probability defined, use uniform
        for item in links.keys():
            jump_prob[item] = 1/num_nodes

    scores = {}
    for item in links.keys():
        scores[item] = jump_prob[item]

    iter = 0
    while (True):
        iter += 1
        new_scores = compute_scores(scores, links, jump_prob, alpha)
        diff = compute_diff(scores,new_scores)
        #print "Iteration %d (diff %.6f):" %(iter,diff)
        scores = new_scores
        if (diff < threshold) or (iter>100):
            break
    return scores
