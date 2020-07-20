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