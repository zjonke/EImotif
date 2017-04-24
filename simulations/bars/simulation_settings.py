#################################
##    SIMULATION PARAMETERS    ##
#################################
			
DT = 1e-3                              			# duration of one time step in sec


#############################
##      SIMULATION CHAIN   ##
#############################

# param(default): learning(False), initialData(random)
SIMULATION_CHAIN = [dict(data="data/training", simTime=4., learning=True, result="results/training"),
				    dict(data="data/testing", simTime=2., learning=False, result="results/testing", init="results/training")]

					
#################################
##        NETWORK MODEL        ##
#################################

NETWORK_MODEL = "kwta"
NETWORK_PARAMS = dict()							# overwrite model default settings


#################################
##   SIMULATION VISUALIZATION  ##
#################################

SHOW_LEARNING_PROGRESS = True
