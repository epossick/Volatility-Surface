from datetime import date, datetime, time, timedelta
import yfinance as yf
import pandas as pd
import main
import numpy as np


"""Setup for volatility surface and implied binomial tree. Cleans data for
        1. OTM strikes
        2. Options that haven't traded in 1 week
        3. Options that are illiquid (no bid)
        """
ticker=yf.Ticker(main.ticker)
#find all expirations
exp=list(ticker.options)

#Delete expiration if todays date
if datetime.isoweekday(pd.Timestamp(exp[0]))==datetime.isoweekday(pd.Timestamp.today()):
    del exp[0]

#Returns only friday expirations within 1 year
expirations=[]
for i in exp:
    if datetime.isoweekday(pd.Timestamp(i))==5 and pd.Timestamp(i).tz_localize('US/Eastern')\
        <(pd.Timestamp.today().tz_localize('US/Eastern')+pd.Timedelta(days=365)):
        expirations.append(i)

#create dataframe and append option chains from every expiration
options=pd.DataFrame()
for e in expirations:
    opt=ticker.option_chain(e)
    opt=pd.DataFrame().append(opt.calls).append(opt.puts)
    opt["expirationDate"]=e
    options=options.append(opt,ignore_index=True)

#clean unwanted columns
clean=options.drop(['contractSymbol','lastPrice','change','percentChange','volume',\
    'openInterest','contractSize','currency'],axis=1)

moneyness=clean['inTheMoney'].tolist()
last_trade=clean['lastTradeDate'].tolist()
bid=clean['bid'].tolist()
ask=clean['ask'].tolist()

#Clean data points for instrinsic value, lack of trades, expirations, and illiquidity
for i in range(len(clean)):
    if moneyness[i]==True:
        clean=clean.drop(index=[i])
    elif pd.Timestamp(last_trade[i]).tz_localize('US/Eastern')<=\
        pd.Timestamp.today().tz_localize('US/Eastern')-pd.Timedelta(days=5):
        clean=clean.drop(index=[i])
    elif bid[i]<0.005 or ask[i]<0.005 or abs(ask[i]-bid[i])>=1:
        clean=clean.drop(index=[i])
    else:
        continue
clean=clean.reset_index(drop=True)

#get all data into own list 
new_bid=clean['bid'].tolist()
new_ask=clean['ask'].tolist()
strike=clean['strike'].tolist()
implied_volatility=clean['impliedVolatility'].tolist()
ex=clean['expirationDate'].tolist()

#return midpoints (input as option price for inplied binomial
midpoints=np.zeros(len(clean))
def get_midpoint():
    for i in range(len(clean)):
        midpoints[i]=((new_bid[i]+new_ask[i])/2)
    return midpoints

#return time until expiration (input as time for binomial models)
def time_until_expiration():
    time=[]
    for t in range(len(clean)):
        ttm=date.fromisoformat(ex[t])-date.today()
        time.append(ttm.days)
    return time
stock=float(main.price)

#get strike flags (call or put)
def get_flags():   
    flags=[]
    for f in range(len(clean)):
        if strike[f]>stock:
            flag='c'
            flags.append(flag)
        else:
            flag='p'
            flags.append(flag)
    return flags
