# Practical Machine Learning Approach to Capture the Scholar Data Driven Alpha in AI Industry

AI technologies are helping more and more companies leverage their resources to expand business, reach higher
financial performance and become more valuable for investors.
However, it is difficult to capture and predict the impacts of
AI technologies on companies’ stock prices through traditional
financial factors. Moreover, common information sources such as
company’s earnings calls and news are not enough to quantify
and predict the actual AI premium for a certain company. In
this paper, we utilize scholar data as alternative data for trading
strategy development and propose a practical machine learning
approach to quantify the AI premium of a company and capture
the scholar data driven alpha in the AI industry. First, we collect
the scholar data from the Microsoft Academic Graph database,
and conduct feature engineering based on AI publication and
patent data, such as conference/journal publication counts, patent
counts, fields of studies and paper citations. Second, we apply
machine learning algorithms to weight and re-balance stocks
using the scholar data and traditional financial factors every
month, and construct portfolios using the “buy-and-hold-long
only” strategy. Finally, we evaluate our factor and portfolio in
terms of factor performance and portfolio’s cumulative return.
The proposed scholar data driven approach achieves a cumulative
return of 1029.1% during our backtesting period, which significantly outperforms the Nasdaq 100 index’s 529.5% and S&P
500’s 222.6%. The traditional financial factors approach only
leads to 776.7%, which indicates that our scholar data driven
approach is better at capturing investment alpha in AI industry
than traditional financial factors.

## Reference
Yunzhe Fang, Xiao-Yang Liu, and Hongyang Yang. 2019.   Practical machine learning approach to capture the scholar data driven alpha in AI industry. In2019IEEE International Conference on Big Data (Big Data) Special Session on IntelligentData Mining. 2230–2239
[Our Paper(https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3501239)
## Data

### Alternative Data & Preprocessing

The alternative data we use is from the [Microsoft Academic Graph database](https://www.microsoft.com/en-us/research/project/microsoft-academic-graph/), which is an open resource database with records of publications, including papers, journals, conferences, books etc. It provides the demographics of the publications like public date, citations, authors and affiliated institutes. 

* First, we collect and combine every component stock from several AI related indexes such as Vanguard Information Technology Exchange-Traded Fund (ETF) and Global X Robotics & Artificial Intelligence Thematic ETF [12]. This gives us a basic company pool to select from.
* Then we get a list of companies including companies in non-US markets or do not have publications and patents
* We remove the stocks which are not in the US stock market and only keep the companies that have at least one publication or patent record during our backtesting period 2009-2018
* We obtain our investment universe that contains 115 publicly trade companies.
* Finally, we extracted 40 scholar-data-driven features including conference publications, journal publications, patents or books

### Financial Data

The daily price of stocks we use is pulled from [Compustat database via Wharton Research Data Services](https://wrds-web.wharton.upenn.edu/wrds/ds/compd/fundq).

## Predictive Model

### Ensemble

* Linear Regression
* Lasso Regression
* Ridge Regression
* Random Forest Regression
* Support Vector Regression
* LSTM

### Rolling window backtesting

* Step 1: We train the 6 models based on the same features and monthly returns data concurrently on a 36-month-train rolling window.
* Step 2: We validate all 6 models by using a 6-month validate-rolling window followed by the 36-month-train rolling window. We calculate the MAE of each model.
* Step 3: After validation, we select the best model which has the lowest MAE to predict and trade. So we will have a set of predicted returns for all current stocks. We rank the stocks by the predicted return and only select top 25% stocks with highest predicted returns to form our portfolio. We use LSTM as our trading model 41 times out of 117 backtesting months, as listed in Table II. From the result we can see that LSTM is the best model for our topic. (https://github.com/chenqian0168/Quantifying-ESG-Alpha-in-Scholar-Big-Data-An-Automated-Machine-Learning-Approach/blob/master/pictures/rolling_window.png)

## Performance

* Scholar Alpha: Our proposed scholar data driven approach achieves a cumulative return of 1029.1% during our back-testing period, which significantly outperforms other portfolios.

Below is the rolling annualized Sharpe ratio of ESG alpha vs. Financial indicators only portfolio.
![rolling_sharpe](https://github.com/chenqian0168/Quantifying-ESG-Alpha-in-Scholar-Big-Data-An-Automated-Machine-Learning-Approach/blob/master/pictures/rolling_sharpe.png)

Below shows the logarithmic cumulative return of ESG scholar alpha.
![cummulative_return](https://github.com/chenqian0168/Quantifying-ESG-Alpha-in-Scholar-Big-Data-An-Automated-Machine-Learning-Approach/blob/master/pictures/cumulative_return.png)



This repository refers to the codes for IEEEBigData paper.
