
######################################
##    NETWORK ANATOMY PARAMETERS    ##
######################################

NUMINP = None									# number of input neurons: 
												# i	f None NUMINP=number of input pattern channels
NUMEXC = 400                             		# number of excitatory neurons
NUMINH = 100									# number of inhibitory neurons

SYN_IN_CONN_PROB = 1.							# connectivity probability between different pools of neurons
SYN_EI_CONN_PROB = 0.575
SYN_IE_CONN_PROB = 0.6
SYN_II_CONN_PROB = 0.55

CONSTRUCTION_SEED = 42


#########################################
##    NETWORK PHYSIOLOGY PARAMETERS    ##
#########################################

PSP_TRISE = 1e-3								# rise const of double exp PSP
PSP_TFALL = 10e-3								# rise const of double exp PSP
PSP_DURATION = 50e-3							# cut off time of PSP, in sec
PSP_MAX_VALUE = 1.								# max value of a double exp PSP shape

TAU_E = 10e-3	                            	# time excitatory neuron is on after spike (refactory period)
TAU_I = 3e-3									# time inhibitory neuron is on after spike (refactory period)

BIAS_I = 0.										# intrisic activity of inhibitory neurons (current injection)

MIN_W = 0.01									# minimum value of input synaptic weight
MAX_W = 1.										# maximum value of input synaptic weight
SYN_W_SCALLING = 0.78  							# scalling of synaptic weights due to the area of PSP (which is 1/0.78)
SYN_SPIKE_TO_SPIKES = 10.  						# factor controlling number of elucided spikes in a population caused by a single incomming spike

# SYNAPTIC DELAYS, in sec
# Note: real synaptic delay equals delay + 1dt (1ms) due to the PCSIM framework delay of 1 timestep(dt) 
SYN_IN_DELAY = 10e-3
SYN_EI_DELAY = 0e-3
SYN_IE_DELAY = 0e-3
SYN_II_DELAY = 0e-3


#################################
##    KWTA MODEL PARAMETERS    ##
#################################

K = -3.4										# parameter
SIGMASQ = 0.35									# parameter
ETA = 0.02										# learning speed factor
FCONST = 2.										# fconst is inference parameter const
