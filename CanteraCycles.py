# -*- coding: utf-8 -*-
"""
Created on Mon Aug 25 12:35:53 2025

@author: Bobke
"""


import cantera as ct

eta_pump = 0.6  # pump isentropic efficiency
eta_turbine = 0.8  # turbine isentropic efficiency


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
w = ct.Methane()


w.TQ = 130.0, 0.0
#w.TP = 130.0, 0.01*1e7
h1 = w.h
p1 = w.P
printState(1, w)

p_max = 100*p1

pump_work = pump(w, p_max, eta_pump)
h2 = w.h
printState(2, w)

w.TP = 800, p_max
h3 = w.h
heat_added = h3 - h2
printState(3, w)

turbine_work = expand(w, p1, eta_turbine)
printState(4, w)


work_ratio = turbine_work/pump_work
eff = (turbine_work - pump_work)/heat_added
print('efficiency = ', eff)

print(f"Pump Work: {pump_work:.0f} J/kg")
print(f"turbine Work: {turbine_work:.0f} J/kg")
print(f"Pump-Turbine work ratio: {work_ratio:.2f}")

prop_eff = 0.8
work_out = prop_eff*(turbine_work - pump_work)

SFC = g/(work_out)
print(SFC)
