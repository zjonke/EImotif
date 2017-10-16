class NetworkModuleSettings:
	def __init__(self, module):
		config = dict(
					  # network anatomy params
					  numinp=module.NUMINP,
					  numexc=module.NUMEXC,
					  numinh=module.NUMINH,

					  syn_in_conn_prob=module.SYN_IN_CONN_PROB,
					  syn_ei_conn_prob=module.SYN_EI_CONN_PROB,
					  syn_ie_conn_prob=module.SYN_IE_CONN_PROB,
					  syn_ii_conn_prob=module.SYN_II_CONN_PROB,

					  syn_in_scalling = getattr(module, "SYN_IN_SCALLING", 1.),
					  syn_ei_scalling = getattr(module, "SYN_EI_SCALLING", 1.),
					  syn_ie_scalling = getattr(module, "SYN_IE_SCALLING", 1.),
					  syn_ii_scalling = getattr(module, "SYN_II_SCALLING", 1.),
					  
					  construction_seed=module.CONSTRUCTION_SEED,
					  
					  # network physiology params
					  psp_trise=module.PSP_TRISE,
					  psp_tfall=module.PSP_TFALL,
					  psp_duration=module.PSP_DURATION,
					  psp_max_value=module.PSP_MAX_VALUE,

					  tauE=module.TAU_E,
					  tauI=module.TAU_I,

					  biasI=module.BIAS_I,

					  minW=module.MIN_W,
					  maxW=module.MAX_W,
					  syn_w_scalling=module.SYN_W_SCALLING,
					  syn_spike_to_spikes=module.SYN_SPIKE_TO_SPIKES,
				
					  syn_in_delay=module.SYN_IN_DELAY,
					  syn_ei_delay=module.SYN_EI_DELAY,
					  syn_ie_delay=module.SYN_IE_DELAY,
					  syn_ii_delay=module.SYN_II_DELAY,

					  # KWTA model params
					  K=module.K, 
					  sigmaSq=module.SIGMASQ, 
					  eta=module.ETA, 
					  fconst=module.FCONST)
					  
		self.__dict__ = config
		
	def update(self, settings):
		for k in settings.keys():
			assert k in self.__dict__, "Settings does not exist!"
		self.__dict__.update(settings)

		
def createSettings(module, additionalSettings):

	nms = NetworkModuleSettings(module)
	nms.update(additionalSettings)

	pool_in = {'name': 'in',
			   'type': 'input',
			   'poolparams': {'N': None,  # auto-size according to the input pattern nchannels
							  'rec': True
							 }			  
				}
	
	pool_e = {'name': 'e',
			  'type': 'excitatory',
			  'poolparams': {'N': nms.numexc,
				    	     'neuronparams': {'type': 'ExponentialPoissonNeuron',
											  'A': 1. / nms.tauE,
											  'C': nms.fconst,
											  'Rm': 1.,
											  'Trefract': nms.tauE,
											  'Iinject': (2 * nms.K - 1) / (2 * nms.sigmaSq * nms.fconst)
											 },
							  'rec': True
							}
				}

	pool_i = {'name': 'i',
			  'type': 'inhibitory',
			  'poolparams': {'N': nms.numinh,
							 'neuronparams': {'type': 'LinearPoissonNeuron',
											  'C': 1.,
											  'Rm': 1.,
											  'Trefract': nms.tauI,
											  'Iinject': nms.biasI
											 },
							  'rec': True
							}
				}

	pools = [pool_in, pool_e, pool_i]

	psp_e = dict(name='EPSP', type='additive', shape='doubleexp', maxvalue=nms.psp_max_value, trise=nms.psp_trise, tfall=nms.psp_tfall, duration=nms.psp_duration)
	psp_ei = dict(name='EPSP_EI', type='additive', shape='doubleexp', maxvalue=nms.psp_max_value, trise=nms.psp_trise, tfall=nms.psp_tfall, duration=nms.psp_duration)
	psp_ie = dict(name='IPSP', type='additive', shape='doubleexp', maxvalue=nms.psp_max_value, trise=nms.psp_trise, tfall=nms.psp_tfall, duration=nms.psp_duration)
	psps = [psp_e, psp_ie, psp_ei]	

	# Note: real synaptic delay equals delay + 1dt due to the PCSIM framework delay of 1 timestep(dt) 
	# Additionaly: PSP shape starts with 0, which effectively adds another 1dt of delays (which we do not count in the paper)
	syntype_e = {'name': 'in_e',
				 'psp': 'EPSP',
				 'type': 'StaticSWTAStdpKernelSynapse',
				 'synparam': {'Winit': 1. * nms.syn_in_scalling, 
							  'delay': nms.syn_in_delay,
							  'activeSTDP': False,  # bio je default True!
							  'STDPgap': 0e-3,
							  'tauneg': 25e-3,
							  'taupos': 10e-3,
							  'Wmin': nms.minW,
							  'Wmax': nms.maxW,
							  'Aneg': -1. * nms.eta,
							  'Apos': 1. * nms.eta,
							  'ad': 0., 'bd': 0., #no weight dependency in depression part
							  'ap': -1., 'bp': 1. # take directly weight
							  }
				}

	w_ei = 1. / nms.syn_ei_conn_prob * nms.syn_w_scalling * nms.syn_spike_to_spikes * nms.syn_ei_scalling
	syntype_ei = {'name': 'e_i',
				  'psp': 'EPSP_EI',
				  'type': 'StaticCurrKernelSynapse',
				  'synparam': {'delay': nms.syn_ei_delay, 'W': w_ei}
				 }
				 
	w_ie = -1. / (nms.sigmaSq * nms.fconst) * 1. / nms.syn_ie_conn_prob * nms.syn_w_scalling * nms.syn_ie_scalling
	syntype_ie = {'name': 'i_e',
				  'psp': 'IPSP',
				  'type': 'StaticCurrKernelSynapse',
				  'synparam': {'delay': nms.syn_ie_delay, 'W': w_ie}
				 }
				 
	# in order to more precisely counterbalance excitation we use SYN_EI_CONN_PROB instead of SYN_II_CONN_PROB 
	w_ii = -1. / nms.syn_ei_conn_prob * nms.syn_w_scalling * nms.syn_spike_to_spikes * nms.syn_ii_scalling
	syntype_ii = {'name': 'i_i',
				  'psp': 'IPSP',
				  'type': 'StaticCurrKernelSynapse',
				  'synparam': {'delay': nms.syn_ii_delay, 'W': w_ii}
				  }

	syntypes = [syntype_e, syntype_ie, syntype_ei, syntype_ii]

	poolsconns = [{'source': 'in', 'target': 'e', 'connprob': nms.syn_in_conn_prob, 'syntype': 'in_e'},
				  {'source': 'e',  'target': 'i', 'connprob': nms.syn_ei_conn_prob, 'syntype': 'e_i'},
				  {'source': 'i',  'target': 'e', 'connprob': nms.syn_ie_conn_prob, 'syntype': 'i_e'},
				  {'source': 'i',  'target': 'i', 'connprob': nms.syn_ii_conn_prob, 'syntype': 'i_i'}
				  ]
				  
	# remove conns which have connprob == 0
	i=0
	while i < len(poolsconns):
		if poolsconns[i]['connprob'] == 0.:
			poolsconns.pop(i)
		else:
			i += 1
	
	return dict(settings=nms, constructionRNGSeed=nms.construction_seed, pools=pools, psps=psps, syntypes=syntypes, poolsconns=poolsconns)