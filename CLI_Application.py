# Import the required libraries and dependencies
import os
import sys
import datetime
import requests
import json
import numpy as np
import pandas as pd
import panel as pn
from panel.interact import interact
from panel import widgets
from dotenv import load_dotenv, find_dotenv
import hvplot.pandas
# %matplotlib inline
#pn.extension("plotly")

# CLI Libraries
import fire
import questionary
import sqlalchemy


print("Loading the enviroment & verifying Polygon Key...")

# Load enviroment variables
load_dotenv(find_dotenv())
# Set Polygon API key
polygon_api_key = os.getenv("POLYGON_API")

# Verifying Polygon key load 
# if type(polygon_api_key) == str:
  #  print("Polygon Key failed to load")
   # real_estate_cli = True
#else:
 #   print("Polygon Key failed to load")
  #  real_estate_cli = False

print(type(polygon_api_key)) 

    
# Make an API call to access the current prices for BEKE, OPEN, RDFN, Z, EXPI, AMT, CBRE, WY, ESS, AVB, ARE and SPY. (Credits: Binoy Das - Slack post)
def fetch_stock_aggregates(tickers, multiplier=1, timespan="day", start_date='', end_date='', columns=['Close'], key=polygon_api_key):

    column_mappings = {'c': 'Close', 'h': 'High', 'l':'Low', 'n':'Transactions', 'o':'Open', 'v':'Volume', 'vw':'Adjusted'}
    data_frames = {}    
    if end_date == '':
        end_date = datetime.date.today().strftime('%Y-%m-%d')
    if start_date == '':
        start_date = (datetime.date.today()-datetime.timedelta(days=1)).strftime('%Y-%m-%d')    
        
    for ticker in tickers:
        if 'polygon' in sys.modules:                
            with RESTClient(key) as polygon_client:
                response_json = polygon_client.stocks_equities_aggregates(ticker, multiplier, timespan, start_date, end_date, limit=50000)
                stock_df = pd.DataFrame(response_json.results)
                print(f"{timespan.capitalize()} aggregates for {response_json.ticker} between {start_date} and {end_date} fetched.")
        else:
            url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{start_date}/{end_date}?sort=asc&limit=50000&apiKey={key}"
            print(url)
            response_json = requests.get(url).json()
            stock_df = pd.DataFrame(response_json['results'])
            print(f"{timespan.capitalize()} aggregates for {response_json['ticker']} between {start_date} and {end_date} fetched.")
        
        stock_df["Date"] = pd.to_datetime(stock_df["t"].div(1000), unit='s')
        stock_df = stock_df.drop(['t'], axis=1)
        stock_df = stock_df.set_index("Date")
        
        column_names = []
        for column in stock_df.columns:
            if column in column_mappings.keys():
                column_name = column_mappings[column]
            if column_name in columns:
                column_names.append(column_name)
            else:
                stock_df = stock_df.drop([column], axis=1)
        stock_df.columns = column_names
        data_frames[ticker] = stock_df
        
    merged_df = pd.concat(data_frames.values(), axis=1, keys=data_frames.keys())
    merged_df=merged_df.dropna()
    
    return merged_df


# Function to convert df to pct change
def pct(stock_df):
    pct_change_df = pd.DataFrame()
    for col in stock_df.columns:
        pct_change_df[col[0]] = stock_df[col[0]][col[1]]
    pct_change_df = pct_change_df.pct_change()
    
    return pct_change_df


def cum_returns(pct_df):
    cumulative_returns = (1 + pct_df).cumprod()
    
    return cumulative_returns


def std_dev(stock_df):
    std_dev_srtd = stocks_df.std().sort_values()
    
    return std_dev_srtd

# Initialize stock_df
def init_stock():
    # Initializing tickers chosen for analysis
    init_tickers = ['BEKE', 'OPEN', 'RDFN', 'Z', 'SPY']
    
    # Initializing earliest possible start date given real estate IPO dates
    init_startdate = '2021-01-01'
    
    # Fetch stock data
    init_stock_df = fetch_stock_aggregates(['BEKE', 'OPEN', 'RDFN', 'Z', 'SPY'], start_date='2021-01-01')
    
    # Cleaning code
    init_stock_df.dropna(inplace=True)
    
    # Fetching stock data    
    #stock_df = fetch_stock_aggregates(['BEKE', 'OPEN', 'RDFN', 'Z'], start_date='2021-01-01')

    #spy_df = fetch_stock_aggregates(['SPY'], start_date='2021-01-01')
    
    return init_tickers, init_startdate, init_stock_df


