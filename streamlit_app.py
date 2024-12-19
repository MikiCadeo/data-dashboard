import streamlit as st
import pandas as pd
from pathlib import Path
import numpy as np
import pydeck as pdk

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Cadeo dashboard',
    page_icon='assets/cadeo-logo-compact.svg'
)

# Sidebar
with st.sidebar:
    st.title('Cadeo data report')
    st.logo("assets/cadeo-logo.svg")
    selected_env = st.selectbox('Environment', ["Development", "Production"], 0)

# -----------------------------------------------------------------------------
# Connect to database and get required data

# Initialize connection.
conn = st.connection("postgresql", type="sql")

# Perform query.
orders_df = conn.query("SELECT * FROM orders_order;", ttl="10m")
users_df = conn.query("SELECT * FROM users_user;", ttl="10m")

# Print results.
# for order in fulfilmentorders_df.itertuples():
#    st.write(f"{order.destination_city}")

# -----------------------------------------------------------------------------
# Helpers

def get_orders_by_status(status_field, status):
    return orders_df[orders_df[status_field] == status]

# -----------------------------------------------------------------------------
# Draw the actual page

#######################

# Set the title that appears at the top of the page.
'''
# Cadeo dashboard
'''

# Add some spacing
''

# Key statistics
accepted_orders, orders, users = st.columns(3, border=True)

accepted_orders.metric("Accepted orders", len(get_orders_by_status('sender_status', 'accepted')))
orders.metric("Total orders", len(orders_df))
users.metric("Number of users", len(users_df))

earnings, pending_earnings, donations = st.columns(3, border=True)

earnings.metric("Earnings", '€' + str(round(sum(get_orders_by_status('sender_status', 'accepted')['total_order_price']), 2)))
pending_earnings.metric("Pending earnings", '€' + str(round(sum(get_orders_by_status('sender_status', 'created')['total_order_price']) + sum(get_orders_by_status('sender_status', 'shared')['total_order_price']), 2)))
donations.metric("Donations", '€' + str(0))

with st.expander("Settings"):
    # Column selection
    cols = st.multiselect('Columns to show:', orders_df.columns, default=['full_order_number', 'sender_status', 'total_order_price', 'sending_method', 'sender_name'])

    # Price range slider
    min_order_price = orders_df['total_order_price'].min()
    max_order_price = orders_df['total_order_price'].max()

    from_price, to_price = st.slider(
        'Filter orders by price',
        min_value=min_order_price,
        max_value=max_order_price,
        value=(min_order_price, max_order_price),
        format='€%.2f')

# Filter and display DataFrame
filtered_orders_df = orders_df[
    (orders_df['total_order_price'] >= from_price) & 
    (orders_df['total_order_price'] <= to_price)
][cols]

st.write(filtered_orders_df)
