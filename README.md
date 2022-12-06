# RyanStockScreener

For Windows

A stock screener inspired by the simple trading strategy of my friend Ryan.  This screener ranks stocks based on SMA, RSI, and how recently they last had a Golden Cross.

Stock ticker data scraped from Wikipedia (https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).  Financial data gathered from Yahoo Finance.

This program first scrapes an up-to-date list of all tickers in the SP500 from Wikipedia.  Then, it uses python-ta and yfinance as a framework for gathering the 1-year daily historical price data from Yahoo Finance for each ticker, calculates the RSI and 50-day SMA and 200-day SMA for each stock, then stores them in a DataFrame.  A final DataFrame is then generated, and technical signals/rankings are calculated.  For the SMA, a simple boolean is used, to select stocks in which the 50 SMA is currently above the 200 SMA.  RSI's are ranked by their inverse percentile (lower RSI being better).  The most recent golden cross (when the 50 SMA rises above the 200 SMA) is calculated, and also ranked by inverse percentile (the more recent, the better).  Each of these percentiles are then averaged to create a single overarching score, and the stocks are then ranked by that score.

Returns a .xlsx file in your CWD.

This is my first stock picker that uses a custom hybrid of indicator interpretation (boolean, simple numeric ranking, and incorporating the number of days from a specific event) to create one unified score.  From here I'd like to keep working on honing these more simple, traditional indicators for stock screening, before moving on to machine learning incorporation.


NOTE:  This program takes ~ 1.5 hours to run on my machine.  I am working on improving the time efficiency.
