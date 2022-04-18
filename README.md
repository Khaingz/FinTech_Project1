# FinTech_Project1
Project1 Real Estate Stock Analysis

# UWFinTech_Group4_Project1

## Project Title
Real Estate Stock Analysis - 2 year

## Software Technologies used
Jupyter Notebook, Python, Pandas.

## Datasets to be Used
## API 
[Polygon API](https://polygon.io/docs/stocks/)

## Stock List 
'AMT', 'CBRE', 'AVB', 'ESS', 'SPY'

## Project Description
Build a program which analyzes the stocks of several big real estate companies. Analyze the real estate stock compare to SPN 500. 

The analysis:
* Determine the fund with the most investment potential based on key risk-management metrics:
* the daily returns, 
* standard deviations
* Sharpe ratios
* betas
* Monte Carlo Sim
* Other helpful interactive visualizations

The program will be accessed via a CLI Web Application (Voila)


## Outline , Financial programming
### Libraries & Dependencies: 
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
from dotenv import load_dotenv
import hvplot.pandas
%matplotlib inline
import warnings
warnings.filterwarnings('ignore')
from MCForecastTools import MCSimulation

1.) API to pull stock information into DF - Polygon
#Set Polygon API key
polygon_api_key = os.getenv("POLYGON_API")

2.) Data cleaning/slicing
Fetching Polygon data and converting it to pct_change at the same time
stock_df = fetch_stock_aggregates(['AMT', 'CBRE', 'AVB', 'ESS', 'SPY'], start_date='2021-01-01')

### Data cleaning - Dropping first NA row from DF
all_stocks_df.dropna(inplace=True)

3.) Analysis
* Determine the fund with the most investment potential based on key risk-management metrics:
* the daily returns
#Plotting daily returns on all 5 portfolios.
all_stocks_df.hvplot(
    xlabel="Trading Days", 
    ylabel= "Daily Returns", 
    title="Daily Returns: Selected Real Estate Stocks (Jan 4th 2021 - Present)",
    width=1000, 
    height=500
)

* Cumulative Returns
### Calculating and plotting the cumulative returns of the 5 portfolios and S&P 500
cumulative_returns = (1 + all_stocks_df).cumprod()

### Reviewing the first 5 rows of the cumulative returns DataFrame
cumulative_returns.head()
### Visualizing the cumulative returns using the Pandas hvplot function
cumulative_returns.hvplot(
    xlabel="Trading Days", 
    ylabel="Cumulative Return", 
    title="Cumulative Returns: Selected Real Estate Stocks (Jan 4th 2021 - Present)",
    width=1000, 
    height=500
)
* standard deviations
### Calculating Standard deviation for all 5 potfolios and SPY
standard_deviation = all_stocks_df.std()
standard_deviation.sort_values()

### Calculating the annualized standard deviation (252 trading days) 
#Reviewing the annual standard deviations from smallest to largest
annualized_standard_deviation = standard_deviation * np.sqrt(252)
annualized_standard_deviation.sort_values()

### Plotting 21-day rolling standard deviation(months SMA)
all_stocks_sma_21 = all_stocks_df.rolling(window=21).std()

### Plotting the stocks df with a 21-day rolling window 
all_stocks_sma_21.dropna().hvplot(title="21-Day SMA: Selected RE Stocks (Jan 4th 2021 - Present)", width=1000, height=500 )

* Sharpe ratios
### Calculating Average annual return for Sharpe ratio
average_annual_return = all_stocks_df.mean() * 252

### Average annual return sorted lowest to highest
average_annual_return.sort_values()

### We calculate the annualized Sharpe Ratios for each of the portfolios and the S&P 500.
sharpe_ratios = average_annual_return/annualized_standard_deviation

### Sharpe ratios sorted lowest to highest
sharpe_ratios.sort_values()

### Visualizing Bar plotting of Sharpe Ratios
sharpe_ratios.hvplot.bar(
    height=500,
    width=1000,
    xlabel= "Tickers", 
    ylabel="Sharpe Ratio", 
    title= "Sharpe Ratios: Selected RE Stocks (Jan 4th 2021 - Present)")
    
### we will need to evaluate how the portfolios react relative to the broader market SPY. 
#Calculate the variance of the S&P 500 using a rolling 60-day window.
snp_rolling_60_variance = all_stocks_df["SPY"].rolling(window=60).var()

# Reviewing the last 5 of the DataFrame
snp_rolling_60_variance.tail()

