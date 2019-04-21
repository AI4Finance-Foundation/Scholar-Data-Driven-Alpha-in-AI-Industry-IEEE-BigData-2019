import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn.linear_model import Ridge

from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import AdaBoostRegressor

from sklearn.model_selection import TimeSeriesSplit, GridSearchCV,RandomizedSearchCV




def prepare_training_data(df,features_column,unique_datetime,testing_windows,fist_trade_date_index, current_index):
    train=df[(df.date >= unique_datetime[current_index-fist_trade_date_index]) & (df.date < unique_datetime[current_index-testing_windows])]
    X_train=train[features_column]
    y_train=train["monthly_return"]
    return X_train,y_train

def prepare_testing_data(df,features_column,unique_datetime,testing_windows,fist_trade_date_index, current_index):
    test=df[(df.date >= unique_datetime[current_index-testing_windows]) & (df.date < unique_datetime[current_index])]
    X_test=test[features_column]
    y_test=test["monthly_return"]
    return X_test,y_test

def prepare_trade_data(df,features_column,unique_datetime,testing_windows,fist_trade_date_index, current_index):
    trade  = df[df.date == unique_datetime[current_index]]
    X_trade_actual=trade[features_column]
    y_trade_actual=trade["monthly_return"]
    trade_tic = trade['ticker'].values
    return X_trade_actual,y_trade_actual,trade_tic


def train_linear_regression(X_train,y_train):

    lr_regressor = LinearRegression()
    model = lr_regressor.fit(X_train, y_train)
    return model


def train_lasso(X_train, y_train):
    # lasso_regressor = Lasso()
    # model = lasso_regressor.fit(X_train, y_train)

    lasso = Lasso()
    # scoring_method = 'r2'
    # scoring_method = 'explained_variance'
    scoring_method = 'neg_mean_absolute_error'
    # scoring_method = 'neg_mean_squared_error'
    # scoring_method = 'neg_mean_squared_log_error'
    parameters = {'alpha': [1e-15, 1e-10, 1e-8, 1e-4, 1e-3, 1e-2, 1, 5, 10, 20]}
    # my_cv_lasso = TimeSeriesSplit(n_splits=3).split(X_train_advanced)
    lasso_regressor = GridSearchCV(lasso, parameters, scoring=scoring_method, cv=3)
    lasso_regressor.fit(X_train, y_train)

    model = lasso_regressor.best_estimator_
    return model


def train_random_forest(X_train, y_train):
    random_grid = {'bootstrap': [True, False],
                   'max_depth': [10, 20, 40, 80, 100, None],
                   'max_features': ['auto', 'sqrt'],
                   'min_samples_leaf': [1, 2, 5, 10],
                   'min_samples_split': [2, 5, 10],
                   'n_estimators': [200, 400, 600, 800, 1000, 1500]}

    # my_cv_rf = TimeSeriesSplit(n_splits=5).split(X_train_rf)
    rf = RandomForestRegressor(random_state=42)
    randomforest_regressor = RandomizedSearchCV(estimator=rf, param_distributions=random_grid,
                                                cv=3, n_jobs=-1, scoring='neg_mean_absolute_error', verbose=0)
    randomforest_regressor.fit(X_train, y_train)
    model = randomforest_regressor.best_estimator_
    '''
    randomforest_regressor = RandomForestRegressor(random_state = 42,n_estimators = 800)
    model = randomforest_regressor.fit(X_train, y_train)
    '''
    return model


def train_gbm(X_train, y_train):
    gbm = GradientBoostingRegressor(random_state=42)
    # model = gbm.fit(X_train, y_train)

    param_grid_gbm = {'learning_rate': [0.1, 0.05, 0.01, 0.001], 'n_estimators': [100, 250, 500, 1000]}
    # scoring_method = 'r2'
    # scoring_method = 'explained_variance'
    scoring_method = 'neg_mean_absolute_error'
    # scoring_method = 'neg_mean_squared_error'
    # scoring_method = 'neg_mean_squared_log_error'
    gbm_regressor = RandomizedSearchCV(estimator=gbm, param_distributions=param_grid_gbm,
                                       cv=3, n_jobs=-1, scoring=scoring_method, verbose=0)

    gbm_regressor.fit(X_train, y_train)
    model = gbm_regressor.best_estimator_

    return model


def train_ada(X_train, y_train):
    ada = AdaBoostRegressor()

    # model = ada.fit(X_train, y_train)

    param_grid_ada = {'n_estimators': [20, 50, 100],
                      'learning_rate': [0.01, 0.05, 0.1, 0.3, 1]}
    # scoring_method = 'r2'
    # scoring_method = 'explained_variance'
    scoring_method = 'neg_mean_absolute_error'
    # scoring_method = 'neg_mean_squared_error'
    # scoring_method = 'neg_mean_squared_log_error'

    ada_regressor = RandomizedSearchCV(estimator=ada, param_distributions=param_grid_ada,
                                       cv=3, n_jobs=-1, scoring=scoring_method, verbose=0)

    ada_regressor.fit(X_train, y_train)
    model = ada_regressor.best_estimator_

    return model


