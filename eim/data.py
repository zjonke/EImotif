import os
import shelve
import copy


def assertNoLearning(initW, finalW, learning):
	if not learning:
		assert (initW == finalW).all(), "Weights changed!"

		
def loadWeights(fname):
	shelf = shelve.open(fname)
	W = shelf['w']
	shelf.close()
	return W

	
def saveData(fname, **kwargs):
	shelf = shelve.open(fname)
	for k, v in kwargs.iteritems():
		shelf[k] = v
	shelf.close()

	
def loadData(fname):
	fileExists = os.path.exists(fname)
	assert fileExists, "Missing data: " + fname

	shelf = shelve.open(fname)
	r = {}
	for k, v in shelf.iteritems():
		r[k] = copy.copy(v)
	shelf.close()
	return r
