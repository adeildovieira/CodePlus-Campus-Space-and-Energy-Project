#!/usr/bin/env python
# coding: utf-8

# In[12]:


import pandas as pd
import folium
import branca.colormap as cm
import math

def create_heatmap(DAY_FILTER, TIME_FILTER):
     
    geojson_file = "/app/bostock1_floorplan.geojson"
     
    ap_dict = {
        "1-bostock-128-ap3802i-rc-1": (36.00303114914303, -78.93810780073801),
        "2-bostock-127-ap3802i-rc-1": (36.00309325474402, -78.93823819435035),
        "3-bostock-124-ap3802i-hc-1": (36.0031312, -78.9383622),
        "4-bostock-140-ap3802i-rc-1": (36.0029811, -78.9381882),
        "5-bostock-128-ap3802i-hc-1": (36.0030213, -78.9381965),
        "6-bostock-140-ap3802i-rc-2": (36.0029991121061, -78.93828896030848),
        "7-bostock-132-ap3802i-hc-1": (36.0030733, -78.9384175),
        "8-bostock-122-ap3802i-rc-1": (36.00313432364271, -78.938492805155),
        "9-bostock-104-ap3802i-rc-1": (36.00291234871183, -78.93817887927578),
        "10-bostock-142-ap3802i-hc-1": (36.0029354, -78.9383950),
        "11-bostock-133-ap3802i-hc-1": (36.0029788, -78.9384175),
        "12-bostock-122-ap3802i-rc-2": (36.003055976799885, -78.93854903821627),
        "13-bostock-120-ap3802i-rc-1": (36.0028238, -78.9383595),
        "14-bostock-127-ap3802i-rc-2": (36.00287274597517, -78.9384467252845),
        "15-bostock-121-ap3802i-hc-1": (36.0029202, -78.9385176),
        "16-bostock-121-ap3802i-rc-1": (36.0029600, -78.9386146),
    }
     
    df = pd.read_csv('/csv/june11_june17.csv')
     
    df['_time'] = pd.to_datetime(df['_time']).dt.tz_localize(None)
    df = df.sort_values(by='_time')
     
    # Convert input to datetime
    try:
        user_date = pd.to_datetime(DAY_FILTER)
        user_time = pd.to_datetime(TIME_FILTER).time()
    except ValueError:
        print("Invalid date or time format. Please use 'YYYY-MM-DD' for date and 'HH:MM' for time.")
     
    # Calculate the time range
    start_time = pd.Timestamp.combine(user_date, user_time) - pd.Timedelta(minutes=20)
    end_time = pd.Timestamp.combine(user_date, user_time) + pd.Timedelta(minutes=20)
     
    # Filter DataFrame for entries within the time range
    filtered_df_datetime = df[(df['_time'] >= start_time) & (df['_time'] <= end_time)]
     
    # Count the number of entries for each AP
    ap_counts = filtered_df_datetime['name'].value_counts()
     
    # Create the map
    m = folium.Map(location=[36.0029354, -78.9383950], zoom_start=20)
     
    # Add the GeoJSON data to the map
    folium.GeoJson(
        geojson_file,
        name='geojson',
    ).add_to(m)
     
    # Determine the maximum count for scaling
    max_count = max(ap_counts.max(), 1)
    max_count = max_count if max_count > 0 else 1
     
    # Create a color map
    index = [0, max_count]
    colormap = cm.LinearColormap(colors=['yellow', 'red'], vmin=0, vmax=max_count)
     
    # Add circles for each AP with a gradient color
    for point_id, coords in ap_dict.items():
        ap_name = '-'.join(point_id.split('-')[1:])
        filtered_point_id = filtered_df_datetime[filtered_df_datetime['name'] == ap_name]
        count = len(filtered_point_id)
        color = colormap(count)
     
        unique_users = filtered_point_id['user'].nunique()
        # Create a larger popup with max_width adjustment
        popup_text = (
            f'AP ID: {point_id}<br>'
            f'Total entries: {count}<br>'
            f'Model Prediction: {math.floor(count * 0.029460424110543018 + 1.7222676937891244) - 1}<br>'
            f'Total unique users: {unique_users}<br>'
            f'Model Prediction: {math.floor(unique_users * 0.7182956186807894 + 1.7222676937891244) - 1}'
        )
     
        folium.Circle(
            location=coords,
            radius=5,
            color=None,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_text, max_width=700),  # Adjust max_width as needed
        ).add_to(m)
     
    # Add colormap legend
    colormap.caption = 'Number of Entries'
    colormap.add_to(m)
     
     
    total_entries = len(filtered_df_datetime)
    linear_reg_prediction_total = total_entries * 0.029460424110543018 + 1.9873392060076185
    # Display the results
    print("\nTotal entries in the 40-minute window:", total_entries)
    print("Linear Regression Prediction based on total entries:", math.floor(linear_reg_prediction_total) - 1)
    unique_users = filtered_df_datetime['user'].nunique()
    linear_reg_prediction_user = unique_users * 0.7182956186807894 + 1.7222676937891244
    # Display the results
    print("Total unique user column in 40 minute window:", unique_users)
    print("Linear Regression Prediction based on total users:", math.floor(linear_reg_prediction_user) - 1) 
     
    # Save the map to an HTML file
    heatmap_filename = f"heatmap_{DAY_FILTER}_{TIME_FILTER}.html"
    m.save(heatmap_filename)

    return heatmap_filename
