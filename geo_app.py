import streamlit as st
import pandas as pd
import pydeck as pdk

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

    # Display data if needed
    if st.checkbox("Show Data Table"):
        st.write(data)

    # Slider for radius with 0.5 km steps
    radius_km = st.slider("Select Radius (in km)", min_value=0.5, max_value=10.0, value=2.0, step=0.5)
    radius_meters = radius_km * 1000  # Convert to meters

    # Combine store name and Avg Sales for display
    if 'Avg Sales' in data.columns:
        data['DISPLAY_TEXT'] = data['STORE'] + "\nAvg Sales: " + data['Avg Sales'].fillna("N/A").astype(str)
    else:
        st.warning("The 'Avg Sales' column is missing from the dataset. Defaulting to STORE names only.")
        data['DISPLAY_TEXT'] = data['STORE']

    # Scatterplot layer for store locations
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data,
        get_position=["LONGITUDE", "LATITUDE"],
        get_radius=500,
        get_fill_color=[255, 0, 0, 200],
        pickable=True,
    )

    # Text layer for store names and Avg Sales
    text_layer = pdk.Layer(
        "TextLayer",
        data,
        get_position=["LONGITUDE", "LATITUDE"],
        get_text="DISPLAY_TEXT",  # Combined store name and Avg Sales
        get_color=[255, 255, 255],
        get_size=18,  # Adjusted for visibility
        get_alignment_baseline="center",
    )

    # Center view on the data points
    view_state = pdk.ViewState(
        latitude=data['LATITUDE'].mean(),
        longitude=data['LONGITUDE'].mean(),
        zoom=6,
    )

    # Render map with layers
    st.pydeck_chart(pdk.Deck(layers=[scatter_layer, text_layer], initial_view_state=view_state))
else:
    st.warning("Please upload an Excel file to display the map.")