def ytd(cum_df):
    # YTD returns/drop index column
    df_bar = pd.DataFrame({"Stock": cum_df.columns, "Return": (cum_df.iloc[-1]-1).mul(100)})
    # Droppimg the index -- WHY
    df_bar = df_bar.reset_index().drop(["index"], axis=1)
    
    return df_bar


def std_srt(stock_df):
    # Calculating standard deviations
    standard_deviation = stock_df.std().sort_values()
    
    # Calculating the annualized standard deviation (252 trading days) 
    annualized_standard_deviation = standard_deviation * np.sqrt(252)
    
    return standard_deviation, annualized_standard_deviation


def sharpe(pct_df, ann_std_df):
    # Calculating Average annual return for Sharpe ratio
    average_annual_return = pct_df.mean() * 252
    
    # We calculate the annualized Sharpe Ratios for each of the portfolios and the S&P 500.
    sharpe_ratios = average_annual_return/ann_std_df
        
    return sharpe_ratios.sort_values()

def run():
    print("Loading stock data...")
    
    # Initalizing data
    tickers, startdate, stock_df = init_stock()
    
    # Printing initialized values
    print(f"The tickers chosen for analysis are: {', '.join(tickers)}")
    print(f"Analysis on ticker data starting {startdate}")

    # Printing returned data
    print(f"Initial stock Dataframe:\n {stock_df.head()}")    
        
          
    real_estate_cli = True
    
    while real_estate_cli:    
        choice = questionary.select(
            "Which scope of analysis would you prefer?",
            choices=["Complete", "Specific", "Quit"]
        ).ask()
        
        if choice == "Quit":
            real_estate_cli = False
            print("Thank you for using our Real Estate Analysis CLI") 
            
        elif choice == "Specific":
            choice = questionary.select(
                "Which analysis method would you like to perform for the given real estate stocks?",
                choices=["Daily Returns", "Cumulative Returns", "YTD Returns", "Standard Deviation", "Sharpe Ratio", "Beta"]
            ).ask() 
            
            
        if choice == "Daily Returns":
            # Running through the function for pct_change
            pct_df = pct(stock_df)
            
            print(f"This is the first five rows of the Percent Change DataFrame:\n {pct_df.head()}")

            #Plotting daily returns on all 10 portfolios. - Won't work with CLI
            #pct_df.hvplot(
             #   xlabel="Date", 
             #   ylabel="Daily Returns",
             #  title="Daily Returns Real Estate Stocks & SPY (1/2021 - 4/2022)",
            #width=1000, 
            #height=500
            #)
        
        elif choice == "Cumulative Returns":
            # Fetching percent change of DataFrame
            pct_df = pct(stock_df)
            
            # Calculating the cumulative returns of the 10 portfolios and S&P 500
            cumulative_returns = cum_returns(pct_df)

            print(f"This is the first five rows of the Cumulative Returns DataFrame:\n {cumulative_returns.head()}")
            
        
        elif choice == "YTD Returns":
            pct_df = pct(stock_df)
            cumulative_returns_df = cum_returns(pct_df)
            ytd_df = ytd(cumulative_returns_df)
            
            print(f"This is the first five rows of the Year-to-Date Returns DataFrame:\n {ytd_df.head()}")
            
            
        elif choice == "Standard Deviation":
            pct_df = pct(stock_df)
            std_srt_df, ann_std_srt_df = std_srt(pct_df)
            
            print(f"Standard Deviations (smallest to largest):\n {std_srt_df}")
            
            print(f"Standard Deviations (smallest to largest):\n {ann_std_srt_df}")

        elif choice == "Sharpe Ratio":
            pct_df = pct(stock_df)
            std_df, ann_std_df = std_srt(pct_df)

            sharpe_ratios_srt = sharpe(std_df, ann_std_df)
            print(f"Sharpe Ratios (smallest to largest):\n {sharpe_ratios_srt}")
            
        
            
if __name__ == "__main__":
    fire.Fire(run)