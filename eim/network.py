import numpy as np
from pypcsim import *
from pool import NeuronsPool
from psp import createPSPShape


class Network:
    def __init__(self, simulationSettings, modelSettings):
        ss, ms = simulationSettings, modelSettings

        self.dt = ss.dt
        self.simulationRNGSeed = ss.simulationRNGSeed
        self.constructionRNGSeed = ms.constructionRNGSeed

        pools = ms.pools
        psps = ms.psps
        syntypes = ms.syntypes
        poolsconns = ms.poolsconns

        self.synlearning= ['StaticSWTAKernelSynapse','StaticSWTAStdpKernelSynapse']
		
        # create network
        sp = SimParameter(dt=Time.sec(self.dt), constructionRNGSeed=self.constructionRNGSeed, simulationRNGSeed=self.simulationRNGSeed)

        self.net = SingleThreadNetwork(sp)

        # pools holder
        self.pools = {}
        self.poolnames = []
		
        # create pools
        for p in pools:
            print "network pool", self.net, p["type"], p["poolparams"]
            self.pools[p["name"]] = NeuronsPool(self.net, pooltype=p["type"], poolparams=p["poolparams"])
            self.poolnames.append(p["name"])

        # shapes holder
        self.psps = {}
        self.pspnames = []
		
        # create psp shapes
        for p in psps:
            self.psps[p['name']] = self.createPSP(p)
            self.pspnames.append(p["name"])

        # syntypes holder
        self.syntypes = {}
        self.syntypesinfo = {}
        self.synnames = []
        # create synapse types
        for s in syntypes:
            self.syntypes[s['name']]= self.createSynType(s)
            self.synnames.append(s["name"])
            self.syntypesinfo[s['name']]=s

        # connect pools
        self.conns = {}
        self.connslearning = []
        for conn in poolsconns:
            self.conns[(conn['source'],conn['target'])] = self.connectPools(conn)
            if self.syntypesinfo[conn['syntype']]['type'] in self.synlearning:
                self.connslearning.append((conn['source'],conn['target']))

        #add progress bar
        self.progBarID=self.net.add(SimProgressBar())
        self.totalsimtime=0

    def createPSP(self, PSP):
        psp = createPSPShape(PSP,self.dt)
        return KernelArray(psp)

    def createSynType(self, syntype):
        #print syntype['psp']
        #print self.psps
        psp_kernel = self.psps[syntype['psp']]
        syn_type = syntype['type']
        synparam = syntype['synparam']
        if syn_type == 'StaticSWTAKernelSynapse':
            syn_model = StaticSWTAKernelSynapse(kernel=psp_kernel,
                                                activeLearning=synparam['learning'],
                                                Winit=synparam['Winit'],  #  real initialization is done after
                                                eta=synparam['eta'],
                                                Wmin=synparam['Wmin'],
                                                Wmax=synparam['Wmax'],
                                                fa=synparam['fa'],
                                                fb=synparam['fb'],
                                                delay=synparam['delay'],
                                                back_delay=0e-3)

            syn_fact = SimObjectVariationFactory( syn_model )
            syn_fact.set( 'Winit', UniformDistribution(synparam['Wmin'], synparam['Wmin']+1.))
            syn_fact.set( 'delay', UniformDistribution(0., synparam['delay']))

        elif syn_type == 'StaticCurrKernelSynapse':
            syn_model = StaticCurrKernelSynapse(kernel=psp_kernel,
                                                W=synparam['W'],
                                                delay=synparam['delay'])
            syn_fact = SimObjectVariationFactory( syn_model )

        elif syn_type == 'StaticSWTAStdpKernelSynapse':
            syn_model = StaticSWTAStdpKernelSynapse(  kernel=psp_kernel,
                                                Winit=synparam['Winit'],#  real initialization is done after
                                                delay=synparam['delay'],
                                                back_delay=0e-3,
                                                activeSTDP=synparam['activeSTDP'],
                                                STDPgap = synparam['STDPgap'],
                                                tauneg = synparam['tauneg'],
                                                taupos = synparam['taupos'],
                                                Wmin=synparam['Wmin'],
                                                Wmax=synparam['Wmax'],
                                                Aneg = synparam['Aneg'],
                                                Apos = synparam['Apos'],
                                                ad = synparam['ad'],
                                                bd = synparam['bd'],
                                                ap = synparam['ap'],
                                                bp = synparam['bp']
                                                )

            syn_fact = SimObjectVariationFactory( syn_model )
            syn_fact.set( 'Winit', UniformDistribution(synparam['Wmin'], synparam['Wmin']+1.))
            syn_fact.set( 'delay', UniformDistribution(0., synparam['delay']))

        return syn_fact

    def connectPools(self,conn):
		# Create Synaptic Connections
        s = conn['source']
        t = conn['target']
        syntype = conn['syntype']
        prob = conn['connprob']
        same = True if s==t else False
        syns = [];
        for j in range (self.pools[t].pop.size()):
            for i in range(self.pools[s].pop.size()):
                if not(i==j) or not(same) and i==j:
                    if prob > np.random.rand():
                        synapse = self.net.connect( self.pools[s].pop[i], self.pools[t].pop[j], self.syntypes[syntype])
                        syns.append( synapse ) 

        return SimObjectPopulation(self.net, syns)

    def setBias(self, value, pool, ids):
        # sets Iinject (bias) of specific neurons in pool
        targetpool = self.pools[pool]
        nrns = targetpool.pop
        if len(ids)>0:
            assert min(ids)>-1 and max(ids)<nrns.size()
            for n in ids:
                nrn = nrns.object(n)
                nrn.Iinject=value

    def setLearning(self, onOff, sourcepool, targetpool, targetids=None):
        # sets synapses of specific pool' neurons to learning/no learning
        conn = (sourcepool,targetpool)
        if  conn in self.connslearning:
            #get sizes of pools
            sN = self.pools[sourcepool].N
            tN = self.pools[targetpool].N
            #get synapses between pools
            syns = self.conns[(sourcepool, targetpool)]
            synsids = syns.idVector()
            assert len(synsids) == sN * tN
            if targetids == None:
                targetids = range(tN)
            for i in targetids:
                for j in xrange(sN):
                    syn = self.net.object(synsids[i * sN + j])
                    if "activeLearning" in dir(syn):
                        syn.activeLearning = onOff
                    elif "activeSTDP" in dir(syn):
                        syn.activeSTDP = onOff

    def setLearningOld(self, onOff, sourcepool, targetpool):
        # sets specific pool synapses to learning
        conn = (sourcepool, targetpool)
        if  conn in self.connslearning:
            #get synapses between pools
            syns = self.conns[(sourcepool,targetpool)]
            synsids = syns.idVector()
            for i in xrange(len(synsids)):
                syn = self.net.object(synsids[i])
                #work around
                if "activeLearning" in dir(syn):
                    syn.activeLearning = onOff
                elif "activeSTDP" in dir(syn):
                    syn.activeSTDP = onOff
    
    def simulate(self, Tsim, stimulus=None, reset=True, simulationRNGSeed=None):
        self.totalsimtime += Tsim
        if not stimulus is None:
            self.pools['in'].setSpikes(stimulus)

        if reset:
            self.net.reset();

        if not simulationRNGSeed is None:
            self.net.seed(simulationRNGSeed)

        print "Tsim=", Tsim, " dt:", self.dt
        progBar = self.net.object(self.progBarID)
        progBar.changeSimulationTime(Time.sec(self.totalsimtime))

        self.net.advance(int(Tsim/self.dt))  # takes number of steps
        print "Simulation complete"

    def reset(self):
        self.net.reset();

    def getResponse(self,pool):
        spikes = []
        if pool == "all":
            for p in self.pools.keys():
                spikes += self.pools[p].getSpikes()
        else:
            spikes = self.pools[pool].getSpikes()
        return spikes
    
    def getPoolIds(self):
        pass

    def getWeights(self, sourcepool, targetpool):
        conn = (sourcepool, targetpool)
        #get synapses between pools
        syns = self.conns[(sourcepool, targetpool)]
        weights = [ syns.object(i).W for i in range(syns.size())]
        return weights

    def getShapedWeights(self, sourcepool, targetpool):	
        shape = (self.pools[targetpool].pop.size(), self.pools[sourcepool].pop.size())
        return np.array(self.getWeights(sourcepool, targetpool)).reshape(shape)

    def getAllWeights(self):
        W = {}
        for conn in self.conns.keys():
            #get synapses between pools
            (sourcepool, targetpool) = conn
            syns = self.conns[(sourcepool, targetpool)]
            weights = [ syns.object(i).W for i in range(syns.size())]
            W[conn] = weights
        return W

    def setWeights(self, sourcepool, targetpool, W):
        conn = (sourcepool, targetpool)
        weights = W.reshape([W.shape[0] * W.shape[1],])
        #get synapses between pools
        syns = self.conns[(sourcepool, targetpool)]
        assert syns.size() == len(weights)
        for i in range(syns.size()):
            syns.object(i).W  = weights[i]

    def setAllWeights(self, W):
        for conn in W.keys():
            (sourcepool, targetpool) = conn
            self.setWeights(sourcepool, targetpool, W[conn])

    def getAllSpikes(self):
        allSpikes = {}
        for pool in self.pools:
            allSpikes[pool] = self.getResponse(pool)
        return allSpikes
