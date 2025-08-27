# -*- coding: utf-8 -*-
"""
Created on Sun Aug 24 22:34:37 2025

@author: Bobke
"""

import cantera as ct

eta_pump = 0.7  # pump isentropic efficiency
eta_turbine = 0.8  # turbine isentropic efficiency
p_max = 200*1e5  # maximum pressure, pa
mdot = 1 #kg/s

g = 9.81

def pump(fluid, p_final, eta):
    """Adiabatically pump a fluid to pressure p_final, using
    a pump with isentropic efficiency eta."""
    h0 = fluid.h
    s0 = fluid.s
    fluid.SP = s0, p_final
    h1s = fluid.h
    isentropic_work = h1s - h0
    actual_work = isentropic_work / eta
    h1 = h0 + actual_work
    fluid.HP = h1, p_final
    return actual_work


def expand(fluid, p_final, eta):
    """Adiabatically expand a fluid to pressure p_final, using
    a turbine with isentropic efficiency eta."""
    h0 = fluid.h
    s0 = fluid.s
    fluid.SP =s0, p_final
    h1s = fluid.h
    isentropic_work = h0 - h1s
    actual_work = isentropic_work * eta
    h1 = h0 - actual_work
    fluid.HP = h1, p_final
    return actual_work


def printState(n, fluid):
    print('\n***************** State {0} ******************'.format(n))
    print(fluid.report())
    
    
# Create an object representing water:
H2 = ct.Solution('h2o2.yaml')
H2.TPX = 20, 1.5*1e5, 'H2:1'

h1 = H2.h
p1 = H2.P
#printState(1, H2)

pump_work = pump(H2, p_max, eta_pump)
h2 = H2.h
#printState(2, H2)


H2.TP = 1200, p_max
h3 = H2.h
heat_added = h3 - h2
#printState(3, H2)

turbine_work = expand(H2, 20*1e5, eta_turbine)
#printState(4, H2)

work_ratio = turbine_work/pump_work
print(f"Pump Work: {pump_work:.0f} J/kg")
print(f"turbine Work: {turbine_work:.0f} J/kg")
print(f"Pump-Turbine work ratio: {work_ratio:.2f}")

eff = (turbine_work - pump_work)/heat_added
print("cycle efficiency: ", eff)

prop_eff = 0.8
work_out = prop_eff*(turbine_work - pump_work)

SFC = g/work_out

print(SFC)