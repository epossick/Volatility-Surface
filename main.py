import numpy as np
from datetime import date, datetime, timedelta
import yfinance as yf
import pandas as pd
from bs4.element import Script
import requests
from bs4 import BeautifulSoup

"""Inputs"""
ticker=input("Ticker: ")
#ticker="SPY"
#rf=input("Risk-free rate: ")
#n=input("# of steps: ")
rf=.0008

"""Program scrapes yahoo finance to get stock price"""

url = "https://finance.yahoo.com/quote/{}?p={}"
response=requests.get(url.format(ticker,ticker))
soup=BeautifulSoup(response.text,'html.parser')
#stock price
price=soup.find('fin-streamer',{'class':"Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text




"""Limits for Data"""
# Only Friday expirations (isoweekday==5)
# Only expirations within a year (365 days)
# Only OTM strikes
# Implied Volatility is priced with midpoint price
# Only options that were traded within 5 days
# Take out options without a bid or ask
# Take out options with a bid/ask spread over 1.00
# Regression done with nonlinear least squares optimization method