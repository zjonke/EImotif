# EI motif

This repository contains data and code used for the submitted manuscript.

## Requirements

PCSIM, http://www.lsm.tugraz.at/pcsim/
Python
IPython
Numpy
Scipy
Matplotlib

The Enthought Python distribution (https://www.enthought.com/products/epd/) is a simple way to install all of them except PCSIM.

**Note**: PCSIM runs on linux and requires python 2.5.
We included simulation data (spike trains), so that the code for analyses and plots can be run without installing PCSIM.

## Setup

Download or clone code.
Add code folder (eimotif) to the python path in the .bashrc file
```
PYTHONPATH=<path_to_eimotif_folder>:$PYTHONPATH
```

## Code organisation

- `eim` folder: contains common code and model definition
- `simulations` folder: contains all simulations, each in its own folder (e.g. bars, oriented_bars, ..)

Each simulation is self contained in its folder, containing simulation settings and scripts to create simulation data, run simulation, perform analysis and to show results of simulation (weights).

## Run simulations

To perform simulation of e.g. bars, go to the folder of simulation and run scripts in order:
- `python create_data.py` (creates data for simulation)
- `python run_simulations.py` (runs simulations of model, requires PCSIM, but we provide data so you can skip it)
- `ipython --pylab show_weights.py` (plots network weights after learning)
- `python analyse.py` (performs analysis of network)

