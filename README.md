# 🗺️ Uber Trip Analysis – Geospatial Clustering, Route Optimization & Weather Overlay

This Streamlit app allows you to explore Uber trip data using geospatial visualizations, identify demand hotspots using clustering, optimize routes between pickup and drop-off points, and display real-time weather conditions.

## 🚀 Features

- 📦 Upload and process large Uber datasets
- 📊 Analyze trips by time (hour, day)
- 🌡️ Visualize pickup heatmaps with Folium
- 📍 Cluster high-demand pickup zones using KMeans
- 🔮 Predict real-time pickup zones based on latitude/longitude input
- 🚗 Optimize travel routes using OpenRouteService API
- 🌦️ Show live weather at pickup point via OpenWeatherMap API

## 🧰 Technologies Used

- Python
- Streamlit
- Pandas / NumPy
- Folium & HeatMap
- Scikit-learn (KMeans)
- Plotly (Charts)
- OpenRouteService API
- OpenWeatherMap API

## 🗃️ Dataset

Use monthly files from the [Uber NYC Kaggle Dataset](https://www.kaggle.com/datasets/fivethirtyeight/uber-pickups-in-new-york-city). Each file should contain:
- `Date/Time`
- `Lat`
- `Lon`

## 📦 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/uber-trip-analysis.git
cd uber-trip-analysis
```

### 2. Create Virtual Environment (Optional)
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Requirements
```bash
pip install -r requirements.txt
```

### 4. Add Your API Keys
In the Python file, add your API keys:
```python
ORS_API_KEY = "your_openrouteservice_api_key"
OWM_API_KEY = "your_openweathermap_api_key"
```

### 5. Run the App
```bash
streamlit run uber_trip_analysis.py
```

## 📌 Notes

- Large datasets are automatically sampled to ensure smooth performance.
- Route optimization requires valid coordinates and internet access.
- Weather API requires OpenWeatherMap free account.