rank_aggregation: Rank Aggregation Algorithms
===============================================

This repository contains a number of simple rank aggregation algorithms and iterative algorithms that take as input a ranker and improves the ranking.

Copyright (c) 2014, Sibel Adali

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

    • Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    • Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

Any publication resulting from the use of this work must cite the following publication :

   Sibel Adali, Brandeis Hill and Malik Magdon-Ismail. 
   "Information vs. Robustness in Rank Aggregation: Models, Algorithms and a Statistical Framework for Evaluation",
   Journal of Digital Information Management (JDIM), special issue on Web information retrieval, 5(5), October, 2007.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Module Description
-------------------

All rankers are provided in file named rank_aggregators.py, except for pagerank method is given in a separate module.

The module create_ranking.py can be used to create random test rankers.

All rankers should be provided in a single input file which is:

    *  comma separated
    *  contain a header row
    *  first column is the object ids, assumed to be integers
    *  each column is a separate ranker
    *  if an object is not ranked by a ranker, leave that value empty.
    
Rankers can be total or partial, ranks can be consecutive or not, ties may exist. Currently, all ties are disregarded. There is no penalty for breaking ties.

The performance score is given by Kendall-tau, implemented as a score between 1 and -1. See Wikipedia for details.

Simple aggregators pagerank and indegree are based on a graph representation of the ranks, where the weights from object i to j represents the number of rankers that rank object j higher than object i.

Iterative improvements algorithms are iterative greedy flip, igf, (flip a pair as long as improvements are made), iterative best flip, ibf, (flip a pair even when it does not improve for each possible pairs and try other greedy flips), and remove top k worst rankers, ir. 

IBF is described in the above paper.


A wrapper to call rank aggregation from comamand line is also included. You can call a simple aggregator, followed by any number of iterative improvements on it.

Please include

To call the wrapper around the rank aggregation algorithms, use the following:

Usage 
-------------

Call the wrapper function by:

    python aggregate.py inputfile aggregator <list of iterative algorithms>

Aggregator list:

    * in: indegree
    * pg alpha: pagerank with given alpha (float between 0-1, default 0.85)
    * rnd k: random with k tries

Iterative algorithms (executed in the order given):

    * igf: iterative greedy flip
    * ibf k: iterative best flip (at most k (integer, default 1) rounds
    * ir k: iterative remove up to k (integer, default 1) rankers
    
All parameters with default values must be explicitly provided when combined with other functions. 

Example: 

        python aggregate.py test/data10_10.csv pg 0.85 ibf
        Pagerank, followed by ibf

Example: 

        python aggregate.py test/data10_10.csv in ir 5 ibf
        Indegree followed by iterative remove, followed by ibf
	
	
