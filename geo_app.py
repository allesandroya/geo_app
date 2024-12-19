import streamlit as st
import pandas as pd
import pydeck as pdk
from geopy.distance import geodesic  # For calculating distances

st.title("Store Location Map - Indonesia")

# File uploader
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file is not None:
    # Load data from uploaded file
    data = pd.read_excel(uploaded_file)
    
    # Ensure LATITUDE and LONGITUDE are numeric
    data['LATITUDE'] = pd.to_numeric(data['LATITUDE'], errors='coerce')
    data['LONGITUDE'] = pd.to_numeric(data['LONGITUDE'], errors='coerce')

    # Drop rows with missing or invalid coordinates
    data = data.dropna(subset=['LATITUDE', 'LONGITUDE'])

    st.title("Mie Gacoan Store Map - Indonesia")

    # Display data if needed
    if st.checkbox("Show Data Table"):
        st.write(data)

    # Slider for radius with 0.5 km steps
    radius_km = st.slider("Select Radius (in km)", min_value=0.5, max_value=10.0, value=2.0, step=0.5)
    radius_meters = radius_km * 1000  # Convert to meters

    # Define layers for points, radius circles, and text labels
    # Scatterplot layer for store locations
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data,
        get_position=["LONGITUDE", "LATITUDE"],
        get_radius=500,
        get_fill_color=[255, 0, 0, 140],
        pickable=True
    )

    # Circle layer for dynamic radius circles around stores
    circle_layer = pdk.Layer(
        "ScatterplotLayer",
        data,
        get_position=["LONGITUDE", "LATITUDE"],
        get_radius=radius_meters,
        get_fill_color=[0, 255, 0, 80],
        stroked=True,
    )

    # Text layer for store names
    text_layer = pdk.Layer(
        "TextLayer",
        data,
        get_position=["LONGITUDE", "LATITUDE"],
        get_text="STORE",  # Column name for store names
        get_color=[255, 255, 255],  # White color for text
        get_size=16,
        get_alignment_baseline="'bottom'"
    )

    # Center view on the data points
    view_state = pdk.ViewState(
        latitude=data['LATITUDE'].mean(),
        longitude=data['LONGITUDE'].mean(),
        zoom=6,
    )

    # Render map with layers
    st.pydeck_chart(pdk.Deck(layers=[scatter_layer, circle_layer, text_layer], initial_view_state=view_state))

    # Calculate distances between stores in the same city
    st.subheader("Distances Between Stores in the Same City")

    # Filter the data by each unique city and calculate distances between stores within the same city
    distance_data = []

    for city in data['CITY'].unique():
        city_stores = data[data['CITY'] == city]
        
        # Calculate pairwise distances between stores in the same city
        for i, store1 in city_stores.iterrows():
            for j, store2 in city_stores.iterrows():
                if i != j:  # Include all pairs, avoid self-pairs
                    loc1 = (store1['LATITUDE'], store1['LONGITUDE'])
                    loc2 = (store2['LATITUDE'], store2['LONGITUDE'])
                    distance_km = geodesic(loc1, loc2).kilometers
                    
                    # Append the information to distance_data
                    distance_data.append({
                        "City": city,
                        "Store 1": store1['STORE'],
                        "Store 2": store2['STORE'],
                        "Distance (km)": round(distance_km, 2)
                    })

    # Convert distance data to DataFrame and display it
    distance_df = pd.DataFrame(distance_data)
    st.write(distance_df)
else:
    st.warning("Please upload an Excel file to display the map.")
