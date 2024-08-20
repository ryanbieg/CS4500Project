from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from . import views

appName = 'flightcomparison' 
urlpatterns = [
    path('', views.flight_search, name='flight_search'), 
    path('recommendations/', views.recommend, name='recommend'), 
    path('flight_search/query/', views.flight_search_data, name='flight_search_data'), 
    path('compare/list/<str:flight_ids>/<str:sort>', views.compare, name="compare/list"),
    path('compare/map/<str:flight_ids>/<str:sort>/', views.compare, name="compare/map"), 
    path('flights/', views.FlightList.as_view(), name='flights'), 
    path('flight/<int:pk>/', views.FlightDetail.as_view(), name='flight_detail'), 
    path('api-calls/', views.api_calls, name='api_calls'),
    path('arrivals_by_airport_api', views.arrivals_by_airport_api, name='arrivals_by_airport_api'),
    path('fetch_states_api', views.fetch_states_api, name="fetch_states_api"),
    path('get_own_states_api', views.get_own_states_api, name='get_own_states_api'),
    path('get_departures_by_airport_api', views.get_departures_by_airport_api, name='get_departures_by_airport_api'),
    path('get_flights_in_time_interval_api', views.get_flights_in_time_interval_api, name='get_flights_in_time_interval_api'),
]