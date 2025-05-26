import streamlit as st
import pandas as pd
import numpy as np
import folium
import openrouteservice
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from sklearn.cluster import KMeans
from openrouteservice.exceptions import ApiError
from openrouteservice import convert 
import requests
import plotly.express as px

# --- API Keys ---
ORS_API_KEY = "5b3ce3597851110001cf6248a2ea68594e4147b980b57e3165b5df0b"
OWM_API_KEY = "3a16a1814468c62d8d0ed165250597a8"

# --- Setup ---
client = openrouteservice.Client(key=ORS_API_KEY)

# --- File Upload ---
# File Upload
st.title("🗺️ Uber Trip Analysis with Route Optimization and Weather")
uploaded_file = st.file_uploader(r"C:\Users\karan\Downloads\archive (12)\uber-raw-data-janjune-15.csv", type=["csv"])

@st.cache_data(show_spinner=True)
def load_data(file, sample_size=None):
    df = pd.read_csv(file)
    if sample_size and len(df) > sample_size:
        df = df.sample(sample_size, random_state=42).reset_index(drop=True)
    df['Date/Time'] = pd.to_datetime(df['Date/Time'], errors='coerce')
    df = df.dropna(subset=['Date/Time', 'Lat', 'Lon'])
    df['Hour'] = df['Date/Time'].dt.hour
    df['DayOfWeek'] = df['Date/Time'].dt.day_name()
    df['Date'] = df['Date/Time'].dt.date
    return df

if uploaded_file:
    max_rows = 100_000  # you can adjust this as needed
    st.info(f"Processing with a maximum of {max_rows:,} rows to ensure smooth performance.")

    df = load_data(uploaded_file, sample_size=max_rows)

    st.success(f"Loaded {len(df):,} rows for analysis.")
    st.subheader("📌 Raw Data Sample")
    st.dataframe(df.head())


    # --- Data Prep ---
    df['Date/Time'] = pd.to_datetime(df['Date/Time'])
    df['Hour'] = df['Date/Time'].dt.hour
    df['DayOfWeek'] = df['Date/Time'].dt.day_name()
    df['Date'] = df['Date/Time'].dt.date

    st.subheader("📌 Raw Data")
    st.dataframe(df.head())

    # --- Pickup Heatmap ---
    st.subheader("🌡️ Pickup Heatmap")
    heat_map = folium.Map(location=[df['Lat'].mean(), df['Lon'].mean()], zoom_start=12)
    heat_data = df[['Lat', 'Lon']].dropna().values.tolist()
    HeatMap(heat_data).add_to(heat_map)
    st_folium(heat_map, width=700)

    # --- Pickup Clustering ---
    st.subheader("📍 Demand Clustering + Real-Time Prediction")
    k = st.slider("Number of clusters", 2, 10, 5)
    kmeans = KMeans(n_clusters=k, random_state=0).fit(df[['Lat', 'Lon']].dropna())
    df['Cluster'] = kmeans.labels_
    df_map = df.rename(columns={'Lat': 'lat', 'Lon': 'lon'})
    st.map(df_map[['lat', 'lon']])


    # Real-Time Prediction Input
st.subheader("🔮 Real-Time Pickup Zone Prediction")
input_lat = st.number_input("Enter Latitude", format="%.6f")
input_lon = st.number_input("Enter Longitude", format="%.6f")
if input_lat and input_lon:
    predicted_cluster = kmeans.predict([[input_lat, input_lon]])[0]
    st.success(f"Predicted demand zone: Cluster #{predicted_cluster}")

   # --- Route Optimization ---
st.subheader("🚗 Route Optimization (OpenRouteService)")
start_lat = st.number_input("Start Latitude", value=40.7128, format="%.6f", key="start_lat")
start_lon = st.number_input("Start Longitude", value=-74.0060, format="%.6f", key="start_lon")
end_lat = st.number_input("End Latitude", value=40.730610, format="%.6f", key="end_lat")
end_lon = st.number_input("End Longitude", value=-73.935242, format="%.6f", key="end_lon")

def is_valid_coord(lat, lon):
    return -90 <= lat <= 90 and -180 <= lon <= 180

# Initialize route state
if "route_displayed" not in st.session_state:
    st.session_state.route_displayed = False
    st.session_state.route_data = None

if st.button("Generate Route", key="generate_route"):
    if is_valid_coord(start_lat, start_lon) and is_valid_coord(end_lat, end_lon):
        coords = [[start_lon, start_lat], [end_lon, end_lat]]
        try:
            route = client.directions(coords)
            st.session_state.route_displayed = True
            st.session_state.route_data = route
        except ApiError as e:
            st.error(f"API Error: {e}")
            st.session_state.route_displayed = False
    else:
        st.warning("Please enter valid latitude and longitude values.")
        st.session_state.route_displayed = False

# Display route if it was generated
if st.session_state.route_displayed and st.session_state.route_data:
    route = st.session_state.route_data
    distance_km = round(route['routes'][0]['summary']['distance'] / 1000, 2)
    duration_min = round(route['routes'][0]['summary']['duration'] / 60, 2)
    st.success(f"Optimized Distance: {distance_km} km | Estimated Time: {duration_min} mins")

    m = folium.Map(location=[start_lat, start_lon], zoom_start=13)
    folium.Marker([start_lat, start_lon], tooltip="Start").add_to(m)
    folium.Marker([end_lat, end_lon], tooltip="End").add_to(m)
    decoded = convert.decode_polyline(route['routes'][0]['geometry'])
    folium.PolyLine(locations=[(c[1], c[0]) for c in decoded['coordinates']],
                    color="blue", weight=5).add_to(m)
    st_folium(m, width=700)


# --- Weather Overlay ---
st.subheader("🌦️ Current Weather at Pickup")
if input_lat and input_lon:
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={input_lat}&lon={input_lon}&appid={OWM_API_KEY}&units=metric"
    response = requests.get(weather_url).json()
    if response.get('main'):
        temp = response['main']['temp']
        desc = response['weather'][0]['description'].capitalize()
        st.info(f"Current weather: {temp}°C, {desc}")
    else:
        st.warning("Could not fetch weather data.")
