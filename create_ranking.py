"""
   Program to create a set of ranked lists of a given number of objects, 
   to be used for testing rank aggregation code.
   Author: Sibel Adali

   Creates partial rankers between num_objects/2 to 3*num_objects/4 objects
   completely randomly. 

   Usage python create_ranking outfilename numobjects numrankers

   Output is saved in an output file in comma separated format

"""

import random
import sys

def get_val(val):
    if val == None:
        return ""
    else:
        return str(val)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print "Usage python create_ranking outfilename numobjects numrankers"
        sys.exit()

    foutname = sys.argv[1]

    num_objects = int(sys.argv[2])  ##numbered 1,2,...
    num_rankers = int(sys.argv[3])


    ##init rankers
    rankers = {}
    obj = range(1, num_objects+1)
    for i in obj:
        rankers[i] = []


    ##each ranker ranks about num_objects/2 to 3*num_objects/4 objects
    min = num_objects/2
    max = 3*num_objects/4 
    ##create each ranker and append
    for i in range(num_rankers):
        num_ranked = random.randint(min, max)
        newranker = obj[:num_ranked] + [None]*(num_objects-num_ranked)
        random.shuffle(newranker)
        for i in range(len(newranker)):
            o = newranker[i]
            rankers[obj[i]].append(o)

    f = open(foutname, "w")
    
    line = "objects,"
    for i in range(1,num_rankers+1):
        line += "ranker" + str(i) + ","
    f.write(line.strip(",") +"\n")

    for o in obj:
        line = str(o) + ","
        for val in rankers[o]:
            line += get_val(val) + ","
        f.write(line[:-1]+"\n")

    f.close()
