from network import Network
from data import assertNoLearning
from pool import findInputPool
import plot

def simulate(generalSettings, simulationSettings, modelSettings, simulationChainData, save=True):
	gs = generalSettings
	ss = simulationSettings
	ms = modelSettings
	scd = simulationChainData
	
	for i, simData in enumerate(scd.getSimulationsData()):
		print "SIMULATION", i + 1, simData.__dict__
		
		# set number of input neurons based on nChannels in patterns
		findInputPool(ms.pools)['poolparams']['N'] = simData.dataSettings.nChannels

		net = Network(ss, ms)
		net.simulate(0., simData.train.spikes)
		
		if simData.init: # results/training
			r = scd.getResult(simData.init)
			if r:
				print "Network initialized based on: ", simData.init
				W = r["finalW"]
				net.setWeights('in', 'e', W)
		
		initW = net.getShapedWeights('in','e')
		net.setLearning(simData.learning, 'in', 'e')
		if simData.learning and ss.showLearningProgress:
			for i in xrange(10):
				net.simulate(simData.simTime / 10., None, reset=False)
				W = net.getShapedWeights('in','e')
				plot.showWeights(simData.dataSettings.patternShape, W)
		else:
			net.simulate(simData.simTime, None, reset=False)
			
		finalW = net.getShapedWeights('in','e')
		assertNoLearning(initW, finalW, simData.learning)

		scd.addResult(simData.result, dict(initW=initW, finalW=finalW,  spikes=net.getAllSpikes()))
	
	if save:
		scd.saveResults()
	
