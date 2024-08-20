from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from .models import Flight

'''
Serializer to get all flights for home view
'''
class FlightListView(View):
    def get(request):
        flightList = Flight.objects.all()
        
        data = [
            {
                'id': flight.id,
                'user': flight.user.username,
                'departure_location': flight.departure_location,
                'arrival_location': flight.arrival_location,
                'departure_time': flight.departure_time.strftime("%Y-%m-%d %H:%M:%S"),
                'arrival_time': flight.arrival_time.strftime("%Y-%m-%d %H:%M:%S"),
                'price': flight.price,
                'seat_number': flight.seat_number,
            } for flight in flightList
        ]
        response = {
            'data': data,
        }
        return JsonResponse(response)