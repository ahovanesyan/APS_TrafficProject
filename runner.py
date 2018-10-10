#!/usr/bin/env python
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2009-2018 German Aerospace Center (DLR) and others.
# This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v2.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v20.html
# SPDX-License-Identifier: EPL-2.0

# @file    runner.py
# @author  Lena Kalleske
# @author  Daniel Krajzewicz
# @author  Michael Behrisch
# @author  Jakob Erdmann
# @date    2009-03-26
# @version $Id$

# Modified for TUDelft course CS4010 by Canmanie T. Ponnambalam, September 2018

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random
import numpy as np
# from solver.genetic import Chromosome, Genetic
import solver.genetic as genetic
from matplotlib import pyplot as plt

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa


def generate_routefile(N):
    random.seed(42)  # make tests reproducible by random.seed(some_number)

    with open("data/cross.rou.xml", "w") as routes:
        print("""<routes>
        <vType id="typeCar" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" guiShape="passenger"/>

        <route id="NS" edges="n2A A2s" />
        <route id="WE" edges="w2A A2e" />
        <route id="SN" edges="s2A A2n" />
        <route id="EW" edges="e2A A2w" />""", file=routes)

        vehNr = 0

        # demand in each direction per time step
        p_NS = 1. / 10
        p_SN = 1. / 20
        p_WE = 3. / 20
        p_EW = 3. / 20

        for i in range(N):
            if random.uniform(0, 1) < p_NS:
                print('    <vehicle id="car_%i" type="typeCar" route="NS" depart="%i"/>' % (vehNr,i), file=routes)
                vehNr += 1

            if random.uniform(0, 1) < p_SN:
                print('    <vehicle id="car_%i" type="typeCar" route="SN" depart="%i"/>' % (vehNr,i), file=routes)
                vehNr += 1

            if random.uniform(0,1) < p_WE:
                print('    <vehicle id="car_%i" type="typeCar" route="WE" depart="%i"/>' % (vehNr,i), file=routes)
                vehNr += 1

            if random.uniform(0,1) < p_EW:
                print('    <vehicle id="car_%i" type="typeCar" route="EW" depart="%i"/>' % (vehNr,i), file=routes)
                vehNr += 1

        print("</routes>", file=routes)


# def fitness_overwrite(n, e, s, w, sectio_id='A'):
#     if traci.trafficlight.getPhase(sectio_id) == 0:
#         return n+s
#     elif traci.trafficlight.getPhase(sectio_id) == 2:
#         return w+e
#     else:
#         assert 'Section id {} is not 0 or 2'.format(sectio_id)


def run():
    """execute the TraCI control loop"""
    step = 0
    halting_cars = []

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        step += 1
        halt_wA0 = traci.lanearea.getLastStepHaltingNumber("wA0")  # number of halting cars on wA0
        halt_nA0 = traci.lanearea.getLastStepHaltingNumber("nA0")
        halt_eA0 = traci.lanearea.getLastStepHaltingNumber("eA0")  # number of halting cars on wA0
        halt_sA0 = traci.lanearea.getLastStepHaltingNumber("sA0")
        if step % 10  == 0:
            phase = solve(halt_nA0, halt_eA0, halt_sA0, halt_wA0)
            traci.trafficlight.setPhase("A", phase)
            # traci.trafficlight.setPhaseDuration('A', 10)
        halting_cars.append(halt_eA0 + halt_wA0 + halt_nA0 + halt_sA0)


        # print('phase', traci.trafficlight.getPhase("A"))
        
    traci.close()
    sys.stdout.flush()
    plt.plot(halting_cars)
    plt.xlabel("time")
    plt.ylabel("#waiting cars")
    plt.show()

def ga_config():
    genetic.POPULATION_SIZE = 100
    genetic.CHROMOSOME_SIZE = 1

def solve(n, e, s, w):
    ga = genetic.Genetic()
    ga.initial_population(chromosome_params=[n, e, s, w])
    best, evo = ga.approximate()
    return 2*best.chromosome[0]


# this is the main entry point of this script
def simulate_n_steps(N,gui_opt):
    # this will start sumo as a server, then connect and run
    if gui_opt=='nogui':
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # first, generate the route file for this simulation
    generate_routefile(N)

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "data/cross.sumocfg","--tripinfo-output", "tripinfo.xml"]) # add ,"--emission-output","emissions.xml" if you want emissions report to be printed

    run()
