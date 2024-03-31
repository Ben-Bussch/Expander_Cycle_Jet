# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 15:36:19 2024

@author: robbi
"""


import numpy as np
from sympy import *

# This uses sympy, which is a library for symbolic maths (ie it can rearrange equations and find exact solutions)
# sympy can also work to arbitrary precision (eg 100 decimals of pi) but can be somewhat slow for tricky maths (eg decimal powers)

""" Reference numbers which aren't used yet"""

O_F = 15            # O/F ratio of the engine
p_1 = 100000        # Static ambient pressure
v_1 = 80            # Ambient air velocity
T_1 = 293.15        # Ambient air temperature
p_1f = 1000000      # Input fuel pressure
T_1f = 293.15       # Input fuel temperature
Delta_T_f = 400     # Fuel temperature gain
Cp_a = 1010         # Air Cp
gam_a = 1.4         # Ratio of specific heats of the air
Cp_f = 2600         # Fuel Cp
gam_f = 1.13        # Ratio of specific heats of the fuel    
LCV_f = 46.4E6      # Lower calorific value of the fuel


""" Symbols and governing equations"""


""" Symbols """

# Symbols need to be defined for sympy to use them in symbolic equations.
# I've divided them up by equation arbitrarily - they could be all defined at once.
# Can't currently place any assumptions on the range of values they could take (ie real, positive), because they cannot be carried over into symbols passed as keys in keyword arguments.

# Cp_ratio symbols
Cp,Cv,gam = symbols('Cp,Cv,gam')

# SFEE symbols (W is positive work out of the system)
h_in, h_out, v_in, v_out, m_dot_in, m_dot_out, W = symbols('h_in, h_out, v_in, v_out, m_dot_in, m_dot_out W')

# Perfect gas enthalpy equation symbols (taking average value of Cp)
Cp_out, Cp_in, T_out, T_in = symbols('Cp_out, Cp_in, T_out, T_in')

# Adiabatic compression equation symbols (using respective values of gamma)
gam_in, gam_out, p_in, p_out = symbols('gam_in, gam_out, p_in, p_out')

""" Equations """

# A bunch of named equations which are true throught the whole system.
# Where there is a change between stations, symbols are labelled 'symbol_in' and 'symbol_out'

Cp_ratio = Eq(Cp, gam*Cv)

SFEE = Eq(W , m_dot_in * (h_in + v_in**2/2) - m_dot_out * (h_out + v_out**2/2))

Enth = Eq(h_out - h_in , (Cp_out+Cp_in)/2*(T_out-T_in))

Adia_comp = Eq(T_in/(p_in**((gam_in-1)/gam_in)) , T_out/(p_out**((gam_out-1)/gam_out)))


""" List of governing equations """

# Governing equations can be grouped together in no particular order

gov_eqs = [Cp_ratio, SFEE, Enth, Adia_comp]



# Create a class of objects for each station through the engine

class Station:
    def __init__(self, governing_eqs, **known_vals):
        
        
        
        # Create a dictionary of values that define a station
        self.st_vars = { 'v'    :   None,
                         'p'    :   None,
                         'T'    :   None,
                         'gam'  :   Rational(7,5),
                         'Cp'   :   None,
                         'h'    :   None,
                         'm_dot':   None,
                         'Cv'   :   None }
        
        # Update the dictionary with any known values
        self.st_vars.update(known_vals)
        
        
        # Substitute any known values into the governing equations
        self.st_eqs = [eq.subs(self.st_vars) for eq in governing_eqs]
        
        
        # Replace all dictionary values with sympified values/floats
        for key, value in self.st_vars.items():
            self.st_vars[key] = S(value)      
        
        # Solve all governing equations simultaneously for any unknown values that can be calculated
        solutions = solve(self.st_eqs, list(self.st_vars.keys()), dict = True)
        
        print(solutions)
        
        # Include any solved results in the dictionary
        self.Include_sols(solutions)
           
    
    def From_prev_st(self, prev_st, **inputs):
        """
        Use the state of a previous station to calculate values of this station, including any inputs or outputs between them

        Parameters
        ----------
        prev_st : Station object
            The previous station to calculate new values from.
        **inputs : symbol = value
            Any inputs between stations (eg work). Optional.

        Returns
        -------
        Dict
            All inputs (eg work) between the stations

        """
        #Create dictionary of potential inputs
        all_inpts = { 'W'    :   None }
        
        # Update potential inputs with given values
        all_inpts.update(inputs)
        
        # Create a dictionary of values from the previous station with keys as: 'value_in'
        in_st_vars = dict([(key + '_in', value) for key, value in prev_st.State().items()])
        
        # Create dictionary of values from this station with keys as 'value_out'
        out_st_vars = dict([(key + '_out', value) for key, value in self.st_vars.items()])
        
        # Concatenate these dictionaries and any inputs/outputs
        all_st_vars = dict(in_st_vars, **dict(out_st_vars, **all_inpts))
        
        # Substitute all values into *this state's* governing equations (only for this method, will not permanently alter this station's equations)
        temp_st_eqs = [eq.subs(all_st_vars) for eq in self.st_eqs]
        
        # Solve for unknown 'out' values
        solutions = solve(temp_st_eqs, list(all_st_vars.keys()), dict = True)
        
        print(solutions)
        
        # Include any solved results in the dictionary
        self.Include_sols(solutions, modifier = '_out')
        
        # Return any solved inputs
        self.Include_sols(solutions, all_inpts)
        
        return all_inpts
        
    def State(self):
        """
        Display the state values of the current station

        Returns
        -------
        Dict
            A dictionary of state variables and their values or None if unknown.

        """
        return self.st_vars
    
    def Include_sols(self, solutions, dictionary = None, modifier = None):
        dictionary = dictionary if dictionary is not None else self.st_vars
        
        for key in dictionary:
            try:
                # If there are multiple solutions, uses first returned. No intelligent solution selection possible yet (because assumptions won't work)
                if modifier:
                    dictionary[key] = solutions[0][sympify(key + modifier)]
                else:
                    dictionary[key] = solutions[0][sympify(key)]
                
                print(key, 'solved')
                
            except:
                
                if dictionary[key]:
                    print(key, 'known')
                
                else: 
                    print(key,'not solvable')
    

""" Set up stations in engine """

# Example 1:

print('------- Station 1 --------')
St1 = Station(gov_eqs, m_dot = 1, v = 0, p = 100000, h = 0.01, Cv = 720, T = 293.15)
print('------- Station 2 --------')
St2 = Station(gov_eqs, m_dot = 1, v = 0.1, Cv = 720)

# Solve station 2 from station 1, assuming work input of 2000 J/s
print('------- Station 1 --> Station 2 --------')
inputs = St2.From_prev_st(St1, W = -2000)

print('State variables at Station 1:', St1.State())
print('State variables at Station 2:', St2.State())
print('Inputs:', inputs)

# Example 2:
    
print('------- Station 3 --------')
St3 = Station(gov_eqs, m_dot = 1, v = 0, p = 100000, h = 0.01, Cv = 720, T = 293.15)
print('------- Station 4 --------')
St4 = Station(gov_eqs, m_dot = 1, v = 0.1, Cv = 720, T = 295.134122023810)

# Solve station 2 from station 1 with known temperature increase
print('------- Station 3 --> Station 4 --------')
inputs = St4.From_prev_st(St1)

print('State variables at Station 3:', St3.State())
print('State variables at Station 4:', St4.State())
print('Inputs:', inputs)