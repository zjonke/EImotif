import numpy as np
from pypcsim import *


def findInputPool(pools):
	for pool in pools:
		if pool["type"] == "input":
			return pool

			
class NeuronsPool:
    """
        Represents a pool of same neurons: input, excitatory, inhibitory
    """

    def __init__(self, net, **kwds):
        """
            net : PCSIM network (single or multi thread)
        """
        self.net = net
        self.pooltype = kwds.get('pooltype', "excitatory")  # default neuron pool

        self.poolparams = kwds.get('poolparams', {'N':1})  # default neuron pool

        #  Create pool of N neurons
        self.N = self.poolparams.get('N', 1)  # at least 1 neuron
        if self.pooltype == "input":
            self.pop = SimObjectPopulation(self.net, SpikingInputNeuron(), self.N)
        else:
            neuronparams = self.poolparams.get('neuronparams',{})
            neurontype=neuronparams.get('type', 'ExponentialPoissonNeuron')
            if neurontype=='ExponentialPoissonNeuron':
                A = neuronparams.get('A', 10e-3)  # 10ms
                C = neuronparams.get('C', 1.)
                Rm = neuronparams.get('Rm', 1.)
                Trefract = neuronparams.get('Trefract', 10e-3)
                Iinject = neuronparams.get('Iinject', 0.)
                nrn_model = ExponentialPoissonNeuron(A=A,C=C,Rm=Rm,Trefract=Trefract,Iinject=Iinject)
            elif neurontype=='LinearPoissonNeuron':
                C = neuronparams.get('C', 1.)
                Rm = neuronparams.get('Rm', 1.)
                Trefract = neuronparams.get('Trefract', 10e-3)
                Iinject = neuronparams.get('Iinject', 0.)
                nrn_model = LinearPoissonNeuron(C=C,Rm=Rm,Trefract=Trefract,Iinject=Iinject)

            self.pop = SimObjectPopulation(self.net, nrn_model, self.N)

        # create recorders
        rec = self.poolparams.get('rec', False)  # flag to record spikes
        if rec:
            self.spike_rec_pop = self.pop.record( SpikeTimeRecorder() )


    def setSpikes(self, spikes):
        # spikes in sec
        if self.pooltype == "input":
            # ensure same number of neurons and the number of provided channels
            assert len(spikes) == self.N 
            # Setting the Input Spikes
            for i in range(self.pop.size()):
                if len(spikes[i]) > 0:
                    self.pop.object(i).setSpikes(spikes[i])  # no aligement to grid

    def getSpikes(self):
        spikes = [ np.array(self.spike_rec_pop.object(i).getRecordedValues()) for i in range(self.spike_rec_pop.size()) ]
        return spikes

    def __str__(self):
        desc = '''  SKWTA
                single  : %s
               ''' % (self.single)
        return desc