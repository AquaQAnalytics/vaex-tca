import numpy as np
import pandas as pd
import vaex
from fastapi import FastAPI

app = FastAPI() # new fastapi instance

quotes = vaex.open('20191007_quote_S_copy2.arrow') # read in quotes file
quotes['Mid'] = (quotes['Offer_Price'] + quotes['Bid_Price']) / 2 # calculate mid
quotes = quotes[['Time','Symbol','Mid']] # select relevant columns

@app.post("/api/v1/TCA") # post request: takes json of trades as argument
async def Mid_VWAP(tradesJSON):
    
    trades = pd.read_json(tradesJSON,orient='records') # convert json to pandas df
    trades['Time'] = pd.to_datetime(trades['Time'],format='%Y-%m-%dT%H:%M:%S.%fZ') # convert iso time string to datetime

    def tca(tradeSymbol, tradeTime): # filter quotes to find mid and calculate vwap
        
        newQuotes = quotes[(quotes.Symbol == tradeSymbol) & (quotes.Time <= np.datetime64(tradeTime))]
        mid = (newQuotes.Mid[-1:].values[0]).as_py() #mid = newQuotes.last(newQuotes.Mid)
        
        vwapFilter = ((trades.Symbol == tradeSymbol) & (trades.Time <= np.datetime64(tradeTime)) & \
                (trades.Time >= (np.datetime64(tradeTime) - np.timedelta64(15, 'm'))))
        vwapTrades = trades[(vwapFilter)]
        vwap = (vwapTrades.Trade_Price * vwapTrades.Trade_Volume).sum() / vwapTrades.Trade_Volume.sum()

        return round(mid,2), round(vwap,2) # returns new columns for trades df

    trades[['Mid','VWAP']] = trades.apply(lambda df: tca(df.Symbol, df.Time), axis=1, result_type='expand')

    return trades.to_json(orient='records',date_format='iso',date_unit='us') # return trades df w/new columns as json

