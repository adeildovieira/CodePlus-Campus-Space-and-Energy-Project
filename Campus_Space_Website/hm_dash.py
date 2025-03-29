import pandas as pd
import folium
import branca.colormap as cm
import math
import ipywidgets as widgets
from IPython.display import display, clear_output
from datetime import datetime

# Widgets for user input
date_picker = widgets.DatePicker(description='Select Date', value=datetime(2024, 6, 11))
time_picker = widgets.TimePicker(description='Select Time', value=datetime.strptime('10:00', '%H:%M').time())
generate_button = widgets.Button(description='Generate Graph', button_style='success')
generate_button.style.button_color = '#00539B'

output = widgets.Output()

def display_hm_options():
    generate_button.on_click(on_generate_button_clicked)
    display(date_picker, time_picker, generate_button, output)

def display_heatmap(selected_date, selected_time):
    DAY_FILTER = selected_date.strftime('%Y-%m-%d')
    TIME_FILTER = selected_time.strftime('%H:%M')

    geojson_file = "./resources/bostock1_floorplan.geojson"

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

    df = pd.read_csv('./resources/june11_july3_bostock.csv')
    df['_time'] = pd.to_datetime(df['_time']).dt.tz_localize(None)
    df = df.sort_values(by='_time')

    # Convert input to datetime
    try:
        user_date = pd.to_datetime(DAY_FILTER)
        user_time = pd.to_datetime(TIME_FILTER).time()
    except ValueError:
        with output:
            print("Invalid date or time format. Please use 'YYYY-MM-DD' for date and 'HH:MM' for time.")
        return
    
    if user_date < pd.to_datetime('2024-06-11') or user_date > pd.to_datetime('2024-07-03'):
        with output:
            print("Error: Date is outside the allowed range of available data. Please select a date between June 11 and July 3.")
        return
    
    # Calculate the time range
    start_time = pd.Timestamp.combine(user_date, user_time) - pd.Timedelta(minutes=20)
    end_time = pd.Timestamp.combine(user_date, user_time) + pd.Timedelta(minutes=20)

    # Filter DataFrame for entries within the time range
    filtered_df_datetime = df[(df['_time'] >= start_time) & (df['_time'] <= end_time)]

    # Count the number of entries for each AP
    ap_counts = filtered_df_datetime['name'].value_counts()

    # Create the map
    m = folium.Map(location=[36.0029354, -78.9383950], zoom_start=20)

    # Define a style function for the GeoJSON data
    def style_function(feature):
        return {
            'fillColor': 'none',
            'color': 'black',
            'weight': 3
        }

    # Add the GeoJSON data to the map with the custom style
    folium.GeoJson(geojson_file, name='geojson', style_function=style_function).add_to(m)

    # Determine the maximum count for scaling
    if ap_counts.empty:
        max_count = 1  # Avoid division by zero or color map errors
    else:
        max_count = max(ap_counts.max(), 1)
    colormap = cm.LinearColormap(colors=['yellow', 'red'], index=[0, max_count], vmin=0, vmax=max_count)

    # Add circles for each AP with a gradient color
    for point_id, coords in ap_dict.items():
        ap_name = '-'.join(point_id.split('-')[1:])
        filtered_point_id = filtered_df_datetime[filtered_df_datetime['name'] == ap_name]
        count = len(filtered_point_id)
        color = colormap(count)

        unique_users = filtered_point_id['user'].nunique()
        popup_text = (
            f'AP ID: {point_id}<br>'
            f'Total entries: {count}<br>'
            f'Model Prediction: {math.floor(count * 0.0347073234431158 + 0.44464825912121597)}<br>'
            f'Total unique users: {unique_users}<br>'
            f'Model Prediction: {math.floor(unique_users * 0.8437650730600083)}'
        )

        folium.Circle(
            location=coords,
            radius=5,
            color=None,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            popup=folium.Popup(popup_text, max_width=700),
        ).add_to(m)

    # Add colormap legend
    colormap.caption = 'Number of Entries'
    colormap.add_to(m)

    total_entries = len(filtered_df_datetime)
    linear_reg_prediction_total = total_entries * 0.0347073234431158 + 0.44464825912121597

    with output:
        # Display the results
        print("\nTotal entries in the 40-minute window:", total_entries)
        print("Linear Regression Prediction based on total entries:", math.floor(linear_reg_prediction_total))

    unique_users = filtered_df_datetime['user'].nunique()
    linear_reg_prediction_user = unique_users * 0.8437650730600083

    with output:
        # Display the results
        print("Total unique user column in 40 minute window:", unique_users)
        print("Linear Regression Prediction based on total users:", math.floor(linear_reg_prediction_user))

    with output:
        # Display the map directly
        display(m)

def on_generate_button_clicked(b):
    with output:
        output.clear_output()
        selected_date = date_picker.value
        selected_time = time_picker.value
        if selected_date and selected_time:
            display_heatmap(selected_date, selected_time)
        else:
            print("Please select both a date and a time.")

# generate_button.on_click(on_generate_button_clicked)
# display_options()