def evaluate_model(model, X_test, y_test):
    from sklearn.metrics import mean_squared_error
    from sklearn.metrics import mean_absolute_error
    from sklearn.metrics import explained_variance_score
    from sklearn.metrics import r2_score
    y_predict = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_predict)
    mse = mean_squared_error(y_test, y_predict)
    explained_variance = explained_variance_score(y_test, y_predict)
    r2 = r2_score(y_test, y_predict)

    return mae


def append_return_table(df_predict, unique_datetime, y_trade_return, trade_tic, current_index):
    tmp_table = pd.DataFrame(columns=trade_tic)
    tmp_table = tmp_table.append(pd.Series(y_trade_return, index=trade_tic), ignore_index=True)
    df_predict.loc[unique_datetime[current_index]] = tmp_table.loc[0]


def run_model(df, unique_ticker, unique_datetime, trade_month, features_column, first_trade_date_index=42,
              testing_windows=6):
    df_predict_lr = pd.DataFrame(columns=unique_ticker, index=trade_month)
    df_predict_rf = pd.DataFrame(columns=unique_ticker, index=trade_month)
    df_predict_lasso = pd.DataFrame(columns=unique_ticker, index=trade_month)
    df_predict_gbm = pd.DataFrame(columns=unique_ticker, index=trade_month)
    df_predict_ada = pd.DataFrame(columns=unique_ticker, index=trade_month)

    df_predict_best = pd.DataFrame(columns=unique_ticker, index=trade_month)
    df_best_model_name = pd.DataFrame(columns=['model_name'], index=trade_month)
    evaluation_record = []
    # first_trade_date = '2013-07-31'
    # fist_trade_date_index = 42
    # testing_windows = 6

    for i in range(first_trade_date_index, len(unique_datetime)):
        # prepare training data
        X_train, y_train = prepare_training_data(df, features_column, unique_datetime, testing_windows,
                                                 first_trade_date_index, current_index=i)

        # prepare testing data
        X_test, y_test = prepare_testing_data(df, features_column, unique_datetime, testing_windows,
                                              first_trade_date_index, current_index=i)

        # prepare trade data
        X_trade, y_trade, trade_tic = prepare_trade_data(df, features_column, unique_datetime, testing_windows,
                                                         first_trade_date_index, current_index=i)

        # Train
        lr_model = train_linear_regression(X_train, y_train)
        rf_model = train_random_forest(X_train, y_train)
        lasso_model = train_lasso(X_train, y_train)
        gbm_model = train_gbm(X_train, y_train)
        ada_model = train_ada(X_train, y_train)

        # Validation
        lr_eval = evaluate_model(lr_model, X_test, y_test)
        rf_eval = evaluate_model(rf_model, X_test, y_test)
        lasso_eval = evaluate_model(lasso_model, X_test, y_test)
        gbm_eval = evaluate_model(gbm_model, X_test, y_test)
        ada_eval = evaluate_model(ada_model, X_test, y_test)

        # Trade
        y_trade_lr = lr_model.predict(X_trade)
        y_trade_rf = rf_model.predict(X_trade)
        y_trade_lasso = lasso_model.predict(X_trade)
        y_trade_gbm = gbm_model.predict(X_trade)
        y_trade_ada = ada_model.predict(X_trade)

        # Decide the best mode
        eval_data = [[lr_eval, y_trade_lr], [rf_eval, y_trade_rf], [lasso_eval, y_trade_lasso],
                     [gbm_eval, y_trade_gbm], [ada_eval, y_trade_ada]]

        eval_table = pd.DataFrame(eval_data, columns=['model_eval', 'model_predict_return'],
                                  index=['lr', 'rf', 'lasso', 'gbm', 'ada'])
        evaluation_record.append(eval_table)

        # lowest error score model
        y_trade_best = eval_table.model_predict_return.values[eval_table.model_eval == eval_table.model_eval.min()][0]
        best_model_name = eval_table.index.values[eval_table.model_eval == eval_table.model_eval.min()][0]

        # Highest Explained Variance
        # y_trade_best = eval_table.model_predict_return.values[eval_table.model_eval==eval_table.model_eval.max()][0]
        # best_model_name = eval_table.index.values[eval_table.model_eval==eval_table.model_eval.max()][0]

        df_best_model_name.loc[unique_datetime[i]] = best_model_name

        # Prepare Predicted Return table
        append_return_table(df_predict_lr, unique_datetime, y_trade_lr, trade_tic, current_index=i)
        append_return_table(df_predict_rf, unique_datetime, y_trade_rf, trade_tic, current_index=i)
        append_return_table(df_predict_lasso, unique_datetime, y_trade_lasso, trade_tic, current_index=i)
        append_return_table(df_predict_gbm, unique_datetime, y_trade_gbm, trade_tic, current_index=i)
        append_return_table(df_predict_ada, unique_datetime, y_trade_ada, trade_tic, current_index=i)
        append_return_table(df_predict_best, unique_datetime, y_trade_best, trade_tic, current_index=i)
        print('Trade Month: ', unique_datetime[i])

    return (df_predict_lr, df_predict_rf, df_predict_lasso, df_predict_gbm, df_predict_ada, df_predict_best, df_best_model_name, evaluation_record)


