from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Flight, FlightData
from .views import FlightDetail
from .serializers import FlightListView
import unittest
import requests
from unittest.mock import patch, MagicMock
from base64 import b64encode
import json
from django.test import Client
from django.http import JsonResponse


class FlightModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        Flight.objects.create(
            user=self.user,
            departure_location="City A",
            arrival_location="City B",
            departure_time=timezone.now(),
            departure_location_latitude = 1,
            departure_location_longitude = 1,
            layover_location = "City C",
            layover_location_latitude = 1,
            layover_location_longitude = 1,
            arrival_location_latitude = 1,
            arrival_location_longitude = 1,
            arrival_time=timezone.now(),
            price=100,
            seat_number=1
        )

    def test_flight_creation(self):
        # Tests the creation of a Flight instance and verifies attributes.
        flight = Flight.objects.all()
        flight = flight[0]
        self.assertEqual(flight.departure_location, "City A")
        self.assertEqual(flight.arrival_location, "City B")
        # Tests the __str__ method returns expected string format.
        self.assertEqual(flight.__str__(), 'testuser: City A to City B')

    def test_FlightData_creation(self):
        flight = FlightData.objects.create(
            icao24 = "CODE",
            firstSeen = 1234,
            estDepartureAirport = "KDEN",
            lastSeen = 1,
            estArrivalAirport = "KGRB",
            callsign = "SIGN",

            estDepartureAirportHorizDistance = 1,
            estDepartureAirportVertDistance = 1,
            estArrivalAirportHorizDistance = 1,
            estArrivalAirportVertDistance = 1,
            departureAirportCandidatesCount = 1,
            arrivalAirportCandidatesCount = 1
        )

        #asserting the important data is correct
        self.assertEqual(flight.estDepartureAirport, "KDEN")
        self.assertEqual(flight.estArrivalAirport, "KGRB")
        self.assertEqual(flight.firstSeen, 1234)

        #testing functions related to model
        self.assertEqual(flight.__str__(), "CODE: KDEN KGRB")
'''
Tests for generic view FlightDetail
'''
class GenericViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.flight = Flight.objects.create(
            user=self.user,
            departure_location="City A",
            arrival_location="City B",
            departure_time=timezone.now(),
            departure_location_latitude = 1,
            departure_location_longitude = 1,
            layover_location = "City C",
            layover_location_latitude = 1,
            layover_location_longitude = 1,
            arrival_location_latitude = 1,
            arrival_location_longitude = 1,
            arrival_time=timezone.now(),
            price=100,
            seat_number=1
        )

    def test_get_context_data(self):
        view = FlightDetail()
        view.object = self.flight

        data = view.get_context_data()

        self.assertIn('flight_list', data)
        self.assertIn(self.flight, data['flight_list'])


class UserInterfaceTests(TestCase):
    '''
    Home View
    '''
    def test_recommend_view_status_code(self):
        # Tests that the home view returns a 200 status code.
        url = reverse('recommend')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_recommend_view_uses_correct_template(self):
        # Tests that the home view uses the correct template.
        url = reverse('recommend')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'flightcomparison/recommend.html')
    '''
    Flight_Search view
    '''
    def test_flight_search_status_code(self):
        #tests that the flight_search page returns a 200 status code
        url = reverse('flight_search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_flight_search_correct_template(self):
        #tests that the blank template was used
        url = reverse('flight_search')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'flightcomparison/flight_search_blank.html')

    def test_flight_search_post_status_code(self):
        #tests that the post code works
        url = reverse('flight_search')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

    '''
    Flight_Compare View
    '''
    def test_flight_compare_get_status_code(self):
        #tests that the flight compare status code is correct
        url = reverse('compare/list', kwargs={'flight_ids':1111, 'sort': 'price'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_flight_compare_correct_template(self):
        #tests to make sure the flight_compare template is being used
        url = reverse('compare/list', kwargs={'flight_ids':1111, 'sort': 'earlydepart'})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'flightcomparison/flight_compare.html')

    def test_flight_compare_list_view(self):
        url = reverse('compare/list', kwargs={'flight_ids':1111, 'sort': 'latestdepart'})
        response = self.client.get(url)
        self.assertContains(response, "Flight")
        self.assertContains(response, "Departure Location")
        self.assertContains(response, "Arrival Location")
    
    def test_flight_compare_map_view(self):
        url = reverse('compare/map', kwargs={'flight_ids':1111, 'sort': 'earlyarrival'})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'flightcomparison/flight_compare.html')

    def test_flight_compare_late_arrival_sort(self):
        url = reverse('compare/list', kwargs={'flight_ids':1111, 'sort': 'latestarrival'})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'flightcomparison/flight_compare.html')

