from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
import os
import json
import csv
import numpy as np
import random
from io import BytesIO
import base64
from datetime import datetime
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import dask.dataframe as dd
import dask.array as da
from sklearn.metrics import r2_score
from fbprophet import Prophet
from fbprophet.plot import add_changepoints_to_plot
# import data models
from dashboard.models import fetch_age_data
from dashboard.models import fetch_covid_data
import dashboard.models as model

# Create your views here.
def home(request):
    return render(request, 'main_page/index.html')


def example(request):
    return HttpResponse(' <h1> home page </h1> ')

def get_data(request):

    df = fetch_covid_data()
    df = df.rename(columns={'Province/State': 'province', 'Country/Region': 'country', 'Last Update': 'updated_date'})
    df = df.drop(['SNo', 'ObservationDate'], axis=1)
    # get countries cases count
    agg_by_country = df.groupby(['country']).agg({'Confirmed': 'sum', 'Deaths': 'sum', 'Recovered': 'sum'}).sort_values(by='Confirmed', ascending=False)
    agg_by_country = agg_by_country.reset_index()
    # get cases count by each month
    df['updated_date'] = pd.to_datetime(df['updated_date'])
    df['month'] = df['updated_date'].dt.month_name().str.slice(stop=3).str.lower()
    agg_by_month = df.groupby(['month']).agg({'Confirmed': 'sum', 'Deaths': 'sum', 'Recovered': 'sum'}).sort_values(by='month', ascending=True)
    # sort data as per months
    months_data = pd.DataFrame([['jan', 1], ['feb', 2], ['mar', 3], ['apr', 4], ['may', 5], ['jun', 6], ['jul', 7], ['aug', 8], ['sep', 9], ['oct', 10], ['nov', 11], ['dec', 12]], columns=['month', 'month_int'])
    agg_by_month = pd.merge(agg_by_month, months_data, on=['month'], how='left')
    agg_by_month = agg_by_month.sort_values(by='month_int')

    # get cases average by each day
    df['updated_date'] = df['updated_date'].dt.date
    daily_avg = df.groupby(['updated_date']).agg({'Confirmed': 'mean', 'Deaths': 'mean', 'Recovered': 'mean'}).sort_values(by='updated_date', ascending=True)
    # get daily average cases count
    avg_confirmed = daily_avg['Confirmed'].mean()

    # get statistics about current cases
    total_confirmed = df['Confirmed'].sum()
    total_deaths = df['Deaths'].sum()
    total_recovered = df['Recovered'].sum()
    active = total_confirmed - (total_deaths + total_recovered)
    # convert data into dict format for easy rendering
    stats = {
            'total_confirmed': total_confirmed,
            'total_deaths': total_deaths,
            'total_recovered': total_recovered,
            'active': active,
            'daily_avg': avg_confirmed
        }

    data = {
        'stats': json.dumps(stats),
        'country_aggs': agg_by_country.to_json(orient='records'),
        'month_aggs': agg_by_month.to_json(orient='records')
    }
    return JsonResponse(data)

