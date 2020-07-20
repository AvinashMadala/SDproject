from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import pandas as pd
import os
import json
import csv
import numpy as np
import random
from dashboard.models import fetch_age_data
from dashboard.models import fetch_covid_data

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

