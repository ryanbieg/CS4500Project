import csv
import os

'''
Python scripts that I wasnt sure where to put
'''
'''
Script that parses airport CSV file to find matching departure and arrival airport
Inputs: departure, arrival are user generated text for departure location and arrival location
Returns: tuple containing list of possible departure and arrival points, each in their own list with syntax [icao, airport name]
'''
#csv data found at https://github.com/datasets/airport-codes?tab=readme-ov-file
def find_airports(departure, arrival):
    #gets location of current file, helps to reference csv file
    cwd = os.path.dirname(os.path.abspath(__file__))
    possible_departures = []
    possible_arrivals = []
    #opens csv file
    with open(cwd + 'static/data/airport-codes.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        #Rows in airport-codes.csv have this format:
        #ICAO code,type,name,elevation_ft,continent,iso_country,iso_region,municipality,gps_code,iata_code,local_code,coordinates
        for row in reader:
            #parses out all non airports (helipads), and closed airports
            if "airport" in row[1] and 'closed' not in row[1]:
                flight = [row[0], row[2]]
                if departure in flight[1]:
                    possible_departures.append(flight)
                if arrival in flight[1]:
                    possible_arrivals.append(flight)

        return possible_departures, possible_arrivals

#Test for function find_airports
print(find_airports("Denver", "Fort Worth"))