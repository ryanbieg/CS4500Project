from django.urls import reverse
from django.db.models import indexes
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.template import loader
from django.views import generic
from django.conf import settings
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
import json
from . import serializers
from .models import *
from django.templatetags.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from opensky_api import OpenSkyApi
import requests
from django.http import QueryDict
import base64

'''
General Views
'''
class FlightList(generic.ListView):
    model = Flight

class FlightDetail(generic.DetailView):

    model = Flight
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)   

        flight_instance = FlightList()
        flight_list = flight_instance.get_queryset()

        context['flight_list'] = flight_list

        return context
    
#recomends flights based on those in the database
def recommend(request):
  response = serializers.FlightListView.get(request)
  binary = response.content
  data = json.loads((binary).decode())
  return render(request, 'flightcomparison/recommend.html', {'flights': data['data']})

# flight search blank, before entering anything into search
def flight_search(request):
    static_url = static('data/airport-codes.csv')
    return render(request, 'flightcomparison/flight_search_blank.html', {'static_url': static_url})

# flight search data, once the user enters data into search form
def flight_search_data(request):
    #for comparison, when asking to compare specific flights, redirects to comparison page
    if request.method == 'POST':
        selected_flight_ids = request.POST.getlist('flights[]')
        sort = request.POST.get('sortoption', '')
        return redirect('compare/list', flight_ids=','.join(selected_flight_ids), sort=sort)
    #loads all data based on user input from search (normal search data)
    static_url = static('data/airport-codes.csv')
    departure_location = request.GET.get('departure_location', '')
    arrival_location = request.GET.get('arrival_location', '')
    departure_time = request.GET.get('departure_time', '')
    price = request.GET.get('price', '')
    sort = request.GET.get('sortoption', '')

    #for query response data
    data = ["","","","",""]

    flights = Flight.objects.all()
    if departure_location:
        flights = flights.filter(departure_location__icontains=departure_location[7:])
        data[0] = departure_location
    if arrival_location:
        flights = flights.filter(arrival_location__icontains=arrival_location[7:])
        data[1] = arrival_location
    if departure_time:
        flights = flights.filter(departure_time=departure_time)
        data[2] = departure_time
    if price:
        flights = flights.filter(price=price)
        data[3] = price
    
    #sorts based on selected
    data[4] = sort
    if sort == 'price':
        flights = sorted(flights, key=lambda x: x.price)
    elif sort == 'earlydepart':
        flights = sorted(flights, key=lambda x: x.departure_time)
    elif sort == 'latestdepart':
        flights = sorted(flights, key=lambda x: x.departure_time, reverse=True)
    elif sort == 'earlyarrival':
        flights = sorted(flights, key=lambda x: x.arrival_time)
    else:
        flights = sorted(flights, key=lambda x: x.arrival_time, reverse=True)

    return render(request, 'flightcomparison/flight_search_data.html', {'query_data': data, 'flights': flights, 'static_url': static_url})

# runs comparison for specific flights
def compare(request, flight_ids, sort):
    # list view
    flight_ids = flight_ids
    selected_flights = [int(x) for x in flight_ids.split(',')]
    selected_flights = Flight.objects.filter(id__in=selected_flights)    
    if sort == 'earlydepart':
        selected_flights = selected_flights.order_by('departure_time')
    elif sort == 'latestdepart':
        selected_flights = selected_flights.order_by('-departure_time')
    elif sort == 'earlyarrival':
        selected_flights = selected_flights.order_by('arrival_time')
    elif sort == 'latestarrival':
        selected_flights = selected_flights.order_by('-arrival_time')
    elif sort == 'price':
        selected_flights = selected_flights.order_by('price')  
    # dictionaries for map view
    flights_dict = json.dumps(Flight.get_all_flights_data(), cls=DjangoJSONEncoder)
    return render(request, 'flightcomparison/flight_compare.html', {'flights': selected_flights, 'flight_ids':flight_ids, 'flights_dict':flights_dict, 'sort': sort})

def api_calls(request):
    if request.method == 'GET':
        try:
            return render(request, 'flightcomparison/api_calls.html')
        except Exception as e:
            return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'error': 'Invalid request method'})

@csrf_exempt
def arrivals_by_airport_api(request):
    if request.method == 'POST':
        url = "https://opensky-network.org/api/flights/arrival?airport={airport}&begin={begin}&end={end}"
        data = json.loads(request.body)
        query_params = QueryDict('', mutable=True)
        query_params.update(data)
        url_with_params = url.format(**query_params)
        request_headers = dict(request.headers)
        try:
            response = requests.get(url_with_params, headers=request_headers)
            response.raise_for_status()
            return JsonResponse(response.json())
        except requests.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
@csrf_exempt
def fetch_states_api(request):
    if request.method == 'POST':
        url = "https://opensky-network.org/api/states/all"
        data = {}
        url_with_params = url
        request_headers = dict(request.headers)
        try:
            response = requests.get(url_with_params, headers=request_headers)
            response.raise_for_status()
            return JsonResponse(response.json())
        except requests.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
@csrf_exempt
def get_own_states_api(request):
    if request.method == 'POST':
        username = 'USERNAME'
        password = 'PASSWORD'
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode('utf-8')

        url = "https://opensky-network.org/api/states/own"
        request_headers = {
            'Authorization': f'Basic {credentials}'
        }
        try:
            response = requests.get(url, headers=request_headers)
            response.raise_for_status()
            return JsonResponse(response.json())
        except requests.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
@csrf_exempt
def get_departures_by_airport_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        airport = data.get('airport')
        begin = data.get('begin')
        end = data.get('end')

        username = 'USERNAME'
        password = 'PASSWORD'
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode('utf-8')
        url = f"https://opensky-network.org/api/flights/arrival?airport={airport}&begin={begin}&end={end}"
        request_headers = {
            'Authorization': f'Basic {credentials}'
        }
        try:
            response = requests.get(url, headers=request_headers)
            response.raise_for_status()
            return JsonResponse(response.json())
        except requests.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
@csrf_exempt
def get_flights_in_time_interval_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            begin = data.get('begin')
            end = data.get('end')

            username = 'USERNAME'
            password = 'PASSWORD'
            credentials = base64.b64encode(f"{username}:{password}".encode()).decode('utf-8')

            url = f"https://opensky-network.org/api/flights/all?begin={begin}&end={end}"
            request_headers = {
                'Authorization': f'Basic {credentials}'
            }

            response = requests.get(url, headers=request_headers)
            response.raise_for_status()
            return JsonResponse(response.json())
        except requests.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)