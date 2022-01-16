from scipy.optimize import curve_fit
import statsmodels.api as sm
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from matplotlib import cm
import numpy as np
import math as m
from yfinance import ticker
import initialize_data
import main
from datetime import datetime, date, timedelta
""" 1. Time is in calendar days (365) and not trading days (252) in initialize_data.py
    2. Rates are constant (I will fix this later to incorporate futures curve) 
           """
ticker=main.ticker
#data from initialize_data.py
df=initialize_data.clean
stock=float(main.price)
strikes=initialize_data.strike
imp_vol=initialize_data.implied_volatility
expirations=(initialize_data.expirations)

#def implied_volatility():



#time as a percent of year
time=np.zeros(len(df))
for i in range(len(df)):
    time[i]=(initialize_data.time_until_expiration()[i])/365
#constant annual rate
rate=main.rf  
#forward price of stock at expiration     
forward=np.zeros(len(df))
for i in range(len(df)):
    forward[i]=stock*m.exp(rate*time[i])
#moneyness   (positive for OTM calls, negative for OTM puts)
moneyness=np.zeros(len(df))
for i in range(len(df)):
    moneyness[i]=m.log(strikes[i]/forward[i])/(m.sqrt(time[i]))
    #moneyness[i]=strikes[i]/forward[i]-1


matrix=np.zeros([len(df),4])
for i in range(len(df)):
    for j in range(len(df)):
        #matrix1[j,0]=1
        matrix[j,0]=moneyness[j]
        matrix[j,1]=moneyness[j]**2
        matrix[j,2]=time[j]
        matrix[j,3]=time[j]*moneyness[j]

"""statsmodel"""
x_coord=matrix
y_coord=imp_vol
x_coord=sm.add_constant(x_coord)
est=sm.OLS(y_coord,x_coord).fit()
#print(est.summary())
x=np.transpose(matrix)

"""scipy"""
def volatility_surface(x,a,b,c,d,f):
    return a + b*x[0] + c*x[1] + d*x[2] + f*x[3]
popt, pcov=curve_fit(volatility_surface,x,imp_vol)
#print(popt)
#print(pcov)
"""predicted Y values"""
ydata=volatility_surface(x,popt[0],popt[1],popt[2],popt[3],popt[4])


"""Returns summary statistics and RMSE"""
print(est.summary())
print("RMSE: ",m.sqrt(sm.tools.eval_measures.mse(y_coord,ydata)))

"""Plot graph"""
fig=plt.figure()
ax=plt.axes(projection='3d')
x=moneyness
y=time
z= popt[0] + popt[1]*x + popt[2]*x**2 + popt[3]*y + popt[4]*y*x 
ax.plot_trisurf(x,y,z,cmap='rainbow')
#ax.scatter(x,y,imp_vol,color='black')
ax.set_xlabel('moneyness')
ax.set_ylabel('Expiration')
ax.set_zlabel('volatility')
ax.set_title(ticker+' volatility surface')
plt.show()

