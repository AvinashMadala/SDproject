from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home-page"),
    path('data/all_data/', views.get_data, name="all_data"),
    path('data/get_age_data/', views.get_age_data, name="get_age_data"),
    path('data/download_data/', views.download_data, name="download_data"),
    path('get_analytics/', views.get_analytics, name="get_analytics")
]
