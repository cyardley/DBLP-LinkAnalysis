#!/usr/bin/python
# PageRank algorithm
# By Peter Bengtsson
#    http://www.peterbe.com/
#    mail@peterbe.com
# License: BSD,http://opensource.org/licenses/bsd-license.php 
#
# Requires the numpy module
# http://numpy.scipy.org/

from numpy import *
import numpy.linalg as la
import cPickle
from util import *

def _sum_sequence(seq):
    """ sums up a sequence """
    def _add(x,y): return x+y
    return reduce(_add, seq, 0)

class PageRanker:
    def __init__(self, p, webmatrix):

        assert p>=0 and p <= 1
        self.p = float(p)
        if type(webmatrix)in [type([]), type(())]:
            webmatrix = array(webmatrix)
        assert webmatrix.shape[0]==webmatrix.shape[1]
        self.webmatrix = webmatrix
        sprint(".")
        # create the deltamatrix
        imatrix = identity(webmatrix.shape[0])
        for i in range(webmatrix.shape[0]):
            imatrix[i] = imatrix[i]*sum(webmatrix[i,:])
        deltamatrix = la.inv(imatrix)
        self.deltamatrix = deltamatrix

        sprint(".")
        # create the fmatrix
        self.fmatrix = ones(webmatrix.shape)
        sprint(".")
        self.sigma = webmatrix.shape[0]

        sprint(".")
        # calculate the Stochastic matrix
        _f_normalized = (self.sigma**-1)*self.fmatrix
        _randmatrix = (1-p)*_f_normalized
        sprint(".")
        _linkedmatrix = p * dot(deltamatrix, webmatrix)
        sprint(".")
        M = _randmatrix + _linkedmatrix
        sprint(".")
        self.stochasticmatrix = M
        sprint(".")
        self.invariantmeasure = ones((1, webmatrix.shape[0]))


    def improve_guess(self, times=1):
        for i in range(times):
            self._improve()
            
    def _improve(self):
        self.invariantmeasure = dot(self.invariantmeasure, self.stochasticmatrix)

    def get_invariant_measure(self):
        return self.invariantmeasure

    def getPageRank(self):
        sum = _sum_sequence(self.invariantmeasure[0])
        copy = self.invariantmeasure[0]
        for i in range(len(copy)):
            copy[i] = copy[i]/sum
        return copy

def doRank():
    sprint("Loading Matrix:")
    f = open('web_matrix', 'rb')
    web = cPickle.load(f);
    sprint("..done.\n")
    sprint("Ranking Page:")
    pr = PageRanker(0.85, web)
    sprint("..done.\n")
    sprint("Improving guess:")
    pr.improve_guess(100)
    sprint("...done\n")
    result = pr.getPageRank()

    sprint("Creating Results List")
    order = cPickle.load(open('web_order', 'rb'))
    resultList = [(float,unicode)]
    i=0
    for p in result:
        tup = (p, order[i])
        resultList.append( tup )
        i += 1
    resultList.remove((float,unicode))
    topResults = sortReverse(resultList)
    sprint("...done.\n")

    sprint("Saving Results List:")
    cPickle.dump(topResults, open('top_pub', 'wb'))

if __name__=='__main__':

    doRank()

    sprint("...done.\n")
    print "Top 10:"
    for k in range(0, 10):
        print str(topResults[k][0]) + "\t" +  str(topResults[k][1])
        print

