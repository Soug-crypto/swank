import streamlit as st
import pandas as pd
import numpy as np
import requests
import folium
from streamlit_folium import st_folium
from ortools.constraint_solver import pywrapcp

# Constants
TRUCK_CAPACITY = 12  # in cubic meters
API_KEY = "5b3ce3597851110001cf624811c647a74e25475a956a0721face67d3" 
GEOCODING_API_URL = "https://nominatim.openstreetmap.org/search"
ROUTING_API_URL = "https://api.openrouteservice.org/v2/directions/driving-car"

# Sample customer data
customer_data = {
    'Name': ['Customer A', 'Customer B', 'Customer C', 'Customer D'],
    'Address': ['Address 1', 'Address 2', 'Address 3', 'Address 4'],
    'Volume': [3, 1.5, 5, 2],  # in cubic meters
    'Preferred Time': ['Morning', 'Afternoon', 'Evening', 'Flexible'],
    'Location': [(32.8872, 13.1913), (32.8874, 13.1920), (32.8876, 13.1925), (32.8880, 13.1930)]  # Example locations
}
customers_df = pd.DataFrame(customer_data)

# Streamlit App Title
st.title("Furniture Delivery Management System")

# Section: Add New Customer Order
st.header("Add New Customer Order")
customer_name = st.text_input("Customer Name")
customer_address = st.text_input("Customer Address")
customer_volume = st.number_input(
    "Volume (cubic meters)", 
    min_value=0.1, 
    max_value=float(TRUCK_CAPACITY), 
)
preferred_time = st.selectbox("Preferred Delivery Time", ['Morning', 'Afternoon', 'Evening', 'Flexible'])

@st.cache_data
def geocode_address(address):
    try:
        response = requests.get(
            GEOCODING_API_URL,
            params={"q": address, "format": "json", "limit": 1},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
        st.warning(f"No results found for: {address}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error with geocoding service: {e}")
    return None

if st.button("Add Order"):
    coordinates = geocode_address(customer_address)
    if coordinates:
        new_order = {
            'Name': customer_name,
            'Address': customer_address,
            'Volume': customer_volume,
            'Preferred Time': preferred_time,
            'Location': coordinates
        }
        customers_df = pd.concat([customers_df, pd.DataFrame([new_order])], ignore_index=True)
        st.success(f"Order added for {customer_name}!")
    else:
        st.error("Unable to fetch coordinates for the address. Please check the address.")

# Section: Current Orders
st.header("Current Orders")
st.dataframe(customers_df)

def calculate_distance(loc1, loc2):
    try:
        response = requests.post(
            ROUTING_API_URL,
            headers={"Authorization": API_KEY},
            json={"coordinates": [[loc1[1], loc1[0]], [loc2[1], loc2[0]]]},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return data["routes"][0]["summary"]["distance"] / 1000  # Distance in km
    except requests.exceptions.RequestException as e:
        st.error(f"Distance calculation failed: {e}")
        return float('inf')  # Return a high value if distance cannot be calculated

def validate_truck_capacity(df):
    total_volume = df['Volume'].sum()
    if total_volume > TRUCK_CAPACITY:
        st.warning("The total volume exceeds the truck's capacity!")
        return False
    return True

def solve_tsp(locations):
    num_locations = len(locations)
    distance_matrix = np.zeros((num_locations, num_locations))

    for i in range(num_locations):
        for j in range(num_locations):
            if i != j:
                distance_matrix[i][j] = calculate_distance(locations[i], locations[j])

    manager = pywrapcp.RoutingIndexManager(num_locations, 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        return distance_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()

    search_parameters.first_solution_strategy = 1  # PATH_CHEAPEST_ARC

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        route = []
        index = routing.Start(0)
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        return route
    return None

def visualize_route(map_, locations, route_indices):
    for i in range(len(route_indices) - 1):
        loc1 = locations[route_indices[i]]
        loc2 = locations[route_indices[i + 1]]
        folium.PolyLine(
            [(loc1[0], loc1[1]), (loc2[0], loc2[1])],
            color="blue",
            weight=2.5,
            opacity=1
        ).add_to(map_)
    return map_

# Section: Optimize Routes
if st.button("Optimize Routes"):
    if not customers_df.empty and validate_truck_capacity(customers_df):
        locations = list(customers_df['Location'])
        optimized_route_indices = solve_tsp(locations)

        if optimized_route_indices:
            st.header("Optimized Route")
            map_ = folium.Map(location=[locations[0][0], locations[0][1]], zoom_start=12)
            route_details = []

            for i in optimized_route_indices:
                customer = customers_df.iloc[i]
                route_details.append(f"{customer['Name']} at {customer['Address']} (Volume: {customer['Volume']} m³)")
                folium.Marker(customer['Location'], popup=f"{customer['Name']}").add_to(map_)

            map_ = visualize_route(map_, locations, optimized_route_indices)
            st.write(route_details)
            st_folium(map_, width=700, height=500)
        else:
            st.warning("No valid route found.")
    else:
        st.warning("No orders to optimize or capacity exceeded!")

# Footer Notes
st.markdown("---")
# st.write("### Notes:")
# st.write("1. Ensure customer availability during preferred delivery time.")
# st.write("2. Use traffic data for real-time adjustments.")

