import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json
import requests

# URL of the backend API endpoint
DATA_URL = 'https://www.bestofworlds.se/vacationlocation/vacation_data.php'

# Load existing data from the webserver
def load_data():
    response = requests.get(DATA_URL)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to load data. HTTP status code: {response.status_code}")
        return []

# Save new data to the webserver
def save_data(new_data):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(DATA_URL, json=new_data, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to save data. HTTP status code: {response.status_code}")
    else:
        st.success("Data saved successfully!")

# Convert location dictionary to tuple
def dict_to_tuple(location_dict):
    return (location_dict['lat'], location_dict['lng'])

# Add logo to the upper right corner
logo = '''
<div style="text-align: right;">
<img src="https://bestofworlds.se/img/BoWlogo.png" width="150px">
</div>
'''
st.markdown(logo, unsafe_allow_html=True)

# App title and description
st.title("Summer Vacation Destination Map")
st.markdown("""
    Welcome to the Summer Vacation Destination Map! 🌍✨
    Please click on the map to select your destination and enter your mode of travel.
    Your input will help us create an aggregated map of vacation destinations and travel modes.
""")

# Create columns for layout
col1, col2 = st.columns([2, 1])

# Initialize map
m = folium.Map(location=[20, 0], zoom_start=2, tiles='OpenStreetMap')

# Function to add existing data to the map
def add_data_to_map(map_obj, data):
    for entry in data:
        if 'destination' in entry and 'travel_mode' in entry:
            destination = dict_to_tuple(entry['destination'])
            folium.Marker(
                location=destination,
                popup=f"Destination ({entry['travel_mode']})",
                icon=folium.Icon(icon='info-sign')
            ).add_to(map_obj)

# Load and display existing data
data = load_data()
add_data_to_map(m, data)

with col1:
    map_container = st.container()
    with map_container:
        # Display map and capture clicks
        map_data = st_folium(m, width=700, height=500, key="initial_map")

        # Handle map clicks
        if map_data and 'last_clicked' in map_data and map_data['last_clicked']:
            st.session_state.clicked_point = map_data['last_clicked']
            st.write("Destination Selected:", st.session_state.clicked_point)

            # Input form under the map
            form_container = st.container()
            with form_container:
                with st.form(key='travel_form'):
                    travel_mode = st.selectbox("Select your mode of travel:", ["Flight", "Car", "Bike", "Other"])
                    submit_button = st.form_submit_button(label='Submit')

                if submit_button and st.session_state.clicked_point:
                    destination = st.session_state.clicked_point
                    new_entry = {"destination": destination, "travel_mode": travel_mode}
                    save_data(new_entry)
                    
                    st.session_state.clicked_point = None  # Clear point after submission

                    # Re-render the map with the new marker
                    m = folium.Map(location=[20, 0], zoom_start=2, tiles='OpenStreetMap')
                    data = load_data()
                    add_data_to_map(m, data)
                    st_folium(m, width=700, height=500, key="updated_map")  # Re-render map with updated data

with col2:
    # Display travel mode counts
    st.header("Travel Mode Counts")
    data = load_data()
    df = pd.DataFrame(data)
    if not df.empty:
        travel_mode_counts = df['travel_mode'].value_counts().reset_index()
        travel_mode_counts.columns = ['Travel Mode', 'Count']
        st.bar_chart(travel_mode_counts.set_index('Travel Mode'))
    else:
        st.write("No data available.")

# Additional styling
st.markdown("""
<style>
    .css-1d391kg {
        background: linear-gradient(135deg, #c3ec52 10%, #0ba29d 100%);
    }
    .css-145kmo2 {
        color: white;
    }
</style>
""", unsafe_allow_html=True)
