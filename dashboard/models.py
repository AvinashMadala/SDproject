from django.db import models
import pandas as pd
import os

# Create your models here.
def fetch_covid_data():
    directory = os.path.abspath(os.path.dirname(__file__))
    data_path = os.path.join(directory,'static', 'data', 'covid_19_data.csv')
    df = pd.read_csv(data_path)
    return df

def fetch_age_data():
    directory = os.path.abspath(os.path.dirname(__file__))
    data_path = os.path.join(directory,'static', 'data', 'covid19_patients_data.csv')
    df = pd.read_csv(data_path)
    return df

def confirmed_timeseries_data():
    directory = os.path.abspath(os.path.dirname(__file__))
    data_path = os.path.join(directory, 'static', 'data', 'data_modal', 'time_series_covid_19_confirmed.csv')
    df = pd.read_csv(data_path)
    return df

def deaths_timeseries_data():
    directory = os.path.abspath(os.path.dirname(__file__))
    data_path = os.path.join(directory, 'static', 'data', 'data_modal', 'time_series_covid_19_deaths.csv')
    df = pd.read_csv(data_path)
    return df

def recovered_timeseries_data():
    directory = os.path.abspath(os.path.dirname(__file__))
    data_path = os.path.join(directory, 'static', 'data', 'data_modal', 'time_series_covid_19_recovered.csv')
    df = pd.read_csv(data_path)
    return df

