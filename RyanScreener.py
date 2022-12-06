# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 16:06:03 2022

@author: marca
"""

import pandas as pd
import pandas_ta as ta
import requests
import numpy as np
from scipy.stats import percentileofscore as score
import xlsxwriter
from statistics import mean
import bs4
import yfinance as yf
import time


def ryan_algo(day):
    
    s = time.perf_counter()
    

    print('Gathering ticker names')
    
    res = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    
    res.raise_for_status()
    
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    
    tag_list = soup.select("a[class='external text']")
    
    ticker_list = []
    
    for tag in tag_list:
        text = tag.getText()
        if len(text) <= 4:
            ticker_list.append(text)
            
    for t in range(len(ticker_list) - 1):
        if ticker_list[t] == 'BF.B':
            del ticker_list[t]
            
    df_dict = {}
    MomoStrategy = ta.Strategy(
    name="Ryan Momo",
    description="RSI",
    ta=[
    {"kind": "rsi"}
   
]
)
    short_lb = 50
    long_lb = 200
    
    
    for ticker in ticker_list:
        
        print(f'Calculating metrics for {ticker}...')
        
        ticker_df = pd.DataFrame()

        ticker_df = ticker_df.ta.ticker(ticker, period='1y')

        ticker_df.ta.strategy(MomoStrategy)
        
        ticker_df['SMA_50'] = ticker_df['Close'].rolling(window=short_lb, min_periods=1, center=False).mean()
        ticker_df['SMA_200'] = ticker_df['Close'].rolling(window=long_lb, min_periods=1, center=False).mean()
        
        df_dict[ticker] = ticker_df
        
        
    print('Creating Final DataFrame and Golden Crosses')
        
    my_columns = ['Ticker',
                  'SMA 50',
                  'SMA 200',
                  'SMA signal',
                  'Golden Cross Index',
                  'RSI',
                  'RSI signal',
                  'Signal score']
        
    final_df = pd.DataFrame(columns=my_columns)
    
    print(final_df.columns)
        
    for df in df_dict:
        
        
        
        final_df.loc[len(final_df.index)] = [df,
            df_dict[df].loc[f'{day} 00:00:00-05:00']['SMA_50'],
            df_dict[df].loc[f'{day} 00:00:00-05:00']['SMA_200'],
            'N/A',
            'N/A',
            df_dict[df].loc[f'{day} 00:00:00-05:00']['RSI_14'],
            'N/A',
            'N/A'
            ]
        
        ticker = df_dict[df][::-1]
        
        golden = pd.DataFrame(index=ticker.index)
        
        golden['Diffs'] = ticker['SMA_50'] - ticker['SMA_200']
        
        diffs = np.array(golden['Diffs'])
        
        zero_crossings = np.where(np.diff(np.sign(diffs)) > 0)[0]
        
        try:
        
            recent_index = zero_crossings[0]
            final_df.loc[final_df.Ticker == df, 'Golden Cross Index'] = recent_index
            
        except IndexError:
            
            final_df.loc[final_df.Ticker == df, 'Golden Cross Index'] = 1000
        
    final_df.dropna(inplace=True)
    for row in final_df.index:
        
        if final_df.loc[row, 'SMA 50'] > final_df.loc[row, 'SMA 200']:
            
            final_df.loc[row, 'SMA signal'] = 1.0
            
        else:
            final_df.loc[row, 'SMA signal'] = -1.0
            
        
        final_df.loc[row, 'RSI signal'] = 1 - (score(final_df['RSI'], final_df.loc[row, 'RSI'])/100)
            
        if final_df.loc[row, 'RSI'] < 30:
            final_df.loc[row, 'RSI signal'] = 1.0
            
        
            
    final_df['Golden Cross Percentile'] = 1 - final_df['Golden Cross Index'].rank(pct=True, ascending=True)
        
    
    
    print('Calculating momentum signal scores')
    
    signal_columns = ['SMA signal', 'RSI signal', 'Golden Cross Percentile']
    for row in final_df.index:
        signal_values = []
        
        for signal in signal_columns:
            signal_values.append(final_df.loc[row, signal])
        
        final_df.loc[row, 'Signal score'] = mean(signal_values)
        
        
        
    final_df.sort_values('Signal score', ascending=False, inplace=True)
    #final_df = final_df[:50]
    final_df.reset_index(inplace=True, drop=True)
    
    f = time.perf_counter() - s
    
    print(f"Runtime: {f} seconds")
    
    return final_df
        
        
if __name__ == "__main__":
    dataframe = ryan_algo('2022-12-01')
    print(dataframe)
    

    
    writer = pd.ExcelWriter('ryan_strategy.xlsx', engine='xlsxwriter')

    dataframe.to_excel(writer, sheet_name='Ryan Strategy', index=False)

    writer.save()
    