* betas
### Calculate (AVB, ESS, CBRE) the covariance using a 60-day rolling window
### Calculate (AVB, ESS, CBRE) the beta based on the 60-day rolling covariance compared to the market (S&P 500)
### Calculate (AVB, ESS, CBRE) the average of the 60-day rolling beta

* Dry betas calculations
### Calculating all 3 portolio's covariance using a 60-day rolling window 
rolling_60_covariance = all_stocks_df[["AVB", "ESS", "CBRE"]].rolling(window=60).cov(all_stocks_df["SPY"])
rolling_60_covariance.tail()

### Calculating Beta's
avb_rolling_60_beta = rolling_60_covariance["AVB"]/snp_rolling_60_variance
ess_rolling_60_beta = rolling_60_covariance["ESS"]/snp_rolling_60_variance
cbre_rolling_60_beta = rolling_60_covariance["CBRE"]/snp_rolling_60_variance

### Overlay Plot of all Betas to compare one to another
overlay_plot_bar = (cbre_plot_bar * ess_plot_bar * avb_plot_bar).opts(
    title="60-Day Rolling Beta Overlay Plot for AVB, ESS, CBRE",  
    width=1000, 
    height=500,
)

* Interactive Dashboard
### Interactive Dashboard, that can be launched outside jupyter noteook, to overview all 3 stocks Beta and Overlay Plot as tabs
dashboard = pn.Tabs(
    ("All Stocks", overlay_plot_bar),
    ("AVB", avb_plot_bar),
    ("ESS", ess_plot_bar),
    ("CBRE", cbre_plot_bar)
)

### Use this command to display outside jupyter, throught terminal, maybe can be used in CLI application (!panel serve Real_estate_stocks_analysis.ipynb --show)
dashboard.servable()

* Monte Carlo Sim
### Monte Carlo Simulation
top_3_tickers = ["AVB", "ESS", "CBRE"]

mc_top3_df = pd.DataFrame(stock_df[top_3_tickers])

for ticker in top_3_tickers:
    mc_top3_df.columns = mc_top3_df.columns.values
    mc_top3_df.columns = pd.MultiIndex.from_tuples(mc_top3_df.rename(columns={(ticker, 'Close'): (ticker, 'close')}))

mc_top3_df

### Configure the Monte Carlo simulation to forecast 10 years cumulative returns
### The weights should be split equal between all 3 stocks
### Run 500 samples.
MC_ten_year = MCSimulation(
    portfolio_data = mc_top3_df,
    weights = [.50, .50, .50],
    num_simulation = 500,
    num_trading_days = 252 * 10
)
### Review the simulation input data
MC_ten_year.portfolio_data.head()

### Run the Monte Carlo simulation to forecast 10 years cumulative returns
MC_ten_year.calc_cumulative_return()

### Visualize the 10-year Monte Carlo simulation by creating an
### overlay line plot
MC_ten_year.plot_simulation()

### Visualize the probability distribution of the 10-year Monte Carlo simulation 
### by plotting a histogram
MC_ten_year.plot_distribution()

### Visualize the probability distribution of the 10-year Monte Carlo simulation 
### by plotting a histogram
MC_ten_year.plot_distribution()

* Other helpful interactive visualizations
4.) Format into visually appealing way
5.) CLI (see --> 7_Mod/Lesson/01_A_CRUD-Based_CLI_Application/Solved/a_crud_based_cli_application.py)

## Project Conculusions and Summary of the analysis

* Historical performance
* Top 3 portfolio picks (e.g. volatility, covariance with SNP, etc.)
### Based on the analysis and visualization of the Sharpe Ratio, we would recommend CBRE, ESS, and AVB as investment options. 

### From the historical stock analysis performance at first CBRE seem a good investment option but the volatility and risk are a bit higher and more recently the stock price was decreased compared to 2021.

* Investment opportunities
### We would recommend AVB is the most suitable stock for future investment opportunities. 

## Project Next Steps
* Washington housing market prediction
* Seattle housing market price compare to King Country housing market price.

---
## Contributors

* Maureen Kaaria

Email: maureenkaaria@gmail.com
* Khaing Thwe

Email: khaingzt88@gmail.com
* Olga Koryachek

Email: olgakoryachek@live.com

[LinkedIn](https://www.linkedin.com/in/olga-koryachek-a74b1877/?msgOverlay=true "LinkedIn")
* Arthur Lovett

Email: arthur@arthurlovett.com

---

## License

Licensed under the [MIT License](https://choosealicense.com/licenses/mit/)

