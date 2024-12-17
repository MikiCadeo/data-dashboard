import streamlit as st
import pandas as pd
from pathlib import Path
import numpy as np
import pydeck as pdk

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Cadeo dashboard',
    page_icon='https://www.cadeo.nl/wp-content/uploads/2023/11/LogoCadeo_logo_Ocean.svg', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.


@st.cache_data
def get_city_data():
    DATA_FILENAME = Path(__file__).parent/'data/cities.csv'
    cities_df = pd.read_csv(DATA_FILENAME)

    return cities_df



@st.cache_data
def get_order_data():
    DATA_FILENAME = Path(__file__).parent/'data/orders.csv'
    raw_orders_df = pd.read_csv(DATA_FILENAME)

    orders_df = raw_orders_df.melt(
        ['price', 'did_swap', 'method', 'last_update_at', 'city', 'name']
    )
    
    return orders_df


def add_coordinates(main_df, city_coords_df):
    # Create a list of unique cities from the coordinates DataFrame
    cities = city_coords_df['city'].tolist()
    
    # Randomly select cities for each row in the main DataFrame
    random_cities = np.random.choice(cities, size=len(main_df))
    
    # Create a dictionary mapping cities to their coordinates
    city_coords_dict = dict(zip(city_coords_df['city'], 
                                zip(city_coords_df['lat'], city_coords_df['lng'])))
    
    # Add random city and its coordinates
    main_df['city'] = random_cities
    main_df[['latitude', 'longitude']] = main_df['city'].apply(
        lambda x: pd.Series(city_coords_dict[x])
    )
    
    return main_df

cities_df = get_city_data()
orders_df = add_coordinates(get_order_data(), cities_df)

st.write(orders_df.drop(columns=['variable', 'value']))

# -----------------------------------------------------------------------------
# Draw the actual page

#######################
# Sidebar
with st.sidebar:
    st.title('Cadeo data report')
    
    selected_env = st.selectbox('Environment', ["Development", "Production"], 1)

# Set the title that appears at the top of the page.
'''
# Cadeo dashboard

Description to be updated.
'''

# Add some spacing
''
''

min_value = orders_df['price'].str.replace('$', '').astype(float).min()
max_value = orders_df['price'].str.replace('$', '').astype(float).max()

from_year, to_year = st.slider(
    'Filter orders by price',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])

cities = sorted(orders_df['city'].unique())

if not len(cities):
    st.warning("Select at least one city")

selected_cities = st.multiselect(
    'Which city would you like to view?',
    cities,
    ["Amsterdam", "Eindhoven", "Haarlem", "Arnhem", "Leiden"])

''
''
''

st.pydeck_chart(
    pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=52.3728,
            longitude=4.8936,
            zoom=6,
            pitch=36,
        ),
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=orders_df,
                get_position="[longitude, latitude]",
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
            pdk.Layer(
                "ScatterplotLayer",
                data=orders_df,
                get_position="[longitude, latitude]",
                get_color="[200, 30, 0, 160]",
                get_radius=200,
            ),
        ],
    )
)