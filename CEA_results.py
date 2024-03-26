# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 01:14:31 2024

@author: Bobke
"""
import numpy as np
import matplotlib.pyplot as plt

#atmospheric
"""
P_c = np.array([2.0265, 2.2292, 2.3305])
OF = np.array([45])
v_j = np.array([664.6, 749.2, 768.1])
"""

P_c = np.array([1.5199, 1.6212, 1.7225,1.8238, 1.9252, 2.0265])
OF = np.array([48])
vj = np.array([519.4, 557.1, 589.9,618.8, 644.6, 667.9])

isp = vj*OF
plt.figure(1)
plt.title("isp vs Pc at OF of 48 ")
plt.plot(P_c, isp, label = "isp")
#plt.plot(turb_pr, Tmax_list, label = "Compressor Pressure Ratio")
plt.ylabel("isp (m/s)")
plt.xlabel("Chamber Pressure [Bars]")
plt.grid()
plt.savefig('isp_vs_Pc.png', dpi = 400)
plt.show()

print(isp)
P_c = 2.0265
OF_2 = np.array([48, 50, 52, 54, 56, 58, 60])
vj_2 =  np.array([667.9, 659.7, 652.0, 644.8, 638.0, 631.5, 625.4])
isp_2 = vj_2*OF_2
print(isp_2)

plt.figure(2)
plt.title("isp vs OF at Pc of 2 bars ")
plt.plot(OF_2, isp_2, label = "isp")
#plt.plot(turb_pr, Tmax_list, label = "Compressor Pressure Ratio")
plt.ylabel("isp (m/s)")
plt.xlabel("OF ratio")
plt.grid()
plt.savefig('isp_vs_OF.png', dpi = 400)
plt.show()

P_c = 1.52
OF_3 = np.array([100, 102, 104, 106, 112, 120])
vj_3 =  np.array([409.0, 406.9, 404.8, 402.8, 397.1, 390.2])
isp_3 = vj_3*OF_3
print(isp_3)

plt.figure(3)
plt.title("isp vs OF at Pc of 1.52 bars ")
plt.plot(OF_3, isp_3, label = "isp")
#plt.plot(turb_pr, Tmax_list, label = "Compressor Pressure Ratio")
plt.ylabel("isp (m/s)")
plt.xlabel("OF ratio")
plt.grid()
plt.savefig('isp_vs_OF_2.png', dpi = 400)
plt.show()