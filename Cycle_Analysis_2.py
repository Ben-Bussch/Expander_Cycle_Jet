# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 13:00:48 2024

@author: Bobke
"""
import os 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as integrate

try: 
    print('The home directory has been saved as: ', home_directory)
except:
    home_directory = os.path.normpath(os.getcwd())    
    print('Saving the home directory as: ', home_directory)
    
path_pentane = home_directory+'\Pentane'
path_air = home_directory+'\Air'
path_graphs = home_directory+'\Graphs'


def cp_polyfit(P, n, path):
    """Finding Cp vs Temp polynomial fit, 
    takes in pressrue (kPa, int) and polynomial degree (int)"""
    os.chdir( path)
    directories = os.listdir()
    print(directories)

    df = pd.read_csv(str(P)+".csv")
    print(df)
    #print(df.keys())
    T = df["T"]
    cp = df["Cp"]
    cp_fit_coeff = np.polynomial.polynomial.polyfit(T, cp, n)
    
    "Plotting the fit"
    cp_fit = []
    T_range = np.linspace(300, 850, 500)
    for i in T_range:
        cpi = 0
        for n in range(len(cp_fit_coeff)):
            cpi += cp_fit_coeff[n]*i**(n)
            
        cp_fit.append(cpi)
    
    os.chdir(home_directory)
    os.chdir(path_graphs)
    
    plt.figure()
    plt.title("Cp vs Temp at "+str(P)+"kPa")
    plt.plot(T, cp, "rx", label = "Data")
    plt.plot(T_range, cp_fit, linewidth = '0.75', label = "fit")
    plt.grid()
    plt.legend()
    plt.ylabel("cp [kJ/kg/K]")
    plt.xlabel("Temp [K]")
    plt.savefig("Cp_vs_T_"+str(P)+".png",dpi = 400)
    plt.show()
    os.chdir(home_directory)
    return(cp_fit_coeff)


def cp_integrand(T, cp_fit_coeff):
    cp = 0
    for n in range(len(cp_fit_coeff)):
            cp += cp_fit_coeff[n]*T**(n) 
    return cp


def turbine_work(Tmin, Tmax, cp_fit_coeff, phase_change):
    specific_power = integrate.quad(cp_integrand, Tmax, Tmin, args=(cp_fit_coeff))[0] 
    if phase_change:
        specific_power -= 366 #specific heat of vaporization pentane, kJ/kg
    return specific_power

def compressor_temp(Tmin, Tmax_guess, cp_fit_coeff, specific_power):
    run = True
    while run:
        specific_power_guess = integrate.quad(cp_integrand, Tmin, Tmax_guess, args=(cp_fit_coeff))[0] 
        #print("SP guess: ",specific_power_guess)
        #print("SP intagrate: ",specific_power)
        SP_error = specific_power - specific_power_guess 
        #print("SP error: ",SP_error)
        Tmax_guess += SP_error*1.0001 
        if SP_error < 0.001 and SP_error > -0.001:
            run = False
    print("Tmax:",Tmax_guess)
    return Tmax_guess

def T_to_P_ratio(Tmin, Tmax, gamma):
    Pr = (Tmax/Tmin)**(gamma/(gamma-1))
    return Pr

def pump_work(rho, pmin, pmax):
    """Assuming constant density fluid (more or less true until critical point
    at which rho increases so this should be an overestimate of required power)"""
    pump_specific_power =(1/rho)*(pmax-pmin)/1000 #kJ/kg/s
    return pump_specific_power
    

p_ambiant = 26200 #Pa
T_ambiant = 298.15 #K

cp_100_coeff = cp_polyfit(100, 2, path_pentane)
cp_50_K = cp_integrand(500, cp_100_coeff)

"Calculating Pump Work"
rho = 565 #at 350K, constant with pressure change up till critical pressure (33 bar) and then increases
pmin = 500000 #Pa, needs to be around 150 kPa or more to ensure condensation at 320K
cooling_pressure_drop = 600000 #Pressure drop over fuel cooling channels
heating_pressure_drop = 600000 #Pressure drop over fuel heating channels
cp_air_coeff = cp_polyfit(100, 4, path_air) #air cp is ~constant with pressure changes
bleed_ratio = 0.1
OF = 150

"Calculating Turbine Work"
Tmax_list = np.linspace(375, 575, 100) #K
turb_pr = []
comp_pr = []
Tmin = 349.65 #K, tmin for half way point for 298.15 atm temp, 120K temp diff and 576K chamber temp
for Tmax in Tmax_list:
    turbine_specific_power = turbine_work(Tmin, Tmax, cp_100_coeff, True) 
    "Assuming cp only varies with tempurature across the turbine"
    "Resonable approximation as long as there is no phase change"
    turbine_pressure_ratio = T_to_P_ratio(Tmin, Tmax , 1.09)
    print("Turbine Pressure Ratio: ", turbine_pressure_ratio)
    turb_pr.append(turbine_pressure_ratio)
    print("Turbine Specific Power:", turbine_specific_power, "kJ/kg/s")
    
    pmax = turbine_pressure_ratio*(pmin + cooling_pressure_drop) + heating_pressure_drop
    pump_specific_power = pump_work(rho, pmin, pmax)
    print("Pump specific power required:", pump_specific_power, "kJ/kg/s")
    
    "Calculating Compressor Work"
    
    compressor_specific_power = -(turbine_specific_power+pump_specific_power)/(OF*bleed_ratio)
    print("Compressor Specific Power: ", compressor_specific_power, "kJ/kg/s")
    T_compressor = compressor_temp(T_ambiant, 500, cp_air_coeff, compressor_specific_power) 
    #print("Tempurature at end of compressor: ",T_compressor,"K")
    
    compressor_p_ratio = T_to_P_ratio(T_ambiant,T_compressor, 1.4)
    #print("Compressor Pressure ratio: ", compressor_p_ratio)
    P_compressor = compressor_p_ratio*p_ambiant
    comp_pr.append(compressor_p_ratio)
    



  
os.chdir(path_graphs)

plt.figure(1)
plt.title("Compressor Ratio vs Turbine Pressure ratio at "+str(bleed_ratio)+" Bleed ratio and "+str(OF)+" OF")
plt.plot(turb_pr, comp_pr, label = "Compressor Pressure Ratio")
#plt.plot(turb_pr, Tmax_list, label = "Compressor Pressure Ratio")
plt.ylabel("Compressor Pressure Ratio")
plt.xlabel("Turbine Pressure Ratio")
plt.grid()
plt.savefig('Comp_vs_Turb_0.15_bleed_10km.png', dpi = 400)
plt.show()

plt.figure(2)
plt.title("Compressor Ratio vs net Tempurature Change across Cycle "+str(bleed_ratio)+" Bleed ratio and "+str(OF)+" OF")
plt.plot(Tmax_list-Tmin, comp_pr, label = "Compressor Pressure Ratio")
#plt.plot(turb_pr, Tmax_list, label = "Compressor Pressure Ratio")
plt.ylabel("Compressor Pressure Ratio")
plt.xlabel("Tempurature difference Across Cycle")
plt.grid()
plt.savefig('Comp_vs_delta_T_0.1_bleed_10km.png', dpi = 400)
plt.show()


os.chdir(home_directory)
    



    







    

    