'''
Tests Flight Search 
'''
class FlightSearchTests(TestCase):
    def setUp(self):
        # Creates a Flight instance for testing the search functionality.
        self.user = User.objects.create_user(username='testuser', password='12345')
        Flight.objects.create(
            user=self.user,
            departure_location="City A",
            arrival_location="City B",
            departure_location_latitude = 1,
            departure_location_longitude = 1,
            layover_location = "City C",
            layover_location_latitude = 1,
            layover_location_longitude = 1,
            arrival_location_latitude = 1,
            arrival_location_longitude = 1,
            departure_time=timezone.now(),
            arrival_time=timezone.now(),
            price=100,
            seat_number=1
        )

    def test_flight_search_data(self):
        url = reverse('flight_search_data')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'flightcomparison/flight_search_data.html')
        self.assertEqual(response.status_code, 200)
    
    def test_flight_search_post(self):
        url = reverse('flight_search_data')
        response = self.client.post(url)
        self.assertEqual(response.url, 'compare/list')
        self.assertEqual(response.status_code, 302)

    #Testing different sorting options
    def test_search_by_departure_location(self):
        # Tests flight search functionality filters by departure location.
        response = self.client.get(reverse('flight_search_data'), {'departure_location': 'City A'})
        self.assertContains(response, "City A")
        self.assertNotContains(response, "No flights found.")
    def test_flight_search_sort_price(self):
        url = reverse('flight_search_data')
        response = self.client.get(url, {'departure_location': 'City A', 'arrival_location': 'City B', 'departure_time': timezone.now(), 'arrival_time': timezone.now(), 'price': 100, 'sortoption': 'price'})
        self.assertTemplateUsed(response, 'flightcomparison/flight_search_data.html')
        self.assertEqual(response.status_code, 200)

    def test_flight_search_sort_early_departure(self):
        url = reverse('flight_search_data')
        response = self.client.get(url, {'departure_location': 'City A', 'arrival_location': 'City B', 'departure_time': timezone.now(), 'arrival_time': timezone.now(), 'sortoption': 'earlydepart'})
        self.assertTemplateUsed(response, 'flightcomparison/flight_search_data.html')
        self.assertEqual(response.status_code, 200)

    def test_flight_search_sort_late_departure(self):
        url = reverse('flight_search_data')
        response = self.client.get(url, {'departure_location': 'City A', 'arrival_location': 'City B', 'departure_time': timezone.now(), 'arrival_time': timezone.now(), 'sortoption': 'latestdepart'})
        self.assertTemplateUsed(response, 'flightcomparison/flight_search_data.html')
        self.assertEqual(response.status_code, 200)

    def test_flight_search_sort_early_arrival(self):
        url = reverse('flight_search_data')
        response = self.client.get(url, {'departure_location': 'City A', 'arrival_location': 'City B', 'departure_time': timezone.now(), 'arrival_time': timezone.now(), 'sortoption': 'earlyarrival'})
        self.assertTemplateUsed(response, 'flightcomparison/flight_search_data.html')
        self.assertEqual(response.status_code, 200)
    
    def test_flight_search_sort_late_arrival(self):
        url = reverse('flight_search_data')
        response = self.client.get(url, {'departure_location': 'City A', 'arrival_location': 'City B', 'departure_time': timezone.now(), 'arrival_time': timezone.now(), 'sortoption': 'latestarrival'})
        self.assertTemplateUsed(response, 'flightcomparison/flight_search_data.html')
        self.assertEqual(response.status_code, 200)

class ExceptionTests(TestCase):
    def test_managepy(self):
        with self.assertRaises(ImportError):
            raise ImportError()



