#import passiogo

import os
import time

import json
from passiogo_fix import passiogo

from mapTimeGet import drive_time_minutes_along_path
from lineListMakeSelect import kmz_route_points
from bus5stop import find_bus_path









system = passiogo.getSystemFromID(1007)


# All system alerts
#alerts = system.getSystemAlerts()









#GET STOPS
def get_selected_stops(filename="config/nyu_stops.json"):
#get stops marked as true from the stop list json
    with open(filename, "r", encoding="utf-8") as file:
        stop_data = json.load(file)

    selected_stops = []

    for stop_name, enabled in stop_data.items():
        if enabled is True:
            selected_stops.append(stop_name)

    return selected_stops


# CLEAN DATA
def convert_stops(selected_stops, stops):
    # Build lookup dictionary of Passio stop objects by name
    stop_lookup = {stop.name: stop for stop in stops}


    #SANITY CHECK
    missing_stops = [
        name for name in selected_stops
        if name not in stop_lookup
    ]
    if missing_stops:
        raise Exception(
            f"Selected stops not found in Passio: {missing_stops}"
        )



    # Convert selected stop names into Passio stop objects
    return [stop_lookup[name] for name in selected_stops]


#GET ROUTES
def get_matching_routes(selected_stops):
    matching_routes = []

    for route in system.getRoutes():
        route_stops = route.getStops()

        for stop in route_stops:
            if stop.name in selected_stops:   #THE FUNCTION IN QUESTION
                matching_routes.append(route)
                break

    return matching_routes


#GET BUSSES
def get_buses_on_routes(matching_routes, vehicles):
    #get all busses and match to routes
    matching_buses = []
    #keep the indexing across all route refrences in order
    for route in matching_routes:

        routeRn = []

        for bus in vehicles:

            if bus.routeName == route.name:

                routeRn.append(bus)

        matching_buses.append(routeRn)


    #matching busses will be a matching of busses
    #matchin busses will be consist of routes in order of routes
    return matching_buses
    #matching busses will kill you if you let it








#I wonder what this function does...
selected_stops = get_selected_stops()

#got matching routes in order
matching_routes = get_matching_routes(selected_stops)

#got matching busses, in lists in order of the route order, so each list is a route, indexed the same as routes
buses = get_buses_on_routes(matching_routes, system.getVehicles())








script_dir = os.path.dirname(os.path.abspath(__file__))
files = os.listdir(os.path.join(script_dir, "routeMaps"))
#list of lists similar to busses list
routeSPolyLinesWithStops = []
#wait is there a typo ...?
for route in matching_routes:
   #fo route in route band for band 

   matching_files = [file for file in files if file[0] == route.name[-1]]
   if len(matching_files) != 1:
       raise ValueError(
           f"Expected one route map for {route.name}, found {matching_files}"
       )
   file = matching_files[0]

   bigList = kmz_route_points(os.path.join(script_dir, "routeMaps/" + file), selected_stops)
           
   routeSPolyLinesWithStops.append(bigList)
   #appends in same order as last list







#we cleaned our bus data before hand data bus clean hand before bus data clean data bus
#me give orange give orange me give me orange me orange
#a bus to route the organs
routeOrganBus = []
#list of lists, the top list is route, the internal lists are bus lines to the stop
for i in range(len(buses)):
    #buses contains route lists of busses
    route = buses[i]
    line = routeSPolyLinesWithStops[i]

    currBusToRouteLines = []
    #all top level routing is route, hope this helps <3
    for bus in route:
        #jesus christ told me to kill the president of the united states of america
        currBusToRouteLines.append(find_bus_path(float(bus.latitude), float(bus.longitude), float(bus.calculatedCourse), line))

    #keeps route index in tact
    routeOrganBus.append(currBusToRouteLines)








busTimesByRoute = []
#stop inherint to all that is and all that will be
for route in routeOrganBus:

    timesInRoute=[]
    #they call me the spawn a list and then populate it guy, the guy who spawns a list and then populates it, this is because I spawn a list and then populate it
    for bus in route:

        route_points = [
            (point[1], point[0])
            for point in bus
            if isinstance(point, tuple)
        ]

        if len(route_points) < 2:
            continue

        thisBussesTime = drive_time_minutes_along_path(route_points)
        thisBussesTime += bus.count("STOP") * 3
        time.sleep(0.3)

        timesInRoute.append(thisBussesTime)

    busTimesByRoute.append(timesInRoute)
    #ill break into your house, clean it, and shoot you in the head













print(selected_stops)

for i in range(len(busTimesByRoute)):
    currRouteBusTimes = busTimesByRoute[i]
    currRoute = matching_routes[i].name


    print("====================================================================")
    print(currRoute)
    print("--------------------------------------------------------------------")

    for busLine in currRouteBusTimes:
        print(busLine)