def long_only_strategy_daily(df_predict_return, daily_return, trade_month_plus1, top_quantile_threshold=0.7):
    long_dict = {}
    for i in range(df_predict_return.shape[0]):
        top_q = df_predict_return.iloc[i].quantile(top_quantile_threshold)
        # low_q=df_predict_return.iloc[i].quantile(0.2)
        # Select all stocks
        # long_dict[df_predict_return.index[i]] = df_predict_return.iloc[i][~np.isnan(df_predict_return.iloc[i])]
        # Select Top 30% Stocks
        long_dict[df_predict_return.index[i]] = df_predict_return.iloc[i][df_predict_return.iloc[i] >= top_q]
        # short_dict[df_predict_return.index[i]] = df_predict_return.iloc[i][df_predict_return.iloc[i]<=low_q]

    df_portfolio_return_daily = pd.DataFrame(columns=['daily_return'])
    for i in range(len(trade_month_plus1) - 1):
        # for long only
        # calculate weight based on predicted return
        long_normalize_weight = long_dict[trade_month_plus1[i]] / sum(long_dict[trade_month_plus1[i]].values)
        # map date and tic
        long_tic_return_daily = \
        daily_return[(daily_return.index >= trade_month_plus1[i]) & (daily_return.index < trade_month_plus1[i + 1])][
            long_dict[trade_month_plus1[i]].index]
        # return * weight
        long_daily_return = long_tic_return_daily * long_normalize_weight
        df_temp = long_daily_return.sum(axis=1)
        df_temp = pd.DataFrame(df_temp, columns=['daily_return'])
        df_portfolio_return_daily = df_portfolio_return_daily.append(df_temp)

        # for short only
        # short_normalize_weight=short_dict[trade_month[i]]/sum(short_dict[trade_month[i]].values)
        # short_tic_return=tic_monthly_return[tic_monthly_return.index==trade_month[i]][short_dict[trade_month[i]].index]
        # short_return_table=short_tic_return
        # portfolio_return_dic[trade_month[i]] = long_return_table.values.sum() + short_return_table.values.sum()

    return df_portfolio_return_daily


def long_only_strategy_monthly(df_predict_return, tic_monthly_return, trade_month, top_quantile_threshold=0.7):
    long_dict = {}
    short_dict = {}
    for i in range(df_predict_return.shape[0]):
        top_q = df_predict_return.iloc[i].quantile(top_quantile_threshold)
        # low_q=df_predict_return.iloc[i].quantile(0.2)
        # Select all stocks
        # long_dict[df_predict_return.index[i]] = df_predict_return.iloc[i][~np.isnan(df_predict_return.iloc[i])]
        # Select Top 30% Stocks
        long_dict[df_predict_return.index[i]] = df_predict_return.iloc[i][df_predict_return.iloc[i] >= top_q]
        # short_dict[df_predict_return.index[i]] = df_predict_return.iloc[i][df_predict_return.iloc[i]<=low_q]

    portfolio_return_dic = {}
    for i in range(len(trade_month)):
        # for longX_train_rf only
        # calculate weight based on predicted return
        long_normalize_weight = long_dict[trade_month[i]] / sum(long_dict[trade_month[i]].values)
        # map date and tic
        long_tic_return = tic_monthly_return[tic_monthly_return.index == trade_month[i]][
            long_dict[trade_month[i]].index]
        # return * weight
        long_return_table = long_tic_return * long_normalize_weight
        portfolio_return_dic[trade_month[i]] = long_return_table.values.sum()

        # for short only
        # short_normalize_weight=short_dict[trade_month[i]]/sum(short_dict[trade_month[i]].values)
        # short_tic_return=tic_monthly_return[tic_monthly_return.index==trade_month[i]][short_dict[trade_month[i]].index]
        # short_return_table=short_tic_return
        # portfolio_return_dic[trade_month[i]] = long_return_table.values.sum() + short_return_table.values.sum()

    df_portfolio_return = pd.DataFrame.from_dict(portfolio_return_dic, orient='index')
    df_portfolio_return = df_portfolio_return.reset_index()
    df_portfolio_return.columns = ['trade_month', 'monthly_return']
    df_portfolio_return.index = df_portfolio_return.trade_month
    df_portfolio_return = df_portfolio_return['monthly_return']
    return df_portfolio_return