def download_data(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="covid-dashboard-data.csv"'

    df = fetch_covid_data()
    df = df.rename(columns={'Province/State': 'province', 'Country/Region': 'country', 'Last Update': 'updated_date'})
    df = df.drop(['SNo', 'ObservationDate'], axis=1)
    df['updated_date'] = pd.to_datetime(df['updated_date'])

    df.to_csv(path_or_buf=response,sep=',',float_format='%.2f',index=False)

    return response


def get_age_data(request):

    df = fetch_age_data()
    # filter only necessary columns needed
    df = df[['ID', 'age', 'sex', 'country', 'date_confirmation']]
    list_sample = df['age'][~df['age'].isna()]
    list_sample = list_sample.unique()
    df['age'] = df['age'].apply(lambda x: random.choice(list_sample) if (x is None or str(x) == 'nan') else x)
    df['age'] = df['age'].apply(lambda x: (int(x.split('-')[0]) + int(x.split('-')[1])) / 2 if '-' in x else x)
    df['age'] = df['age'].astype(float)
    # Find Age groups as per age
    df['age_group'] = ''
    df['age_group'] = df['age'].apply(lambda x: get_age_group(x))
    # create a column "ID" with unique numbers
    df['ID'] = np.arange(len(df))
    # Apply group by for age groups & calculate counts
    result = df.groupby(by=['age_group']).count()[['ID']]
    result = result.rename(columns={'ID': 'count'})
    # calculate percentages
    total = result['count'].sum()
    result['percentage'] = result['count'] / total * 100
    result = result.reset_index()

    group_order = pd.DataFrame([['< 5', 1], ['5 - 20', 2], ['20 - 40', 3], ['40 - 60', 4], ['> 60', 5]], columns=['age_group', 'group_order'])
    result = pd.merge(result, group_order, on=['age_group'], how='left')
    result = result.sort_values(by='group_order')
    result = result[['age_group', 'percentage']]
    result = result.round({'percentage': 2})

    # return result as JSON format
    data = {
        'data': result.to_json(orient='records')
    }
    return JsonResponse(data)


def get_age_group(x):
    if( x <= 5):
        return '< 5'
    elif ( x <= 20):
        return '5 - 20'
    elif (x <= 40):
        return '20 - 40'
    elif (x <= 60):
        return '40 - 60'
    elif ( x > 60):
        return '> 60'


def get_analytics(request):
    confirmed_df = model.confirmed_timeseries_data()
    deaths_df = model.deaths_timeseries_data()
    recovered_df = model.recovered_timeseries_data()

    dates = confirmed_df.columns[4:]
    confirmed_df_long = confirmed_df.melt(
        id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'],
        value_vars=dates,
        var_name='Date',
        value_name='Confirmed'
    )
    deaths_df_long = deaths_df.melt(
        id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'],
        value_vars=dates,
        var_name='Date',
        value_name='Deaths'
    )
    recovered_df_long = recovered_df.melt(
        id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'],
        value_vars=dates,
        var_name='Date',
        value_name='Recovered'
    )
    recovered_df_long = recovered_df_long[recovered_df_long['Country/Region'] != 'Canada']
    # Merging confirmed_df_long and deaths_df_long
    full_table = confirmed_df_long.merge(
    right=deaths_df_long,
    how='left',
    on=['Province/State', 'Country/Region', 'Date', 'Lat', 'Long']
    )
    # Merging full_table and recovered_df_long
    full_table = full_table.merge(
            right=recovered_df_long,
            how='left',
            on=['Province/State', 'Country/Region', 'Date', 'Lat', 'Long']
        )
    template_data = { }
    data=full_table
    data['CurrentCases'] = data['Confirmed'] - data['Recovered'] - data['Deaths']
    date_df = data.groupby('Date')[['Confirmed', 'Recovered', 'Deaths', 'CurrentCases']].sum()

    # ------------------------------------------------------------------------------
    # running fb prophet
    global_cases = date_df.reset_index()
    conf_df=global_cases[['Date','Confirmed']]
    rec_df=global_cases[['Date','Recovered']]
    death_df=global_cases[['Date','Deaths']]
    current_df = global_cases[['Date', 'CurrentCases']]

    conf_df=rename_func(conf_df)
    rec_df=rename_func(rec_df)
    death_df=rename_func(death_df)
    current_df=rename_func(current_df)

    fig, fig_2 = create_model(conf_df)
    figure_1 = get_bytes_from_img(fig)
    figure_2 = get_bytes_from_img(fig_2)

    template_data['confirmed_img'] = figure_1
    template_data['confirmed_img_history'] = figure_2
    template_data['max_date'] = datetime.strptime( max(conf_df.ds),  "%m/%d/%y").strftime("%d %B, %Y")

    fig, fig_2 = create_model(death_df)
    figure_1 = get_bytes_from_img(fig)
    figure_2 = get_bytes_from_img(fig_2)

    template_data['death_img'] = figure_1
    template_data['death_img_history'] = figure_2


    fig, fig_2 = create_model(rec_df)
    figure_1 = get_bytes_from_img(fig)
    figure_2 = get_bytes_from_img(fig_2)

    template_data['recovered_img'] = figure_1
    template_data['recovered_img_history'] = figure_2



    # changes = add_changepoints_to_plot(fig.gca(), model, predictions)
    # figure

    # ---------- recovered -------------
    # model1 = Prophet()
    # model1.add_seasonality(name='Monthly', period=30.42, fourier_order=5)
    # recovered_train, recovered_test, divisor = train_test_split(rec_df, 70)
    # model1.fit(recovered_train)
    # rfuture_dates = model1.make_future_dataframe(periods=40)
    # rpredictions = model1.predict(rfuture_dates)
    # model1.plot(rpredictions)
    # model1.plot_components(rpredictions)
    # fig=model1.plot(rpredictions)
    # changes=add_changepoints_to_plot(fig.gca(),model1,rpredictions)

    # ---------- deaths -------------
    # model2 = Prophet()
    # model2.add_seasonality(name='Monthly', period=30.42, fourier_order=5)
    # deaths_train, deaths_test, divisor = train_test_split(death_df, 70)
    # model2.fit(deaths_train)
    # dfuture_dates = model2.make_future_dataframe(periods=40)
    # dpredictions = model2.predict(dfuture_dates)
    # model2.plot(dpredictions)
    # model2.plot_components(dpredictions)
    # fig=model2.plot(dpredictions)
    # changes=add_changepoints_to_plot(fig.gca(),model2,dpredictions)


    _html = loader.render_to_string(
        'main_page/analytics-template.html',
        template_data
    )

    output = {
        'html': _html
    }
    return JsonResponse(output)

def get_bytes_from_img(fig):
    buffer = BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    return graphic

def rename_func(dataframe):
  cols=dataframe.columns
  dataframe=dataframe.rename(columns={cols[0]:'ds',cols[1]:'y'})
  return dataframe

def train_test_split(dataframe,ratio):
  divisor=round((ratio/100)*dataframe.shape[0])
  train=dataframe.iloc[:divisor]
  test=dataframe.iloc[divisor:]
  return train,test,divisor

def create_model(data):
    modelx = Prophet()
    modelx.add_seasonality(name='Monthly', period=30.42, fourier_order=5)
    data_train, data_test, divisor = train_test_split(data, 70)
    modelx.fit(data_train)
    future_dates = modelx.make_future_dataframe(periods=35)
    predictions = modelx.predict(future_dates)
    modelx.plot(predictions)
    modelx.plot_components(predictions)

    sns.set()

    fig = modelx.plot(predictions)
    ax = fig.get_axes()
    ax[0].set_xlabel('Date')
    ax[0].set_ylabel('No. of Cases')

    fig_2 = modelx.plot_components(predictions)
    ax = fig_2.get_axes()
    ax[0].set_xlabel('Date')
    ax[2].set_xlabel('Date')


    return fig, fig_2
