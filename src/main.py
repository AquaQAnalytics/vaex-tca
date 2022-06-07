import numpy as np
import pandas as pd
import vaex
from fastapi import FastAPI

appDescription = """
## Description

API to provide TCA for trade data using Vaex and NYSE TAQ data.

## Features

TCA calculated:

* **Mid**
* **VWAP**

## Terms & Contact Info
"""

# tags for post request
metatags = [

    {
        "name": "TCA",
        "description": "Calculate Mid and VWAP of trades."
    }
]

# new fastapi instance
app = FastAPI(

    openapi_tags = metatags,
    title="VAEX TCA",
    description = appDescription,
    version="0.0.1",
    terms_of_service="https://www.aquaq.co.uk",
    contact={

        "name": "AquaQ",
        "url": "https://www.aquaq.co.uk",
        "email": "cameron.webb@aquaq.co.uk"
    }
)

quotes = vaex.open('20191007_quote_S_copy2.arrow') # read in quotes file
quotes['Mid_Price'] = (quotes['Offer_Price'] + quotes['Bid_Price']) / 2 # calculate mid
tradesAll = vaex.open('20191007_trade_copy2.arrow') # read in all trades
starts_with_S = tradesAll['Symbol'].str.startswith('S')
tradesAll = tradesAll[(starts_with_S)] # quotes only have symbols starting w/S

@app.post("/api/v1/TCA", tags=["TCA"]) # post request: takes json of trades as argument
async def Transaction_Cost_Analysis(tradesJSON):

    '''
    **tradesJSON:** List of JSON objects - _str_

        [
            {
                "Time":"2019-10-07T06:39:06.164499Z",
                "Symbol":"S",
                "Trade_Volume":50,
                "Trade_Price":6.23
            }
        ]
    **Time:** ISO Timestamp (microseconds) - _str_\n
    **Symbol:** Stock symbol - _str_\n
    **Trade_Volume:** Number of shares traded - _int_\n
    **Trade_Price:** Share price - _float_\n
    **Returns:** tradesJSON with additional columns (Mid and VWAP) - _str_
    '''

    trades = pd.read_json(tradesJSON,orient='records') # convert json to pandas df
    trades['Time'] = pd.to_datetime(trades['Time'],format='%Y-%m-%dT%H:%M:%S.%fZ') # convert iso time string to datetime

    def tca(tradeSymbol, tradeTime): # filter quotes to find mid and calculate vwap

        newQuotes = quotes[(quotes.Symbol == tradeSymbol) & (quotes.Time <= np.datetime64(tradeTime))]
        mid = (newQuotes.Mid_Price[-1:].values[0]).as_py() #mid = newQuotes.last(newQuotes.Mid_Price)

        vwapFilter = ((tradesAll.Symbol == tradeSymbol) & (tradesAll.Time <= np.datetime64(tradeTime)) & \
                (tradesAll.Time >= (np.datetime64(tradeTime) - np.timedelta64(15, 'm'))))
        vwapTrades = tradesAll[(vwapFilter)]
        vwap = (vwapTrades.Trade_Price * vwapTrades.Trade_Volume).sum() / vwapTrades.Trade_Volume.sum()

        return round(mid,2), round(vwap,2) # returns new columns for trades df

    trades[['Mid_Price','VWAP']] = trades.apply(lambda df: tca(df.Symbol, df.Time), axis=1, result_type='expand')

    return trades.to_json(orient='records',date_format='iso',date_unit='us') # return trades df w/new columns as json