class TestAPI(TestCase):
    def setUp(self):
        self.client = Client()

    @patch('requests.get')
    def test_arrivals_by_airport_api(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'arrival_flights': [{'flight_id': '123', 'flight_number': 'ABC123'}]}
        response = self.client.post('/arrivals_by_airport_api', data=json.dumps({'airport': 'JFK', 'begin': '2024-05-01', 'end': '2024-05-02'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'arrival_flights': [{'flight_id': '123', 'flight_number': 'ABC123'}]})

    @patch('requests.get')
    def test_fetch_states_api(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'states': [{'icao24': 'ABC123', 'callsign': 'ABC123'}]}
        response = self.client.post('/fetch_states_api')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content    ), {'states': [{'icao24': 'ABC123', 'callsign': 'ABC123'}]})

    @patch('requests.get')
    def test_get_own_states_api(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'own_states': [{'icao24': 'XYZ789', 'callsign': 'XYZ789'}]}
        response = self.client.post('/get_own_states_api')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'own_states': [{'icao24': 'XYZ789', 'callsign': 'XYZ789'}]})

    @patch('requests.get')
    def test_get_departures_by_airport_api(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'departure_flights': [{'flight_id': '456', 'flight_number': 'DEF456'}]}
        response = self.client.post('/get_departures_by_airport_api', data=json.dumps({'airport': 'LAX', 'begin': '2024-05-01', 'end': '2024-05-02'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'departure_flights': [{'flight_id': '456', 'flight_number': 'DEF456'}]})


    @patch('requests.get')
    def test_get_flights_in_time_interval_api(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'flights_in_interval': [{'flight_id': '789', 'flight_number': 'GHI789'}]}
        
        response = self.client.post('/get_flights_in_time_interval_api',data=json.dumps({'begin': '2024-05-01', 'end': '2024-05-02'}),content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content),{'flights_in_interval': [{'flight_id': '789', 'flight_number': 'GHI789'}]})
    

class CompareViewTestCase(TestCase):
    def setUp(self):
        # Create some Flight objects for testing
        self.user = User.objects.create_user(username='test_user', email='test@example.com', password='password')
        self.flight1 = Flight.objects.create(user=self.user, departure_location='Location 1', departure_location_latitude=40.7128, departure_location_longitude=-74.0060, layover_location='Location 1', layover_location_latitude=40.7128, layover_location_longitude=-74.0060, arrival_location='Location 2', arrival_location_latitude=34.0522, arrival_location_longitude=-118.2437, departure_time='2024-04-25 10:00:00', arrival_time='2024-04-25 12:00:00', price=100, seat_number=50)
        self.flight2 = Flight.objects.create(user=self.user, departure_location='Location 3', departure_location_latitude=37.7749, departure_location_longitude=-122.4194, layover_location='Location 3', layover_location_latitude=37.7749, layover_location_longitude=-122.4194, arrival_location='Location 4', arrival_location_latitude=34.0522, arrival_location_longitude=-118.2437, departure_time='2024-04-25 11:00:00', arrival_time='2024-04-25 13:00:00', price=150, seat_number=60)

    def test_compare_view_latest_depart_sort(self):
        url = reverse('compare/list', args=('1,2', 'latestdepart'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flightcomparison/flight_compare.html')
        # Check if flights are sorted by departure time descending
        self.assertQuerysetEqual(response.context['flights'], [self.flight2, self.flight1])

    def test_compare_view_early_arrival_sort(self):
        url = reverse('compare/list', args=('1,2', 'earlyarrival'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flightcomparison/flight_compare.html')
        # Check if flights are sorted by arrival time ascending
        self.assertQuerysetEqual(response.context['flights'], [self.flight1, self.flight2])

    def test_compare_view_latest_arrival_sort(self):
        url = reverse('compare/list', args=('1,2', 'latestarrival'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flightcomparison/flight_compare.html')
        # Check if flights are sorted by arrival time descending
        self.assertQuerysetEqual(response.context['flights'], [self.flight2, self.flight1])

    def test_compare_view_price_sort(self):
        url = reverse('compare/list', args=('1,2', 'price'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flightcomparison/flight_compare.html')
        # Check if flights are sorted by price ascending
        self.assertQuerysetEqual(response.context['flights'], [self.flight1, self.flight2])
